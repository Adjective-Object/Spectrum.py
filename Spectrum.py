import visualizer
import pygame
import time
import random
import getopt
import sys
import threading

import mutagen.mp3 #lib to deal with metadata
	
import player
import fft_helper as ffth

import wave
import contextlib

import subprocess as sp
from signal import signal, SIGPIPE, SIG_DFL 


def wav_filelength(fname):
	with contextlib.closing(wave.open(fname,'r')) as f:
		frames = f.getnframes()
		rate = f.getframerate()
		duration = frames / float(rate)
		return duration


def parseColor(string):
	s = string.replace("(","").replace(")","").replace(" ","").split(",")
	if len(s) == 3:
		return pygame.Color(int(s[0]), int(s[1]), int(s[2]))
	elif len(s) == 4:
		return pygame.Color(int(s[0]), int(s[1]), int(s[2]), int(s[3]))
	else:
		print "Improperly specified color argument. Defaulting to Black"
		return pygame.Color(0,0,0)


def get_boolean(s, cmd, argnam):
	if s=="true" or s=="t" or s=="1":
		return True
	elif s=="false" or s=="f" or s=="0":
		return False
	print "Improperly specified boolean argument %s in command %s"%(argnam, cmd)
	sys.exit(1)

def get_int(s, cmd, argnam):
	try:
		return int(s)
	except Exception:
		print "Improperly specified int argument %s in command %s"%(argnam, cmd)
		sys.exit(1)

def get_float(s, cmd, argnam):
	try:
		return float(s)
	except Exception:
		print "Improperly specified float argument %s in command %s"%(argnam, cmd)
		sys.exit(1)

def get_location(s, cmd, argnam):
	if(s.lower() == "bottom"):
		return visualizer.BOTTOM
	elif(s.lower() == "middle" or s=="one-half" or s=="one_hald"):
		return visualizer.MIDDLE
	elif(s.lower() == "top"):
		return visualizer.TOP
	elif(s.lower() == "left"):
		return visualizer.LEFT
	elif(s.lower() == "right"):
		return visualizer.RIGHT

	elif(s.lower() == "first-third" or s.lower() == "first_third" or
			s.lower() == "1/3" or s.lower()=="one-third" or s.lower()=="one_third"):
		return visualizer.FIRST_THIRD
	elif(s.lower() == "second-third" or s.lower() == "second_third" or
			s.lower() == "2/3" or s.lower()=="two-thirds" or s.lower()=="two_thirds"):
		return visualizer.SECOND_THIRD

	elif(s.lower() == "first-quarter" or s.lower() == "first_quarter" or
			s.lower() == "1/4" or s.lower() == "one-quarter" or s.lower()=="one_quarter"):
		return visualizer.FIRST_QUARTER
	elif(s.lower() == "third_quarter" or s.lower() == "third_quarter" or
			s.lower() == "3/4" or s.lower()=="three-quarters" or s.lower()=="three_quarters"):
		return visualizer.SECOND_QUARTER

	elif(s.lower().startswith("arbitrary_")):
		n = s.lower().replace("arbitrary_", "")
		return visualizer.ARBITRARY_FRACTION(float(n))

	print "Improperly specified argument %s in command %s"%(argnam , cmd)
	sys.exit(1)


