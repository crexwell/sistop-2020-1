#include <dirent.h>
#include <stdio.h>


int int main(void) {

  int select;
  printf("Seleccione alguna opcion:\n");
  printf("1.-Lista de contenidos\n");
  printf("2.-Copiar uno de los archivos FiUnamFS -> Sistema\n");
  printf("3.-Copiar uno de los archivos Sistema -> FiUnamFS\n");
  printf("4.-Eliminar un archivo del FiUnamFS\n");
  printf("5.-Desfragmentante\n");

  scanf("%d", &select);
  switch (select) {
    case 1:listDir()
    case 2:copFile()
    case 3:
    case 4:
    case 5:
    default:
      printf("Opcion no valida\n", );
  }


  return 0;
}

int listDir(void) {
  DIR *d;
  struct dirent *dir;//apuntador a la entrada del directorio
  d = opendir("."); //opendir nos regresa un apuntador del tipo DIR

  if (d == NULL){
    printf("Could not open current directory");
    return 0;

  }

  if (d) {
    while ((dir = readdir(d)) != NULL) {
      printf("%s\n", dir->d_name);
    }
    closedir(d);
  }
  return(0);
}

int copFile(int argn, char * argv[]){

    int src_fd, dst_fd, n, error;
    unsigned char buffer[4096];
    char * src_path, dst_path;

    if (argn != 3){
      printf("Wrong argument count.\n", );
      exit(1);
    }

    src_path = argv[1];
    dst_path = argv[2];

    scr_fd = open(src, O_RDONLY);
    dst_fd = open(dst_path, O_CREAT | O_WRONLY);

    while (1) {
      error = read(src_fd, buffer, 4096);
      if (error == -1){
        printf("Error reading file.\n", );
        exit(1)
      }
      n = error;

      if (n == 0) break;
      error = write(dst_fd, buffer, n);
      if (error == -1){
        printf("Error writing to file\n", );
      }
    }
    close(src_fd);
    close(dst_fd);
}
