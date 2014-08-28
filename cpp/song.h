#ifndef SPECTRUM_SONG_INCLUDED
#define SPECTRUM_SONG_INCLUDED

#define SPECTRUM_FRAME_SIZE 4096

class Player{

    //contents of the current frame (on the heap)
    int *framedata;

    int _currentframe;
    int _totalframes;

    FILE *stream;

public:
    void next_frame(); //steps to the next frame

    int *get_data()     {return framedata;}

    int currentframe()  {return _currentframe;}
    int totalframes()   {return _totalframes;}
};


// Handles all class metadata. Just a bunch of fancy getters and setters
// All of the string data is on the heap
class MetaDater{

    char *_title;
    char *_artist;
    char *_album;
    char *_album_artist;
    char *_composer;

    int _year;
    int _trackno;
    int _numtracks;

    char *_genre;
    char *_originalartist;

public:
    //song metadata
    char *title()           {return _title;}
    char *artist()          {return _artist;}
    char *album()           {return _album;}
    char *album_artist()    {return _album_artist;}
    char *composer()        {return _composer;}

    int year()              {return _year;}
    int trackno()           {return _trackno;}
    int numtracks()         {return _numtracks;}

    char *genre()           {return _genre;}
    char *originalartist()  {return _originalartist;}
};

typedef struct Song{
    Player *player;
    MetaDater *metadata;
} Song;

#endif