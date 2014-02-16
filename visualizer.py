import pygame.display, pygame.draw, pygame.gfxdraw, pygame
import sys

#global vars
LEFT = 0
MIDDLE = 6
RIGHT = 12
TOP = 0
BOTTOM = 12
FIRST_THIRD= 4
SECOND_THIRD = 8
FIRST_QUARTER= 3
SECOND_QUARTER = 9


def ARBITRARY_FRACTION(x):
	return 12*x

RESOLUTION = (800, 450)

def moving_towards(start, destination, delta):
			return (destination if
				(abs(delta)<abs(destination-start) and (delta>0) != (destination-start>0))
				else start+delta)


class Visualizer(object):
	sortdepth = 1
	parent = None

	def __init__(self):
		self.baked_location = (0,0)

	def initial_bake(self):
		pass

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		pass

	def get_baked_coords(self, xbake, ybake):
		return (self.parent.padding_external+1.0*self.parent.operatingdim[0]*xbake/RIGHT,
				self.parent.padding_external+1.0*self.parent.operatingdim[1]*ybake/BOTTOM)

class BackgroundImageVisualizer(Visualizer):

	def __init__(self, imagePATH):
		Visualizer.__init__(self)
		self.original_art = pygame.image.load(imagePATH)
		self.scaled_art = self.recalculate_size()

	def recalculate_size(self):
		self.dest_dim = RESOLUTION

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

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		surface.blit(self.scaled_art, (0,0))


class TextVisualizer(Visualizer):
	def __init__(self, tracktitle, artistname, location_x, location_y):
		Visualizer.__init__(self)
		self.track_title, self.artist_name = tracktitle, artistname
		self.location = (location_x, location_y)

	def initial_bake(self):		
		self.label_artist = self.parent.font_big.render(self.artist_name, 1, self.parent.colorMain)
		self.label_song = self.parent.font_small.render(self.track_title, 1, self.parent.colorSub)
		self.baked_location = self.get_baked_coords(self.location[0], self.location[1])

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		surface.blit(self.label_song, (self.baked_location[0], self.baked_location[1]))
		surface.blit(self.label_artist,
				(
					self.baked_location[0],
					self.baked_location[1]+self.parent.font_small.get_height()+self.parent.padding_internal
				)
		)


class HlineVisualizer(Visualizer):

	def __init__(self, location_y, offsety):
		Visualizer.__init__(self)
		self.offsety = offsety
		self.location = (LEFT, location_y)

	def initial_bake(self):
		self.baked_location = self.get_baked_coords(self.location[0], self.location[1])

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		#print(self.baked_location)
		pygame.gfxdraw.box(
			surface,
			pygame.Rect(
				self.baked_location[0],
				self.baked_location[1] + self.offsety,
				self.parent.operatingdim[0] * percentcomp,
				3
			),
			self.parent.colorMain
		)


class TimeVisualizer(Visualizer):
	def __init__(self, xpos, ypos, totaltime):
		Visualizer.__init__(self)
		self.song_length = totaltime
		self.old_timestring = "0:00"
		self.location = (xpos, ypos)

	def initial_bake(self):
		self.label_time = self.parent.font_small.render("0:00", 1, self.parent.colorSub)
		self.label_alltime = self.parent.font_small.render("/"+self.get_timestring(1), 1, self.parent.colorMain)
		self.baked_location = self.get_baked_coords(self.location[0], self.location[1])

	def get_timestring(self, percentcomp):
		n = (percentcomp * self.song_length)
		return "%d:%02d"%(int(n/60), int(n)%60)

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		if(self.old_timestring != self.get_timestring(percentcomp)):
			self.label_time = self.parent.font_small.render(self.get_timestring(percentcomp), 1, self.parent.colorSub)

		surface.blit(self.label_time,
			(self.baked_location[0]-109, self.baked_location[1]-self.parent.font_big.get_height()-8))
		surface.blit(self.label_alltime,
			(self.baked_location[0]-65, self.baked_location[1]-self.parent.font_big.get_height()-8))



