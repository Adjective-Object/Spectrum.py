import pygame.display, pygame.draw, pygame.gfxdraw, pygame
import random
import time
import sys
import getopt

class Constants:
	pass


constants = Constants()
constants.fourier_resolution = 10

constants.mainColor = pygame.Color(32,32,32)
constants.subColor = pygame.Color(24,24,24)
constants.bkgColor = pygame.Color(16,16,16)

constants.padding_external = 50
constants.padding_internal = 5

constants.resolution = (800,450)

constants.LEFT = 0
constants.MIDDLE = 6
constants.RIGHT = 12
constants.TOP = 0
constants.BOTTOM = 12

constants.font_big = None
constants.font_small = None

#lazy correspondance function
constants.lazy_corr = lambda self, i, elapsed: i

#list of values 0.0 to 1.0
def make_random_noise():
	return [random.random() *(constants.fourier_resolution-i)/constants.fourier_resolution 
			for i in range(constants.fourier_resolution)]


def moving_towards(self, start, destination, delta):
			return (detination if
				(abs(delta)<abs(destination-start) and (delta>0) != (destination-start>0))
				else start+delta)


class Visualizer():
	sortdepth = 1

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		pass


class BackgroundImageVisualizer(Visualizer):

	def __init__(self, image):
		self.original_art = display_art
		self.scaled_art = self.recalcuate_size()

	def recalculate_size(self):
		self.dest_dim = contents.resolution

		if( self.original_art.get_width()*1.0/self.original_art.get_height()  < self.dest_dim[0]*1.0/self.dest_dim[1]):
			self.scaled_art = pygame.transform.smoothscale(
				self.original_art,
				(self.dest_dim[0], int(1.0*self.dest_dim[0]/self.original_art.get_width() * self.original_art.get_height()))
			)
		else:
			self.scaled_art = pygame.transform.smoothscale(
				self.original_art,
				( int(1.0*self.dest_dim[1]/self.original_art.get_height() * self.original_art.get_width() ), self.dest_dim[1])
			)
		return self.scaled_art

	def render(self,surface, percentcomp):
		surface.blit(self.image)


class TextVisualizer(Visualizer):
	def __init__(self, tracktitle, artistname, location_x, location_y):
		self.track_title, self.artist_name = tracktitle, artistname
		self.baked_location = (0,0)

		self.label_artist = self.font_big.render(self.artist, 1, self.color)
		self.label_song = self.font_small.render(self.song_title, 1, self.color)

	def render(self, surface, percentcomp):
		surface.blit(self.label_song, (baked_location[0], baked_location[1]))
		surface.blit(self.label_artist,
				(
					baked_location[0],
					baked_location[1]+constants.font_small.get_height()+constants.padding_internal
				)
		)


class HlineVisualizer(Visualizer):

	def __init__(self, vpos, offsety):
		self.vpos = vpos
		self.offsety = offsety
		recalculate_anchor()

	def recalculate_anchor():
		self.anchor = constants.resolution[1] * 
				(self.offsety/constants.BOTTOM) + offsety

	def render(self, surface, percentcomp):
		pygame.gfxdraw.box(
			surface,
			pygame.Rect(
				self.padding_external,
				self.anchor + self.offsety,
				operatingdim[0] * percentcomp,
				3
			),
			self.color
		)


class BarEqualizer(Equalizer):
	def __init__(self):
		Equalizer.__init__(self,
			1, lambda self, f, elapsed: f,
			color, bkgColor, padding_external, padding_internal
			)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)
		rectwidth = (
			(   operatingdim[0] -
				self.padding_internal * (constants.fourier_resolution-1)
			) / constants.fourier_resolution)

		surface.fill(self.bkgColor)

		for x in range(constants.fourier_resolution):
			pygame.draw.rect(
				surface,
				self.color,
				pygame.Rect(
					self.padding_external+(rectwidth + self.padding_internal)*x,
					surface.get_height()/2-operatingdim[1]/2 * self.display_fourier[x],
					rectwidth,
					operatingdim[1]/2 * self.display_fourier[x]
				)
			)

		pygame.draw.rect(
			surface,
			self.color,
			pygame.Rect(
				self.padding_external,
				surface.get_height()/2 + self.padding_internal,
				operatingdim[0] * percentcomp,
				2
			)
		)


