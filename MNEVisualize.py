import visualizer
import pygame
import time
import random
import getopt
import sys
import threading

#import player
#import spectrum

#list of values 0.0 to 1.0
def make_random_noise(resolution):
    return [random.random() *(resolution-i)/resolution 
            for i in range(resolution)]

def parseColor(string):
    s = string.replace("(","").replace(")","").replace(" ","").split(",")
    if len(s) == 3:
        return pygame.Color(int(s[0]), int(s[1]), int(s[2]))
    elif len(s) == 4:
        return pygame.Color(int(s[0]), int(s[1]), int(s[2]), int(s[3]))
    else:
        print "Improperly specified color argument. Defaulting to Black"
        return pygame.Color(0,0,0)


def get_boolean(s, cmd, argnum):
    if s=="true" or s=="t" or s=="1":
        return True
    elif s=="false" or s=="f" or s=="0":
        return False
    print "Improperly specified boolean argument %s in command %s"%(argnum, cmd)
    sys.exit(1)

def get_float(s, cmd, argnum):
    try:
        return int(s)
    except Exception:
        print "Improperly specified float argument %s in command %s"%(argnum, cmd)
        sys.exit(1)

def get_location(s, cmd, argnam):
    if(s.lower() == "bottom"):
        return visualizer.BOTTOM
    elif(s.lower() == "middle"):
        return visualizer.MIDDLE
    elif(s.lower() == "top"):
        return visualizer.TOP
    elif(s.lower() == "left"):
        return visualizer.LEFT
    elif(s.lower() == "right"):
        return visualizer.RIGHT

    elif(s.lower() == "first-third" or s.lower() == "first_third" or
            s == "1/3"):
        return visualizer.FIRST_THIRD
    elif(s.lower() == "firstthird" or s.lower() == "second_third" or
            s == "2/3"):
        return visualizer.SECOND_THIRD

    elif(s.lower() == "first-quarter" or s.lower() == "first_quarter" or
            s == "1/4"):
        return visualizer.FIRST_QUARTER
    elif(s.lower() == "first_quarter" or s.lower() == "third_quarter" or
            s == "3/4"):
        return visualizer.SECOND_QUARTER

    elif(s.lower().startswith("arbitrary_")):
        s = s.lower().replace("arbitrary", "")
        return visualizer.ARBITRARY_FRACTION(float(s))

    print "Improperly specified argument %s in command %s"%(argnum, cmd)
    system.exit(1)


def printHelpString():
    print "Usage is visualize [OPTION...] SONGIN FILEOUT"
    print " -f, --fresolution=f           sets the resolution of the fourier"
    print "                                    transform. Defaults to 10."
    print " -r, --resolution=AxB          set the output resoltuion AxB,"
    print "                                    Defaults to 1920x1080"
    print " -p, --preview=false,f         display or do not display a preview"
    print "                                    while rendering. defaults to true"
    print " -x, --expadding[=###]         specify the external padding of the"
    print "                                    visualizer. Position is judged "
    print "                                    relative to external padding."
    print "                                    Defaults to 50"
    print " -n, --inpadding[=###]         specify the internal padding between"
    print "                               elements in the visualizer."
    print "                                    defaults to 5"
    print " -m, --colormain[=(#,#,#,#)]   set the dominant color (RGB/RGBA),"
    print "                                    Defaults to (32,32,32)"
    print " -s, --colorsub[=(#,#,#,#)]    set the supporting color (RGB/RGBA),"
    print "                                    Defaults to (24,24,24)"
    print " -b, --colorback[=#,#,#,#]     set the background color (RGB/RGBA),"
    print "                                    Defaults to (16,16,16)"
    print
    print " XLOC = {left, middle, right}"
    print " YLOC = {top, middle, bottom}"
    print 
    print " -e, --elements=(ELEMENTS)     Elements of the visualizer, specified"
    print "                                    in a comma-seperated list"
    print
    print " EX: -e \"hbar MIDDLE -5, bareq MIDDLE 5 inverted\""
    print "      creates a visualizer with a single horizonatal progress bar and"
    print "      an inverted bar equalizer"
    print 
    print " hbar <vlocation> <voffset> :"
    print "      horizontal bar at position <vlocation>"
    print "      with verical offset <voffset>"
    print
    print " bkgimg <PATH>:"
    print "      background image at location PATH"
    print
    print " songinf <hlocation> <vlocation> <title> <artist>:"
    print "       Displays <title> \\n <artist> at specified location"
    print
    print " time <xlocation> <ylocation>:"
    print "       Displays the current time in 0:00/0:00 at specified location"
    print
    print " bareq <xlocation> <yoffset> <direction>:"
    print "      bar-based eqalizer at vertical position <vlocation>,"
    print "      verical offset <yoffset>, and <direction> (inverted/upright)"
    print
    print " polyeq <xlocation> <yoffset> <direction>:"
    print "      polygon eq at vertical position <vlocation>,"
    print "      verical offset <yoffset>, and <direction> (inverted/upright)"
    print
    print " bulbeq <ylocation> <yoffset> <direction> <wireframe> <fatness>:"
    print "      bulbous eq at vertical position <vlocation>, offset <voffset>."
    print "      <wireframe> defaults to false, <fatness> defaults to 1.4"


