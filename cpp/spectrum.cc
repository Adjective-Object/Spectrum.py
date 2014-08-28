#include <stdio.h>
#include <unistd.h>
#include "json/json.h"
#include "song.h"
using namespace std;

int main (int argc, char *argv []) {
	//usage is "spectrum soundfile cfgfile"
	if (argc != 2) {
		 printf("args format is spectrum <flags> [soundfile] [cfgfile]\n");
		 printf("flags are:\n");
		 printf("\t-p: preview in window without rendering video");
		 printf("\t-h: print verbose help text");
		 return 1;
	}

	int cur = 0;
	while (cur < argc && *argv[cur] == '-'){
		printf("!\n");
	}

	char *soundfilename = argv[0];
	char *cfgfilename = argv[1];



	return 0;
}