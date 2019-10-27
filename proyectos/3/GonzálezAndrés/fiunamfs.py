from mmap import mmap
import re
import math
from datetime import datetime #, strptime

MSGERR_NO_MONTADO = 'Error: No se ha montado el sistema de archivos'
MSGERR_ARCH_NO_ENC = 'Error: No se encuentra el archivo de origen'
MSGADV_FS_YA_MONT = 'Advertencia: El sistema de archivos ya está montado'
MSGERR_FN_INVALIDO = 'Error: el tamaño del nombre del archivo debe ser de 1 a 15 caracteres y estos deben ser US-ASCII imprimibles'

PATRON_FN_VALIDO = re.compile(r'[\x21-\x7F][\x20-\x7F]{,14}') # Patrón para verificar si los archivos tienen caracteres válidos

def now():
    return datetime.now().strftime('%Y%m%d%H%M%S')#.encode('ascii')

class FIUNAMFS(object):
    def __init__(self, ruta_img):
        self.ruta_img = ruta_img
        self.__listaEntDir = []
        self.montado = False

    def montar(self):
        if self.montado:   
            print(MSGADV_FS_YA_MONT)
            return True 
                    
        try:
            self.__f = open(self.ruta_img, 'r+b')
        except OSError as oserr:
            print('OSError: %s' % oserr)
        except IOError as ioerr:
            print('IOError %s' % ioerr)
        else:
            self.__mmfs = mmap(self.__f.fileno(), 0)
            nombrefs = self.__mmfs[0:8].decode('ascii')
            # print(nombrefs)
            if nombrefs == 'FiUnamFS':
                self.montado = True

                self.nombre = nombrefs
                # print('Nombre del sistema de archivos: %s' % self.nombre)

                self.version = self.__mmfs[10:13].decode('ascii').strip()
                # print('Versión: %s' % self.version)
                
                self.etiqueta = self.__mmfs[20:35].decode('ascii').strip()
                # print('Etiqueta del volumen: %s' % self.etiqueta)
                
                self.tam_cluster = int(self.__mmfs[40:45].decode('ascii').strip())
                # print('Tamaño del cluster: %i bytes' % self.tam_cluster)

                self.tam_dir = int(self.__mmfs[47:49].decode('ascii').strip())
                # print('Tamaño del directorio: %i clusters' % self.tam_dir)

                self.tam_unidad = int(self.__mmfs[52:60].decode('ascii').strip())
                # print('Tamaño de la unidad: %i clusters' % self.tam_unidad)

                self.tam_entradadir = 64

                self.scandir()

                print('Sistema de archivos montado')
                return True
            else:
                print('No se reconoce el sistema de archivos')
                self.__mmfs.close()
                self.montado = False
                return False

    def desmontar(self):
        if self.montado:
            self.__mmfs.close()
            self.__f.close()
            self.montado = False
            print('Sistema de archivos desmontado')
        else:
            print(MSGERR_NO_MONTADO)

    def listdir(self):
        ldir = []
        if self.montado:
            for entradaDir in self.__listaEntDir:
                ldir.append(entradaDir.nombre)
        else: 
            print(MSGERR_NO_MONTADO)
        return ldir
    
    def scandir(self):
        self.__listaEntDir = []
        if not self.montado:
            print(MSGERR_NO_MONTADO)
            return []
        
        inicio = self.tam_cluster
        fin = self.tam_cluster*self.tam_dir+self.tam_cluster
        paso = self.tam_entradadir
        for i in range(inicio,fin,paso):
            entdir = self.__mmfs[i:i+paso]
            nombre = entdir[0:15].decode('ascii').strip()
            # if nombre == 'README.org':                    
            #     print(len(('\0'*3+'24527').encode('ascii')), ('\0'*8+'24527').encode('ascii'))
            #     print(len(self.__mmfs[i+16:i+24]), self.__mmfs[i+16:i+24])
            #     self.__mmfs[i+16:i+24] = ('00029718').encode('ascii')
            #     self.__mmfs.flush()
            if nombre != 'Xx.xXx.xXx.xXx.':
                tam_archivo = int(entdir[16:24].decode('ascii').strip())
                cluster_inicial = int(entdir[25:30].decode('ascii').strip())
                f_creacion = entdir[31:45].decode('ascii')
                f_modif = entdir[46:60].decode('ascii')
                nuevaEntrada = EntradaDir(nombre, tam_archivo, cluster_inicial, f_creacion, f_modif)
                self.__listaEntDir.append(nuevaEntrada)            
        return self.__listaEntDir

    def descargar(self, origen = '', destino = ''):
        """Copiar un archivo de FIUNAMFS a nuestro sistema de archivos
        Atributos:
            origen -- nombre del archivo a copiar
            destino -- ruta y nombre del archivo de destino
        """
        if not self.montado:
            print(MSGERR_NO_MONTADO)
            return False

        resultado = list(filter( lambda entdir: entdir.nombre == origen, self.__listaEntDir)) # Buscamos el elemento que coincida
        if not resultado:
            print(MSGERR_ARCH_NO_ENC)
            return False
        
        entrDir = resultado.pop() # Obtenemos la entrada del directorio
        dir_inicio = entrDir.cluster_inicial * self.tam_cluster # dirección de inicio
        dir_fin = dir_inicio + entrDir.tam_archivo # dirección de fin
        bytes_archivo = self.__mmfs[dir_inicio:dir_fin] # bytes en bruto
        try:
            destino = origen if not destino else destino # Usar el mismo nombre que el del origen si no le dimos ninguno
            f = open(destino, 'w+b') # Abrimos el archivo en modo w+b
            f.write(bytes_archivo)
            f.close()
            print('Se escribió el archivo %s' % destino)
            return True
        except IOError as ioerr:
            print('IOError: %s' % ioerr)            
    
    def subir(self, origen, destino=''):
        if not self.montado:
            print(MSGERR_NO_MONTADO)
            return False

        try:
            f = open(origen, 'rb') # Abrimos el archivo en modo lectura
            bytes_archivo = f.read()
            tam_archivo = len(bytes_archivo)
            clusters_requeridos = math.ceil(tam_archivo / self.tam_cluster)
            print('Tamaño de "%s": %i bytes, %i clusters' % (origen, tam_archivo, clusters_requeridos))
            f.close()

            destino = destino.strip() # Le quitamos los caracteres en blanco al inicio y al final
            if not destino:
                destino = origen # Si no se nombre de archivo de destino, usamos el de origen

            if not re.fullmatch(PATRON_FN_VALIDO, destino): # Checamos si el nombre de destino cumple con el patrón
                print(MSGERR_FN_INVALIDO)
                print('Nombre ingresado: %s' % destino)
                return False

            resultado = list(filter( lambda entdir: entdir.nombre == destino, self.__listaEntDir)) # Buscamos el elemento que coincida
            if resultado:
                print('Ya existe un archivo con ese nombre en el directorio: %s' % destino)
                return False
            
            self.__listaEntDir = sorted(self.__listaEntDir, key=lambda ed: ed.cluster_inicial) # Ordenamos la lista de entradas con base en el cluster donde inician
            #print('Guardando: %s -> %s' % (origen, destino))
            for i, ed_actual in enumerate(self.__listaEntDir): # ed_actual : entrada del directorio actual
                try:
                    ed_sig = self.__listaEntDir[i+1] # ed_sig : entrada del directorio siguiente
                    delta_clusters = ed_sig.cluster_inicial - ed_actual.cluster_inicial # vemos cuántos clusters hay entre entrada de directorio y entrada de directorio
                    clusters_usados = math.ceil(ed_actual.tam_archivo / self.tam_cluster)
                    clusters_libres = delta_clusters - clusters_usados
                    print('Clusters libres entre "%s" y "%s": %i' % (ed_actual.nombre, ed_sig.nombre, clusters_libres))

                    if clusters_libres>=clusters_requeridos:
                        cluster_inicial = ed_actual.cluster_inicial+clusters_usados
                        print('Guardando "%s" en cluster %i' % (origen, cluster_inicial))
                        ed_nueva = EntradaDir(destino, tam_archivo, cluster_inicial, now(), now())
                        return self.agregarEntDir(ed_nueva, bytes_archivo)

                except IndexError:
                    print('Fin de la lista, guardar al final')
                    return True

        except IOError as ioerr:
            print('IOError: %s' % ioerr)
            return False
    
    def agregarEntDir(self, entDir, datos):
        if not self.montado:
            print(MSGERR_NO_MONTADO)
            return False
        
        inicio = self.tam_cluster
        fin = self.tam_cluster*self.tam_dir+self.tam_cluster
        paso = self.tam_entradadir
        for i in range(inicio,fin,paso):
            nombre_ant = self.__mmfs[i + 0 : i + 15].decode('ascii')
            if nombre_ant == 'Xx.xXx.xXx.xXx.': # Comparamos lo que hay en el nombre con la cadena de entrada de dir vacía
                
                self.__mmfs[i + 0 : i + 15] = ('%15s' % entDir.nombre).encode('ascii')
                self.__mmfs[i + 16 : i + 24] = ('%08s' % entDir.tam_archivo).encode('ascii')
                self.__mmfs[i + 25 : i + 30] = ('%05s' % entDir.cluster_inicial).encode('ascii')
                self.__mmfs[i + 31 : i + 45] = ('%14s' % entDir.f_creacion).encode('ascii')
                self.__mmfs[i + 46 : i + 60] = ('%14s' % entDir.f_modif).encode('ascii')

                dir_inicio_datos = entDir.cluster_inicial*self.tam_cluster
                tam_archivo = len(datos)

                # print('Tamaño mmap fs: ', len(self.__mmfs[dir_inicio_datos : dir_inicio_datos + tam_archivo]))
                # print('Tamaño a escribir: ', len(datos))
                
                self.__mmfs[dir_inicio_datos : dir_inicio_datos+tam_archivo]=datos
                
                self.__mmfs.flush()
                
                self.__listaEntDir.append(entDir) # Agregamos la entrada a la lista
                return True
    
    def format(self):
        pass


class EntradaDir(object):
    def __init__(self, nombre, tam_archivo, cluster_inicial, f_creacion = now(), f_modif = now()):
        self.nombre = nombre
        self.tam_archivo = tam_archivo
        self.cluster_inicial = cluster_inicial
        self.f_creacion = f_creacion
        self.f_modif = f_modif

    def __str__(self):
        return '%i %s %i bytes %s %s' % (self.tam_archivo, 
                                    self.nombre, 
                                    self.cluster_inicial, 
                                    self.f_creacion, 
                                    self.f_modif)
# Error de sistema no montado
# class NMError(Error):
#     def __init__(self, expression, message):
#         self.expression = expression
#         self.message = message