def printHelpString():
	print "Usage is python MNEVisualize.py [OPTION...] PATH_TO_SONG"
	print " -q, --fresolution=f           sets the resolution of the fourier"
	print "                                    transform. Defaults to 10."
	print " -r, --resolution=AxB          set the output resoltuion AxB,"
	print "                                    Defaults to 1920x1080"
	print " -f, --file=PATH               render images to directory. Disables"
	print "                                    normal window display"
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
	print " -o, --font[=path,size,p2,s2]  sets fontBig and fontSmall"
	print "                                    path/size denote the font and size of the font for fontBig"
	print "                                    p2/s2 denote the font and size for fontSmall"
	print "                                    if unspecified, p2 and s2 degault to path and size."
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
	print " hbar <vlocation> <voffset> <thickness>:"
	print "      horizontal bar at position <vlocation>"
	print "      with verical offset <voffset>"
	print "      <thickness> defaults to internal padding value"
	print "      If <thickness> == 0, then height will be the internal padding value"
	print
	print " bkgimg <PATH>:"
	print "      background image at location PATH"
	print
	print " songinf <hlocation> <vlocation> <title> <artist>:"
	print "       Displays <title> \\n <artist> at specified location"
	print
	print " time <xlocation> <ylocation> <xoffset> <yoffset>:"
	print "       Displays the current time in 0:00/0:00 at specified location"
	print "       <xoffset> and <yoffset> default to 0"
	print
	print " bareq <xlocation> <yoffset> <direction>:"
	print "      bar-based eqalizer at vertical position <vlocation>,"
	print "      verical offset <yoffset>, and <direction> (inverted/upright)"
	print
	print " polyeq <xlocation> <yoffset> <direction>:"
	print "      polygon eq at vertical position <vlocation>,"
	print "      verical offset <yoffset>, and <direction> (inverted/upright)"
	print
	print " bulbeq <ylocation> <yoffset> <direction> <wireframe> <fatness> <hscale>:"
	print "      bulbous eq at vertical position <vlocation>, offset <voffset>."
	print "      <wireframe> defaults to false, <fatness> defaults to 1.4"
	print "      <hscale> defaults to 20.0"
	print
	print "trendy <backgroundImage> <title> <artist>:"
	print "      preconfigured player with WOW SO TRENDY aesthetic"
	print "      defaults to data read from file metadata"
	print
	print "minimalist:"
	print "      preconfigured player with minimalist aesthetic"
def check_num_args(funcname, s, num):
	if len(s)< num:
		print "error: %s expecting %s args got %s"%(funcname, num, len(s))
		sys.exit(1)

def add_elements(nset, declarations):
	for declaration in declarations:
		s = declaration.split(" ")
		while ('' in s):
			s.remove('')

		if(s[0].lower() == "hbar"):
			check_num_args("hbar",s,2)
			if(len(s)<3):
				s = s + [0]
			nset.add(visualizer.HlineVisualizer(
				get_location(s[1], "hbar", "<ylocation>"),
				get_int(s[2], "hbar", "<yoffset>"),
				get_int(s[3], "hbar", "<thickness>"))
			)
		elif(s[0].lower() == "bkgimg"): #TODO graceful image load fail
			check_num_args("hbar",s,2)
			nset.add(visualizer.BackgroundImageVisualizer(s[1]))
		elif(s[0].lower() == "time"):
			check_num_args("hbar",s,2)
			if(len(s)==3):
				s.append("0")
			if(len(s)==4):
				s.append("0")
			nset.add(visualizer.TimeVisualizer(
				get_location(s[1],"time","<xlocation>"),
				get_location(s[2],"time","<ylocation>"),
				get_int(s[3],"time","<xoffset>"),
				get_int(s[4],"time","<yoffset>"))
			)
		elif(s[0].lower() == "songinf"):
			check_num_args("songinf",s,6)
			nset.add(visualizer.TextVisualizer(
				s[3].replace("_"," "), s[4].replace("_"," "),
				get_location(s[1],"songinf","<xlocation>"),
				get_location(s[2],"songinf","<ylocation>"),
				get_int(s[5],"songinf","<xoffset>"),
				get_int(s[6],"songinf","<yoffset>"))
			)
		elif(s[0].lower() == "bareq"):
			check_num_args("bareq",s,3)
			if(len(s)==4):
				s.append("2")
			nset.add(visualizer.BarEqualizer(
				get_location(s[1], "bareq", "<ylocation"),
				get_int(s[2], "bareq", "<yoffset>"),
				get_boolean(s[3], "bareq", "<direction>"),
				get_float(s[4], "bareq", "<speed>"))
			)
		elif(s[0].lower() == "polyeq"):
			check_num_args("polyeq",s,3)
			if (len(s) == 4):
				s.append("f")
			nset.add(visualizer.PolygonEqualizer(
				get_location(s[1], "polyeq", "<ylocation>"),
				get_int(s[2], "polyeq","<yoffset>"),
				get_boolean(s[3], "polyeq", "<direction>"),
				get_boolean(s[4], "polyeq", "<wireframe>"))
			)
		elif(s[0].lower() == "bulbeq"):
			check_num_args("bulbeq",s,3)
			if(len(s)==3):
				s.append("true")
			if(len(s)==4):
				s.append("false")
			if(len(s)==5):
				s.append("1.4")
			if(len(s)==6):
				s.append("20.0")
			
			nset.add(visualizer.BulbEqualizerAA(
				get_location(s[1], "bulbeq", "<ylocation>"),
				get_int(s[2], "bulbeq","<yoffset>"),
				get_boolean(s[3], "bulbeq", "<direction>"),
				get_boolean(s[4], "bulbeq", "<wireframe>"),
				get_float(s[5], "bulbeq", "<fatness>"),
				get_float(s[6], "bulbeq", "<hscale>"))
			)
		elif(s[0].lower() == "minimalist"):
			nset = visualizer.make_minimalist_eq(nset)
		elif(s[0].lower() == "trendy"):
			if len(s)<=2:
				s.append("./dunes.jpg")
			if len(s)<=3:
				s.append("TITLE")
			if len(s)<=4:
				s.append("ARTIST")
			s[2] = s[2].replace("_"," ")
			s[3] = s[3].replace("_"," ")
			nset = visualizer.make_trendy_visualizer(nset, s[1], s[2], s[3])
		else:
			print("cannot parse declaration %s"%(s))