class Equalizer(Visualizer):
	def __init__(self,
			smoothing_factor=0,
			input_output_relationship=constants.lazy_corr,
			):
		self.smoothing_factor = smoothing_factor
		self.input_output_relationship = input_output_relationship

		self.display_fourier = [0]*constants.fourier_resolution
		self.operating_fourier = [0]*constants.fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		self.operating_fourier = self.input_output_relationship( self, fourier, elapsed)
		self.display_fourier = self.gradualize_display(elapsed)
		self.render(surface, percentcomp)

	def gradualize_display(self, elapsed):
		return [
			(self.moving_towards(
					self.display_fourier[i],
					self.operating_fourier[i],
					(self.operating_fourier[i] - self.display_fourier[i]) *
						elapsed * self.smoothing_factor
			))
			for i in range(contents.fourier_resolution)] if self.smoothing_factor != -1 else self.operating_fourier
	
	def render(self, surface, percentcomp):
		pass


class PolygonEqualizer(Equalizer):
	def __init__(self, smoothing_factor=1):
		Equalizer.__init__( smoothing_factor, constants.lazy_corr)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)

		surface.fill(self.bkgColor)

		poly = [
			(self.padding_external + operatingdim[0], surface.get_height()/2),
			(self.padding_external, surface.get_height()/2)
		]
		w = operatingdim[0]/(constants.fourier_resolution*1.0)
		for x in range(constants.fourier_resolution):
			poly.append( (
				self.padding_external+ w*x + w/2,
				surface.get_height()/2 - operatingdim[1]/2 * self.display_fourier[x]
				)
			)
		pygame.draw.polygon(surface, self.color, poly)      

		pygame.draw.rect(
			surface,
			self.color,
			pygame.Rect(
				self.padding_external,
				surface.get_height()/2 + self.padding_internal,
				operatingdim[0] * percentcomp,
				2
			)
		)


class ThresholdPolygonEqualizer(PolygonEqualizer):
	def __init__(self,
			trigger_sensitivity=1,
			decay_factor=0.2):

		Equalizer.__init__(self,
			1, (lambda self, f, elapsed:
					[   max(
							0,
							f[i] * (f[i] > (self.trigger_sensitivity * self.previous_fourier[i])),
							self.operating_fourier[i] - elapsed * self.decay_factor
						)
					for i in range(constants.fourier_resolution)]
			),
			color, bkgColor, padding_external, padding_internal
			)

		self.smoothing_factor = 5
		self.trigger_sensitivity = 50
		self.decay_factor = decay_factor
		self.previous_fourier = [1]*constants.fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		Visualizer.render_to_screen(self, surface, fourier, percentcomp, elapsed)
		self.previous_fourier = fourier


class BulbVisualizer(PolygonEqualizer):
	def __init__(self, smoothing_factor=1):
		PolygonEqualizer.__init__(self, smoothing_factor) 
		self.hscale = 20.0
		self.fatness_factor = 1.4

	def calc_norm(self, relativex):
		#print(relativex, (relativex)**2 /2)
		return (1/2.5) * 2.797**( -(relativex)**2 /2)

	def make_norm(self, array, location, normheight):
		for i in range(max(0, int(location-(3*self.hscale ))), min(len(array), int(location+( 3*self.hscale )))):
			array[i] = max(array[i], self.calc_norm(
				(((i-location<0)*-1)+(1*(i-location>=0))) *
				(( abs(i-location) * (1/self.hscale)/3)**self.fatness_factor)*3
			)* normheight)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)

		heights = [0]*operatingdim[0]

		positionscale = operatingdim[0]*1.0/(len(self.display_fourier)+1)
		for x in range(len(self.display_fourier)):
			self.make_norm(heights, int(positionscale*(x+1)), self.display_fourier[x])

		heights = [ max(int(height*surface.get_height()/2),2) for height in heights]

		self.do_render(surface, operatingdim, heights, percentcomp)

	def do_render(self, surface, operatingdim, heights, percentcomp):

		surface.fill(self.bkgColor)

		for x in range(len(heights)):
			pygame.draw.rect(
				surface,
				self.color,
				pygame.Rect(
					self.padding_external+(x),
					surface.get_height()/2-heights[x]+1,
					1, heights[x]
				)
			)

