#include <cstdio>
#include "song.h"
using namespace std; 

#define PLAYERBUFFCOMMAND 100

// Date constructor
Player::Player(char *filename)
{
	//will fail on non-null terminated strings
	char *command = malloc(sizeof(char) * PLAYERBUFFCOMMAND) 
	snprintf(command, PLAYERBUFFCOMMAND, "ffmpeg -i %s -f s16le -ac 2 -");
	popen(command);
}


