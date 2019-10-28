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
    case 1:listDir();
    case 2:copFile();
    case 3:copFile();
    //case 4:rmFile(1,[1]);
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

int copFile(){

      FILE *fptr1, *fptr2;
      char filename[100], c;

      printf("Enter the filename to open for reading \n");
      scanf("%s", filename);

      // Esta parte es para abrir el archivo
      fptr1 = fopen(filename, "r");
      if (fptr1 == NULL)
      {
          printf("Cannot open file %s \n", filename);
          exit(0);
      }

      printf("Enter the filename to open for writing \n");
      scanf("%s", filename);


      fptr2 = fopen(filename, "w");
      if (fptr2 == NULL)
      {
          printf("Cannot open file %s \n", filename);
          exit(0);
      }

      // leemos el contenido del archivo
      c = fgetc(fptr1);
      while (c != EOF)
      {
          fputc(c, fptr2);
          c = fgetc(fptr1);
      }

      printf("\nContents copied to %s", filename);

      fclose(fptr1);
      fclose(fptr2);
      return 0;
}
/*void rmFile(int argc, char* argv[]){
if(argc!=2 || argv[1]=="--help")
  {
    printf("\nusage: rm FileTodelete\n");
  }
int status;
status=remove(argv[1]);
if(status==0)
  {
    printf("successfull\n");
  }
else
   {
    printf("Unsuccessfull\n");
   }
}*/
