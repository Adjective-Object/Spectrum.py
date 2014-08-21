#ifndef SPECTRUM_PLAYER_INCLUDED
#define SPECTRUM_PLAYER_INCLUDED

typedef struct Song{
    Player player,
    Metadater metadata
} Song;

song load

class Player{

    //contents of the current frame (on the heap)
    int *framedata;

    int _currentframe;
    int _totalframes;

public:
    void open(); //opens the ffmpeg subprocess
    void next_frame(); //steps to the next frame

    int *get_data()     {return framedata};

    int currentframe()  {return _currentframe};
    int totalframes()   {return _totalframes};
};


// Handles all class metadata. Just a bunch of fancy getters and setters
// All of the string data is on the heap
class Metadater{

    char *_title;
    char *_artist;
    char *_album;
    char *_album_artist;
    char *_composer;

    int _year;
    int _trackno;
    int _numtracks;

    char *_genre;
    char *_originalartist

public:
    //song metadata
    char *title()           {return _title;}
    char *artist()          {return _artist;}
    char *album()           {return _album;}
    char *album_artist()    {return _album_artist;}
    char *composer()        {return _composer;}

    int year()              {return _year};
    int trackno()           {return _trackno};
    int numtracks()         {return _numtracks;}

    char *genre()           {return _genre};
    char *originalartist()  {return _originalartist;}
};

#endif