class Equalizer(Visualizer):
	def __init__(self,
			smoothing_factor=0,
			input_output_relationship=lambda self, i, elapsed: i,
			):
		Visualizer.__init__(self)
		self.smoothing_factor = smoothing_factor
		self.input_output_relationship = input_output_relationship

	def initial_bake(self):
		self.display_fourier = [0]*self.parent.fourier_resolution
		self.operating_fourier = [0]*self.parent.fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		self.operating_fourier = self.input_output_relationship( self, fourier, elapsed)
		self.display_fourier = self.gradualize_display(elapsed)
		self.render(surface)

	def gradualize_display(self, elapsed):
		return ([( moving_towards(
					self.display_fourier[i],
					self.operating_fourier[i],
					(self.operating_fourier[i] - self.display_fourier[i]) *
						elapsed * self.smoothing_factor
			) if  self.display_fourier[i]<self.operating_fourier[i] else
			moving_towards(
					self.display_fourier[i],
					self.operating_fourier[i],
					(self.operating_fourier[i] - self.display_fourier[i]) *
						elapsed * self.smoothing_factor * 10
			) ) for i in range(self.parent.fourier_resolution)]

		if self.smoothing_factor != -1 else self.operating_fourier)
	
	def render(self, surface):
		pass 


class BarEqualizer(Equalizer):
	def __init__(self, location_y, offset_y):
		Equalizer.__init__(self,
			1, lambda self, f, elapsed: f)
		self.location_y = location_y
		self.offsety = offset_y

	def initial_bake(self):
		Equalizer.initial_bake(self)
		self.baked_location = self.get_baked_coords(LEFT,self.location_y)

	def render(self, surface):
		rectwidth = (
			(   self.parent.operatingdim[0] -
				self.parent.padding_internal * (self.parent.fourier_resolution-1)
			) / self.parent.fourier_resolution)

		for x in range(self.parent.fourier_resolution):
			pygame.draw.rect(
				surface,
				self.parent.colorMain,
				pygame.Rect(
					self.baked_location[0]+(rectwidth + self.parent.padding_internal)*x,
					self.baked_location[1]+self.offsety-self.parent.operatingdim[1]/2 * self.display_fourier[x],
					rectwidth,
					self.parent.operatingdim[1]/2 * self.display_fourier[x]
				)
			)


class PolygonEqualizer(Equalizer):
	def __init__(self, smoothing_factor=1, input_output_relationship=lambda self, i, elapsed: i):
		Equalizer.__init__( self, smoothing_factor, input_output_relationship)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.parent.padding_external*2,
							surface.get_height()-self.parent.padding_external*2)

		poly = [
			(self.parent.padding_external + operatingdim[0], surface.get_height()/2),
			(self.parent.padding_external, surface.get_height()/2)
		]
		w = operatingdim[0]/(self.parent.fourier_resolution*1.0)
		for x in range(self.parent.fourier_resolution):
			poly.append( (
				self.parent.padding_external+ w*x + w/2,
				surface.get_height()/2 - operatingdim[1]/2 * self.display_fourier[x]
				)
			)
		pygame.draw.polygon(surface, self.parent.colorMain, poly)      

		pygame.draw.rect(
			surface,
			self.parent.colorMain,
			pygame.Rect(
				self.parent.padding_external,
				surface.get_height()/2 + self.parent.padding_internal,
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
					for i in range(self.parent.fourier_resolution)]
			),
			color, bkgColor, padding_external, padding_internal
			)

		self.smoothing_factor = 5
		self.trigger_sensitivity = 50
		self.decay_factor = decay_factor
		self.previous_fourier = [1]*self.parent.fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		Visualizer.render_to_screen(self, surface, fourier, percentcomp, elapsed)
		self.previous_fourier = fourier


