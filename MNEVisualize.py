import visualizer
import pygame
import time
import random
import getopt
import sys

#list of values 0.0 to 1.0
def make_random_noise(resolution):
    return [random.random() *(resolution-i)/resolution 
            for i in range(resolution)]


def printHelpString():
    print "Usage is visualize [OPTION...] SONGIN FILEOUT"
    print " -q, --fresolution=f           sets the resolution of the fourier"
    print "                                    transform. Defaults to 10."
    print " -r, --resolution=AxB          set the output resoltuion AxB,"
    print "                                    Defaults to 1920x1080"
    print " -n, --preview=false,f         display or do not display a preview"
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


def get_visualizer_from_args():
    try:
        interps={
            "-i":lambda args: BackgroundImageVisualizer(args[1])
        }
        visualizers=[]
        args, postargs = getopt.getopt(
            sys.argv[1:],
            "f:r:n:p:x:n:m:s:b:l:t:q:i",
            ["fresolution=", "resolution=", "preview=", "expandding=", "inpadding=",
                "colormain=", "colorsub=", "colorback=", "hbar=", "timestamp", "equalizer", "image"
            ]
        )
        for arg in args:
            if arg[0]=="-h":
                printHelpString()
                sys.exit(0)
        for arg in args:
            if arg[0] in interp.keys:
                vis = interps[arg[0]](args)
                visualizers.append(vis if vis else [])
            else:
                print("Unknown Arg %s"%(arg[0]))
        return interps
    except getopt.GetoptError as e:
        print("error parsing argv")
        print(e)
        printHelpString()
        sys.exit(0)


if __name__ == "__main__":
    pygame.init()
    
    finish_time=5
    fps = 60
    length = 20.0

    #visualizerSet = get_visualizer_from_args()
    visualizerSet = visualizer.make_minimalist_eq(length)
    visualizerSet.initial_bake()

    window = pygame.display.set_mode((visualizerSet.resolution[0],visualizerSet.resolution[1]))
    
    elapsed = 1.0/fps
    sumelapsed = 0.0
    initialtime = time.time()
    lastupdate = initialtime
    while(sumelapsed <= length+finish_time):
        if(sumelapsed < length):
            signal = make_random_noise(visualizerSet.fourier_resolution)
        else:
            signal = [0.0]*visualizerSet.fourier_resolution

        visualizerSet.render_to_screen(window, signal, min(1.0,sumelapsed/length), elapsed)

        pygame.display.flip()

        #preemptive close
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        elapsed = time.time()-lastupdate
        
        #maintain fps limit on high end machines
        while(elapsed<1.0/fps):
            time.sleep(1.0/fps -elapsed)
            elapsed = time.time()-lastupdate

        lastupdate = time.time()
        sumelapsed = lastupdate-initialtime