def add_elements(nset, declarations):
    for declaration in declarations:
        s = declaration.split(" ")
        if(s[0].lower() == "hbar"):
            nset.add(visualizer.HLineVisualizer(
                get_location(s[1], "hbar", "<ylocation>"),
                get_int(s[2], "hbar", "<yoffset>"))
            )
        elif(s[0].lower() == "bkgimg"): #TODO graceful image load fail
            nset.add(visualizer.BackgroundImageVisualizer(s[1]))
        elif(s[0].lower() == "time"):
            nset.add(visualizer.TimeVisualizer(
                get_location(s[1],"time","<xlocation>"),
                get_location(s[2],"time","<ylocation>"))
            )
        elif(s[0].lower() == "songinf"):
            nset.add(visualizer.TextVisualizer(
                get_location(s[1],"songinf","<xlocation>"),
                get_location(s[2],"songinf","<ylocation>"),
                s[3], s[4])
            )
        elif(s[0].lower() == "bareq"):
            nset.add(visualizer.BarEqualizer(
                get_location(s[1], "bareq", "<ylocation"),
                get_int(s[2], "bareq", "<yoffset>"),
                get_boolean(s[3], "bareq", "<direction>"))
            )
        elif(s[0].lower() == "polyeq"):
            nset.add(visualizer.PolygonEqualizer(
                get_location(s[1], "polyeq", "<ylocation>"),
                get_int(s[2], "polyeq","<yoffset>"),
                get_boolean(s[3], "polyeq", "<direction>"))
            )
        elif(s[0].lower() == "bulbeq"):
            if(len(s)==3):
                s.append("true")
            if(len(s)==4):
                s.append("false")
            if(len(s)==5):
                s.append("1.4")
            
            nset.add(visualizer.BulbEqualizerAA(
                get_location(s[1], "bulbeq", "<ylocation>"),
                get_int(s[2], "bulbeq","<yoffset>"),
                get_boolean(s[3], "bulbeq", "<direction>"),
                get_boolean(s[4], "bulbeq", "<wireframe>"),
                get_float(s[5], "bulbeq, <fatness>"))
            )

def get_visualizer_from_args(totaltime):
    try:
        args, postargs = getopt.getopt(
            sys.argv[1:],
            "f:r:p:x:m:n:s:b:e:",
            ["fresolution=", "resolution=", "preview=", "expandding=", "inpadding=",
                "colormain=", "colorsub=", "colorback=", "elements="
            ]
        )
        #look for help
        for arg in args:
            if arg[0]=="-h":
                printHelpString()
                sys.exit(0)
        newset = visualizer.VisualizerSet()
        #look for env stuff
        print args
        for arg in args:
            if arg[0] == "f" or arg[0] == "fresolution=":
                newset.fourier_resolution = int(arg[1])
            elif arg[0] == "r" or arg[0] == "resolution=":
                split = arg[1].replace(")","").replace("(","").replace(" ","").split("x")
                newset.resolution = (int(split[0]), int(split[1]))
            elif arg[0] == "n" or arg[0] == "inpadding=":
                newset.padding_internal = float(arg[1])
            elif arg[0] == "p" or arg[0] == "preview":
                print("preview option not implemented")
            elif arg[0] == "x" or arg[0] == "expadding":
                newset.padding_external = float(arg[1])
            elif arg[0] == "m" or arg[0] == "colormain":
                newset.colorMain = parseColor(arg[1])
            elif arg[0] == "s" or arg[0] == "colorsub":
                newset.colorSub = parseColor(arg[1])
            elif arg[0] == "b" or arg[0] == "colorback":
                newset.colorBkg = parseColor(arg[1])
            elif arg[0] == "e" or arg[0]=="elements":
                addElements(newset, arg[1].split(","))
            else:
                print("Unknown Arg %s"%(arg[0]))
        newset.song_length = totaltime
        return newset
    except getopt.GetoptError as e:
        print("error parsing argv")
        print(e)
        printHelpString()
        sys.exit(0)

class PlayerThread(threading.Thread):
    live = True
    def __init__(self, player):
        super(PlayerThread, self).__init__()
        self.player = player
    def run(self):
        while(self.live and (self.player.get_data() != '')):
            self.player.next_frame()
        self.live = False
    def live(self):
        return self.live
    def kill(self):
        self.live = False

if __name__ == "__main__":
    pygame.init()
    """
    mneplayer = ''
    if (sys.argv[1].split(".")[-1].lower() == "mp3"):
        mneplayer = player.Player(sys.argv[1], player.Player.TYPE_MP3)
    else:
        mneplayer = player.Player(sys.argv[1], player.Player.TYPE_WAV)
    playerthread = PlayerThread(mneplayer)
    playerthread.start()
   """
    
    finish_time=5
    fps = 60
    length = 20.0

    visualizerSet = get_visualizer_from_args(length)
    #visualizerSet = visualizer.make_minimalist_eq(length)
    #visualizerSet = visualizer.make_trendy_visualizer(length)
    visualizerSet.initial_bake()

    print visualizerSet.visualizers
    """
    data = mneplayer.get_data()

    window = pygame.display.set_mode((visualizerSet.resolution[0],visualizerSet.resolution[1]))
    
    elapsed = 1.0/fps
    sumelapsed = 0.0
    initialtime = time.time()
    lastupdate = initialtime
    while(playerthread.live()):
        signal = spectrum.generate_spectrum(mneplayer.get_data())
        signal = spectrum.remove_negative(signal)
        signal = spectrum.into_bins(signal, 10)
        visualizerSet.render_to_screen(window, signal, min(1.0,sumelapsed/length), elapsed)

        pygame.display.flip()

        #preemptive close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                playerthread.kill()
                sys.exit(0)

        elapsed = time.time()-lastupdate
        
        #maintain fps limit on high end machines
        while(elapsed<1.0/fps):
            time.sleep(1.0/fps -elapsed)
            elapsed = time.time()-lastupdate

        lastupdate = time.time()
        sumelapsed = lastupdate-initialtime
    """