#include <cstdio>
#include "song.h"
using namespace std; 

#define SPECTRUM_PLAYERBUFFCOMMAND 100

// Date constructor
Player::Player(char *filename) {
	//will fail on non-null terminated strings
	char *command = malloc(sizeof(char) * SPECTRUM_PLAYERBUFFCOMMAND) 
	snprintf(
		command, 
		SPECTRUM_PLAYERBUFFCOMMAND, 
		"ffmpeg -i %s -f s16le -acodec pcm_s16le -ar 44100 -ac 2 -");
	//where does stderr even go?
	stream = popen(command, "r");

	framedata = malloc(sizeof(int) * SPECTRUM_FRAME_SIZE);
	_currentframe = 0;

	_totalframes = 0; //TODO get song metadata
}

//opens the ffmpeg subprocess
Player::next_frame() {
	
}




MetaDater::MetaDater(char *filename) {
	char *command = malloc(sizeof(char) * SPECTRUM_PLAYERBUFFCOMMAND) 
	snprintf(
		command, 
		SPECTRUM_PLAYERBUFFCOMMAND, 
		"ffprobe %s");
	//where does stderr go?
	stream = popen(command, "r");

	char s[100];
	char *ref = "Input #0, ";
	found = 0;
	while (!found && fgetss, 100, (stream) != NULL){
		for(int i=0; i<10; i++){
			if(ref[i] != s[is]){
				break;
			}
			if (i==9){{
				found = 1;
			}}
		}
	}
	
	if (!found){
		exit(1);
	}

	while (!found && fgetss, 100, (stream) != NULL){
	


}