def get_visualizer_from_args():
	try:
		newset = visualizer.VisualizerSet()
		args, postargs = getopt.getopt(
			sys.argv[1:],
			"q:r:f:x:m:n:s:b:e:o",
			["fresolution=", "resolution=", "file=", "expandding=", "inpadding=",
				"colormain=", "colorsub=", "colorback=", "elements=", "font="
			]
		)
		#look for help
		for arg in args:
			if arg[0]=="-h":
				printHelpString()
				sys.exit(0)
		#look for env stuff
		for arg in args:
			if arg[0] == "-q" or arg[0] == "--fresolution":
				newset.fourier_resolution = int(arg[1])
			elif arg[0] == "-r" or arg[0] == "--resolution":
				split = arg[1].replace(")","").replace("(","").replace(" ","").split("x")
				newset.resolution = (int(split[0]), int(split[1]))
			elif arg[0] == "-n" or arg[0] == "--inpadding":
				newset.padding_internal = float(arg[1])
			elif arg[0] == "-f" or arg[0] == "--file":
				newset.to_file = True
				newset.file_destination = arg[1]
			elif arg[0] == "-x" or arg[0] == "--expadding":
				newset.padding_external = float(arg[1])
			elif arg[0] == "-m" or arg[0] == "--colormain":
				newset.colorMain = parseColor(arg[1])
			elif arg[0] == "-s" or arg[0] == "--colorsub":
				newset.colorSub = parseColor(arg[1])
			elif arg[0] == "-b" or arg[0] == "--colorback":
				newset.colorBkg = parseColor(arg[1])
			elif arg[0] == "-e" or arg[0]=="--elements":
				s = arg[1].split(",")
				add_elements(newset, s)
			elif arg[0] == "-o" or arg[0] == "--font":
				s = arg[1].split(",")
				newset.font_big = pygame.font.Font(
						s[0], get_int(s[1], "-o/--font", "param 2"))
				if(len(s)==2):
					s = s+s[0:2]
				elif(len(s)==3):
					arg.append(arg[2])
				newset.font_small = pygame.font.Font(
						s[2], get_int(s[3], "-o/--font", "param 4s"))
			else:
				print("Unknown Arg %s"%(arg[0]))
		if(len(newset.visualizers)==0):
			return visualizer.make_minimalist_eq(newset), postargs

		return newset, postargs
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
	def isLive(self):
		return self.live
	def kill(self):
		self.live = False


