import visualizer
import pygame
import time
import random
import getopt
import player
import sys
import spectrum
import threading
#list of values 0.0 to 1.0
def make_random_noise(resolution):
    return [random.random() *(resolution-i)/resolution 
            for i in range(resolution)]

def parseColor(string):
    s = string.remove("(").remove(")").remove(" ").split(",")
    if len(s) == 3:
        return pygame.Color(int(s[0]), int(s[1]), int(s[2]))
    elif len(s) == 4:
        return pygame.Color(int(s[0]), int(s[1]), int(s[2]), int(s[3]))
    else:
        print "Improperly specified color argument. Defaulting to Black"
        return pygame.Color(0,0,0)

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
    print " time <hlocation> <vlocation>:"
    print "       Displays the current time in 0:00/0:00 at specified location"
    print
    print " bareq <vlocation> <voffset> <direction>:"
    print "      bar-based eqalizer at vertical position <vlocation>,"
    print "      verical offset <voffset>, and <direction> (inverted/upright)"
    print
    print " polyeq <vlocation> <voffset> <direction>:"
    print "      polygon eq at vertical position <vlocation>,"
    print "      verical offset <voffset>, and <direction> (inverted/upright)"
    print
    print " bulbeq <vlocation> <voffset> <direction> <fatness>:"
    print "      bulbous eq at vertical position <vlocation>, offset <voffset>."
    print "      fatness defaults to "

def add_elements(nset, declarations):
    for declaration in declarations:
        s = declaration.split(" ")
        

def get_visualizer_from_args():
    try:
        args, postargs = getopt.getopt(
            sys.argv[1:],
            "f:r:p:x:m:n:s:b:",
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
            if arg[0] in interp.keys:
                if arg[0] == "f" or arg[0] == "fresolution=":
                    newset.fourier_resolution = int(arg[1])
                elif arg[0] == "r" or arg[0] == "resolution=":
                    split = arg[1].remove(")").remove("(").remove(" ").split("x")
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
    mneplayer = ''
    if (sys.argv[1].split(".")[-1].lower() == "mp3"):
        mneplayer = player.Player(sys.argv[1], player.Player.TYPE_MP3)
    else:
        mneplayer = player.Player(sys.argv[1], player.Player.TYPE_WAV)

    playerthread = PlayerThread(mneplayer)
    playerthread.start()
   
    finish_time=5
    fps = 60
    length = 20.0

    visualizerSet = get_visualizer_from_args()
    #visualizerSet = visualizer.make_minimalist_eq(length)
    #visualizerSet = visualizer.make_trendy_visualizer(0)
    visualizerSet.initial_bake()
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