class BulbVisualizerAA(BulbVisualizer):

	def __init__(self, wireframe = False,  smoothing_factor=1):
		BulbVisualizer.__init__(self, smoothing_factor)
		self.wireframe=wireframe

	def generate_verts(self, heights, line, width, flipped=False):
		verts = [(width-self.padding_external, line),
				(self.padding_external, line)]      

		verts = verts + [
			(   self.padding_external+h,
				line - (heights[h] if not flipped else -heights[h]) )
			for h in range(len(heights))
		]

		return verts

	def do_render(self, surface, operatingdim, heights, percentcomp):
		verts = self.generate_verts(heights, surface.get_height()/2, surface.get_width())

		if( not self.wireframe):
			pygame.gfxdraw.filled_polygon(
				surface,
				verts,
				self.color)

		pygame.gfxdraw.aapolygon(
			surface,
			verts,
			self.color)

class VeryTrendyVisualizer(BulbVisualizerAA):
	def __init__(self, song_title, artist, display_art, display_font_big, display_font_small, song_length_seconds):
		BulbVisualizerAA.__init__(
			self, False,
			pygame.Color(255,255,255,50),
			pygame.Color(255,255,255,30),
			0, 3)

		self.decay_factor = 20
		self.smoothing_factor_fast = 10

		self.song_title = song_title
		self.artist = artist
		self.song_length = song_length_seconds


		self.original_art = display_art

		self.dest_dim = 0;
		
		self.font_big = display_font_big
		self.font_small = display_font_small

		self.label_time = self.font_small.render("0:00", 1, self.bkgColor)
		self.label_alltime = self.font_small.render("/"+self.get_timestring(1), 1, self.color)
		self.old_timestring = "0:00"

	def get_timestring(self, percentcomp):
		n = (percentcomp*self.song_length)
		return "%d:%02d"%(int(n/60), int(n)%60)

	def gradualize_display(self, elapsed):
		out = [0]*constants.fourier_resolution
		for i in range(constants.fourier_resolution):
			if(self.display_fourier[i]>self.operating_fourier[i]):
				out[i] = self.moving_towards(
									self.display_fourier[i],
									self.operating_fourier[i],
									(self.operating_fourier[i] - self.display_fourier[i]) *
										elapsed * self.smoothing_factor
				)
			else:
				out[i] = self.moving_towards(
									self.display_fourier[i],
									self.operating_fourier[i],
									(self.operating_fourier[i] - self.display_fourier[i]) *
										elapsed * self.smoothing_factor_fast
				)
		return out

	def do_render(self, surface, operatingdim, heights, percentcomp):
		if(self.dest_dim != surface.get_size()):
			self.recalculate_size(surface.get_size())

		surface.blit(self.scaled_art, (0,0));

		verts = self.generate_verts(heights, self.line_height, surface.get_width(), True)

		pygame.gfxdraw.filled_polygon(
			surface,
			verts,
			self.color)
		
		pygame.gfxdraw.aapolygon(
			surface,
			verts,
			self.color)
		
		#TODO masking colors

		pygame.gfxdraw.box(
			surface,
			pygame.Rect(
				self.padding_external,
				self.line_height - self.padding_internal - 3,
				operatingdim[0] * percentcomp,
				3
			),
			self.color
		)

		if(self.old_timestring != self.get_timestring(percentcomp)):
			self.label_time = self.font_small.render(self.get_timestring(percentcomp), 1, self.bkgColor)

		surface.blit(self.label_time,
			(surface.get_width()-109, self.line_height-self.font_big.get_height()-8))
		surface.blit(self.label_alltime,
			(surface.get_width()-65, self.line_height-self.font_big.get_height()-8))