class BulbEqualizer(PolygonEqualizer):
	def __init__(self, smoothing_factor=1, orientation=True):
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

	def render(self, surface):
		operatingdim = (surface.get_width()-self.parent.padding_external*2,
							surface.get_height()-self.parent.padding_external*2)

		heights = [0]*operatingdim[0]

		positionscale = operatingdim[0]*1.0/(len(self.display_fourier)+1)
		for x in range(len(self.display_fourier)):
			self.make_norm(heights, int(positionscale*(x+1)), self.display_fourier[x])

		heights = [ max(int(height*surface.get_height()/2),2) for height in heights]

		self.do_render(surface, operatingdim, heights)

	def do_render(self, surface, operatingdim, heights):
		for x in range(len(heights)):
			pygame.draw.rect(
				surface,
				self.parent.colorMain,
				pygame.Rect(
					self.parent.padding_external+(x),
					surface.get_height()/2-heights[x]+1,
					1, heights[x]
				)
			)

class BulbEqualizerAA(BulbEqualizer):

	def __init__(self, location_y, wireframe = False, orientation=True,
			smoothing_factor=1,  input_output_relationship=lambda self, i, elapsed: i):
		BulbEqualizer.__init__(self, smoothing_factor, input_output_relationship)
		self.wireframe=wireframe
		self.location = (LEFT, location_y)
		self.orientation = orientation;

	def initial_bake(self):
		super(BulbEqualizerAA, self).initial_bake()
		self.baked_location = self.get_baked_coords(self.location[0], self.location[1])

	def generate_verts(self, heights, line, width, flipped=False):
		verts = [(width-self.parent.padding_external, line),
				(self.parent.padding_external, line)]      

		verts = verts + [
			(   self.parent.padding_external+h,
				line - (heights[h] if not flipped else -heights[h]) )
			for h in range(len(heights))
		]

		return verts

	def do_render(self, surface, operatingdim, heights):
		verts = self.generate_verts(heights, self.baked_location[1], surface.get_width(), not self.orientation)

		if( not self.wireframe):
			pygame.gfxdraw.filled_polygon(
				surface,
				verts,
				self.parent.colorMain)

		pygame.gfxdraw.aapolygon(
			surface,
			verts,
			self.parent.colorMain)


class VisualizerSet:
	fourier_resolution = 10

	colorMain = pygame.Color(64,64,64)
	colorSub = pygame.Color(32,32,32)
	colorBkg = pygame.Color(16,16,16)

	padding_external = 50
	padding_internal = 5

	resolution = (900,450)

	font_big = None
	font_small = None

	def __init__(self, *vargs):
		self.visualizers = []+vargs
		for v in self.visualizers:
			v.parent = self

	def add(self, v):
		v.parent = self
		self.visualizers.add(v)

	def initial_bake(self):
		self.operatingdim = (self.resolution[0]-self.padding_external*2, self.resolution[1]-self.padding_external*2)

		for v in self.visualizers:
			v.initial_bake()

	def render_to_screen(self, surface, signal, percentcomp, elapsed):	
		surface.fill(self.colorBkg)
		for v in sorted(self.visualizers, key=lambda v: v.sortdepth):
			v.render_to_screen(surface, signal, percentcomp, elapsed)

def make_trendy_visualizer(totaltime):
	v = VisualizerSet(
				BackgroundImageVisualizer("./dunes.jpg"),
				HlineVisualizer(SECOND_THIRD, -8),
				TextVisualizer("THE HIKIKORMORI BLUES","SENPAIS IN PARADISE",LEFT, MIDDLE),
				TimeVisualizer(RIGHT, SECOND_THIRD, totaltime),
				BulbEqualizerAA(SECOND_THIRD, False, False)
				)
	v.padding_external = 0
	v.colorMain = pygame.Color(255,255,255,50)
	v.colorSub = pygame.Color(255,255,255,30)
	v.font_big = pygame.font.Font("./Quicksand_regular.ttf",20)
	v.font_small = pygame.font.Font("./Quicksand_light.ttf",20)

	return v

def make_minimalist_eq(totaltime):
	v = VisualizerSet(
				TimeVisualizer(RIGHT, MIDDLE, totaltime),
				BarEqualizer(SECOND_THIRD, 0)
				)
	v.font_big = pygame.font.Font("./Quicksand_regular.ttf",20)
	v.font_small = pygame.font.Font("./Quicksand_regular.ttf",20)
	return v