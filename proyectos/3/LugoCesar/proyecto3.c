#include <dirent.h>
#include <stdio.h>


int int main(void) {

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