class VisualizerSet:
	def __init__(*visualizers):
		self.visualizers = visualizers

	def render(self, surface, percentcomp):		
		surface.fill(constants.bkgColor)
		for visualizer in sorted(self.visualizers, key=lambda v: v.sortdepth)
			v.render_to_screen(self, surface, percentcomp)


def makeVeryTrendyVisualizer():
	return VisualizerSet(
				BackgroundImageVisualizer("./dunes.jpg"),
				HlineVisualizer(constants.MIDDLE, )
				)


def printHelpString():
	print("Usage is visualize [OPTION...] SONGIN FILEOUT")
	print("	-f, --fresolution=f                 sets the resolution of the fourier transform. Defaults to 10.")
	print("	-r, --resolution=AxB                set the output resoltuion AxB, Defaults to 1920x1080")
	print("	-n, --preview=false,f               do not display a preview while rendering")
	print("	-p, --preview=true,t                display a preview while rendering. (will probably render slowly)")
	print
	print("	-x, --expadding[=###]               specify the external padding of the visualizer.")
	print("	                                        All elements will judge relative to external padding")
	print("	                                        defaults to 50")
	print("	-n, --inpadding[=###]               specify the internal padding of between elements in the visualizer.")
	print("	                                        defaults to 5")
	print(" -m, --colormain[=(#,#,#,#)]          set the dominant color (RGB/RGBA), defaults to (32,32,32)")
	print(" -s, --colorsub[=(#,#,#,#)]           set the supporting color (RGB/RGBA), defaults to (24,24,24)")
	print("	-b, --colorback[=#,#,#,#]            set the background color (RGB/RGBA), defaults to (16,16,16)")
	print
	print("	XLOC = {left, middle, right}")
	print("	YLOC = {top, middle, bottom}")
	print 
	print("	-b, --hbar[=YLOC_WIDTH+Y]           horizontal progress bar of thicknes Y at given location, offset")
	print("	                                        vertically by Y pixels.")
	print("	-t, --timestamp[=XLOC+YLOC]         updating timestamp at a given location.")
	print("	-q, --equalizer[=EQTYPE+YLOC+DIR]   eqalizer of type EQTYPE at given location.")
	print("	                                        DIR specifies direction (up, down)")
	print("	-i --image[=PATH]                   set a background image to an image at a given PATH")
	print 
	print(" --preset=trendy[image=PATH] 		equivalent to -i PATH -m (255,255,255,50) -s (255,255,255,30)")
	print("	                                        -t RIGHT_MIDDLE, -b MIDDLE_3-5 -x 0 -n 3 -")

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
	constants.font_big = pygame.font.Font("./Quicksand_regular.ttf",20)
	constants.font_small = pygame.font.Font("./Quicksand_light.ttf",20)
	#visualizers = get_visualizers_from_options()
	
	finish_time=5

	
	visualizers = [VeryTrendyVisualizer(
		"SONG TITLE",
		"ARTIST NAME",
		pygame.image.load("dunes.jpg"),
		pygame.font.Font("./Quicksand_regular.ttf",20),
		pygame.font.Font("./Quicksand_light.ttf",20),
		finish_time
		)]
	

	window = pygame.display.set_mode((800,450))
	

	running=True

	fps = 60
	length = 10.0

	elapsed = 1.0/fps
	sumelapsed = 0.0
	lastupdate = time.time()
	while(sumelapsed <= length+finish_time):
		if(sumelapsed < length):
			signal = make_random_noise()
		else:
			signal = [0.0]*fourier_resolution
		for visualizer in visualizers:
			visualizer.render_to_screen(window, signal, min(1, sumelapsed/length), elapsed)
		pygame.display.flip()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				running=False

		if (not running):
			break

		elapsed = time.time()-lastupdate
		#maintain fps limit on high end machines
		while(elapsed<1.0/fps):
			time.sleep(1.0/fps -elapsed)
			elapsed = time.time()-lastupdate

		lastupdate = time.time()
		sumelapsed += elapsed

	pygame.quit()