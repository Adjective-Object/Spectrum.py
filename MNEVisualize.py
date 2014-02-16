import visualizer
import pygame
import time
import random
import getopt

#list of values 0.0 to 1.0
def make_random_noise(resolution):
    return [random.random() *(resolution-i)/resolution 
            for i in range(resolution)]


def printHelpString():
    print("Usage is visualize [OPTION...] SONGIN FILEOUT")
    print(" -f, --fresolution=f                 sets the resolution of the fourier transform. Defaults to 10.")
    print(" -r, --resolution=AxB                set the output resoltuion AxB, Defaults to 1920x1080")
    print(" -n, --preview=false,f               do not display a preview while rendering")
    print(" -p, --preview=true,t                display a preview while rendering. (will probably render slowly)")
    print
    print(" -x, --expadding[=###]               specify the external padding of the visualizer.")
    print("                                         All elements will judge relative to external padding")
    print("                                         defaults to 50")
    print(" -n, --inpadding[=###]               specify the internal padding of between elements in the visualizer.")
    print("                                         defaults to 5")
    print(" -m, --colormain[=(#,#,#,#)]          set the dominant color (RGB/RGBA), defaults to (32,32,32)")
    print(" -s, --colorsub[=(#,#,#,#)]           set the supporting color (RGB/RGBA), defaults to (24,24,24)")
    print(" -b, --colorback[=#,#,#,#]            set the background color (RGB/RGBA), defaults to (16,16,16)")
    print
    print(" XLOC = {left, middle, right}")
    print(" YLOC = {top, middle, bottom}")
    print 
    print(" -b, --hbar[=YLOC_WIDTH+Y]           horizontal progress bar of thicknes Y at given location, offset")
    print("                                         vertically by Y pixels.")
    print(" -t, --timestamp[=XLOC+YLOC]         updating timestamp at a given location.")
    print(" -q, --equalizer[=EQTYPE+YLOC+DIR]   eqalizer of type EQTYPE at given location.")
    print("                                         DIR specifies direction (up, down)")
    print(" -i --image[=PATH]                   set a background image to an image at a given PATH")
    print 
    print(" --preset=trendy[image=PATH]         equivalent to -i PATH -m (255,255,255,50) -s (255,255,255,30)")
    print("                                         -t RIGHT_MIDDLE, -b MIDDLE_3-5 -x 0 -n 3 -")


def get_visualizers_from_options():
    try:
        interps={
            "-i":lambda args: BackgroundImageVisualizer(args[1])
        }
        visualizers=[]
        args, postargs = getopt.getopt(
            sys.argv[1:],
            "x:n:b:t:q:nphm:m:s:i:",
            ["hbar=","timestamp=","equalizer=","expadding=","inpadding=","image="]
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

    visualizerSet = visualizer.make_trendy_visualizer()
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