def do_preview(visualizerSet, mneplayer, length):
	playerthread = PlayerThread(mneplayer)    
	playerthread.start()

	fps = 60

	#visualizerSet = visualizer.make_minimalist_eq()
	#visualizerSet = visualizer.make_trendy_visualizer()
	#TODO maxtim
	visualizerSet.song_length=length
	visualizerSet.initial_bake()

	print visualizerSet.visualizers
	
	data = mneplayer.get_data()

	pygame.display.set_caption("Spectrum.py Preview")
	window = pygame.display.set_mode((visualizerSet.resolution[0],visualizerSet.resolution[1]))

	elapsed = 1.0/fps
	sumelapsed = 0.0
	initialtime = time.time()
	lastupdate = initialtime

	while(playerthread.isLive()):
		signal = ffth.generate_spectrum(mneplayer.get_data())
		signal = ffth.remove_negative(signal)
		signal = ffth.into_bins(signal, visualizerSet.fourier_resolution)
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


def render_to_video(visualizerSet, mneplayer, length):

	renderSurface = pygame.surface.Surface(visualizerSet.resolution)

	video_fps = 24
	total_video_frames = int(video_fps*length)
	currenttime = 0.0
	current_audio_frame = 0

	renderedframes = 0

	opts = [ "ffmpeg",
		'-y', # (optional) overwrite the output file if it already exists
		'-f', 'rawvideo',
		'-vcodec','rawvideo',
		'-s', '%sx%s'%visualizerSet.resolution, # size of one frame
		'-pix_fmt', 'rgb24',
		'-r', '%s'%(video_fps), # frames per second
		'-i', '-', # The imput comes from a pipe
		'-an', # Tells FFMPEG not to expect any audio (TODO use actual audio file)
		'-vcodec', 'mpeg4',
		visualizerSet.file_destination ]
	
	#print opts	

	pipe = sp.Popen(opts, stdin=sp.PIPE,stdout=sp.PIPE, stderr=sp.PIPE)

	#Ignore SIGPIPES as IOExceptions
	#I HAVE NO IDEA WHAT SIGPIPE DO
	#signal(SIGPIPE,SIG_DFL) 

	#dump = file("./dump","w")

	while mneplayer.get_data()!= '':
		#render nxext frame based on data
		while currenttime < length:
			if(renderedframes%100 == 0):
				print("rendering video frame %s/%s 	(%f/ %f)"%(renderedframes, total_video_frames, currenttime, length))
			signal = ffth.generate_spectrum(mneplayer.get_data())
			signal = ffth.remove_negative(signal)
			signal = ffth.into_bins(signal, visualizerSet.fourier_resolution)
			visualizerSet.render_to_screen(renderSurface, signal, min(1.0, currenttime/length), 1.0/video_fps)

			imgraw = pygame.image.tostring(renderSurface, "RGB")
			try:
				#dump.write(imgraw)
				pipe.stdin.write(imgraw)
			except Exception as e:
				print e
				pass

			renderedframes += 1
			currenttime = renderedframes * 1.0/video_fps

		current_audio_frame += 1
		mneplayer.next_frame()
	dump.close()
	print("done")
	print("closing pipe")
	pipe.stdin.close()
	pipe.stdout.close()
	pipe.stderr.close()
	pipe.terminate()


if __name__ == "__main__":
	pygame.init()

	visualizerSet, postargs = get_visualizer_from_args()

	length = 0
	if (postargs[0].split(".")[-1].lower() == "mp3"):
		mneplayer = player.Player(postargs[0], player.Player.TYPE_MP3, not visualizerSet.to_file)
		audio = mutagen.mp3.MP3(postargs[0])
		length = audio.info.length
	else:
		mneplayer = player.Player(postargs[0], player.Player.TYPE_WAV, not visualizerSet.to_file)
		length = wav_filelength(postargs[0])
	visualizerSet.song_length=length
	visualizerSet.initial_bake()

	if(visualizerSet.to_file):
		render_to_video(visualizerSet, mneplayer, length)
	else:
		do_preview(visualizerSet, mneplayer, length)