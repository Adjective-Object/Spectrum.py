import pygame.display, pygame.draw, pygame.gfxdraw, pygame
import random
import time
import sys

fourier_resolution = 10

#list of values 0.0 to 1.0
def make_random_noise():
	return [random.random() *(fourier_resolution-i)/fourier_resolution 
			for i in range(fourier_resolution)]


class Visualizer:
	def __init__(self,
			smoothing_factor=0,
			input_output_relationship=lambda self, i, elapsed: i,

			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5,
			):
		self.color = color
		self.bkgColor = bkgColor
		self.padding_external = padding_external
		self.padding_internal = padding_internal
		self.smoothing_factor = smoothing_factor

		self.input_output_relationship = input_output_relationship

		self.display_fourier = [0]*fourier_resolution
		self.operating_fourier = [0]*fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		self.operating_fourier = self.input_output_relationship( self, fourier, elapsed)
		self.display_fourier = self.gradualize_display(elapsed)
		self.render(surface, percentcomp)

	def gradualize_display(self, elapsed):
		return [
			self.moving_towards(
				self.display_fourier[i],
				self.operating_fourier[i],
				 (self.operating_fourier[i] - self.display_fourier[i] ) * elapsed * self.smoothing_factor)
				for i in range(fourier_resolution)] if self.smoothing_factor != -1 else self.operating_fourier
	
	def moving_towards(self, start, destination, delta):
			return (detination if
				(abs(delta)<abs(destination-start) and (delta>0) != (destination-start>0))
				else start+delta)

	def render(self, surface, percentcomp):
		pass


class BarVisualizer(Visualizer):
	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		Visualizer.__init__(self,
			1, lambda self, f, elapsed: f,
			color, bkgColor, padding_external, padding_internal
			)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)
		rectwidth = (
			(	operatingdim[0] -
				self.padding_internal * (fourier_resolution-1)
			) / fourier_resolution)

		surface.fill(self.bkgColor)

		for x in range(fourier_resolution):
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



class PolygonVisualizer(Visualizer):
	def __init__(self,
			smoothing_factor=1,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		
		Visualizer.__init__(self,
			smoothing_factor, (lambda self, f, elapsed: f),
			color, bkgColor, padding_external, padding_internal
			)

	def render(self, surface, percentcomp):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)

		surface.fill(self.bkgColor)

		poly = [
			(self.padding_external + operatingdim[0], surface.get_height()/2),
			(self.padding_external, surface.get_height()/2)
		]
		w = operatingdim[0]/(fourier_resolution*1.0)
		for x in range(fourier_resolution):
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


class ThresholdPolygonVisualizer(PolygonVisualizer):
	def __init__(self,
			trigger_sensitivity=1,
			decay_factor=0.2,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):

		Visualizer.__init__(self,
			1,
			(	lambda self, f, elapsed:
					[	max(
							0,
							f[i] * (f[i] > (self.trigger_sensitivity * self.previous_fourier[i])),
							self.operating_fourier[i] - elapsed * self.decay_factor
						)
					for i in range(fourier_resolution)]
			),
			color, bkgColor, padding_external, padding_internal
			)

		self.smoothing_factor = 5

		self.trigger_sensitivity = 50
		self.decay_factor = decay_factor
		self.previous_fourier = [1]*fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		Visualizer.render_to_screen(self, surface, fourier, percentcomp, elapsed)
		self.previous_fourier = fourier


class BulbVisualizer(PolygonVisualizer):
	def __init__(self,
			smoothing_factor=1,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		PolygonVisualizer.__init__(self, smoothing_factor,
						color,bkgColor,
						padding_external,padding_internal) 
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


class BulbVisualizerAA(BulbVisualizer):

	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5, **kwargs):
		BulbVisualizer.__init__(self, 2, color,bkgColor,padding_external,padding_internal)
		self.wireframe=False

	def generate_verts(self, heights, line, width, flipped=False):
		verts = [(width-self.padding_external, line),
				(self.padding_external, line)]		

		verts = verts + [
			(	self.padding_external+h,
				line - (heights[h] if not flipped else -heights[h]) )
			for h in range(len(heights))
		]

		return verts

	def do_render(self, surface, operatingdim, heights, percentcomp):

		surface.fill(self.bkgColor)

		verts = self.generate_verts(heights, surface.get_height()/2, surface.get_width())

		if( not self.wireframe):
			pygame.gfxdraw.filled_polygon(
				surface,
				verts,
				self.color)
		return verts

		pygame.gfxdraw.aapolygon(
			surface,
			verts,
			self.color)

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


class BulbVisualizerAAWireframe(BulbVisualizerAA):
	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5, **kwargs):
		BulbVisualizer.__init__(self,color,bkgColor,padding_external,padding_internal)
		self.wireframe=True


class VeryTrendyVisualizer(BulbVisualizerAA):
	def __init__(self, song_title, artist, display_art, display_font_big, display_font_small, song_length_seconds):
		BulbVisualizerAA.__init__(
			self,
			pygame.Color(255,255,255,50),
			pygame.Color(255,255,255,20),
			0, 3)

		self.decay_factor = 20
		self.smoothing_factor_fast = 10

		self.song_title = song_title
		self.artist = artist
		self.song_length = song_length_seconds


		#self.original_art = album_art

		dest_dim = pygame.display.get_surface().get_size();
		self.line_height = int(dest_dim[1]*0.63)

		if( display_art.get_width()*1.0/display_art.get_height()  < dest_dim[0]*1.0/dest_dim[1]):
			self.scaled_art = pygame.transform.smoothscale(
				display_art,
				(dest_dim[0], int(1.0*dest_dim[0]/display_art.get_width() * display_art.get_height()))
			)
		else:
			self.scaled_art = pygame.transform.smoothscale(
				display_art,
				( int(1.0*dest_dim[1]/display_art.get_height() * display_art.get_width() ), dest_dim[1])
			)

		self.font_big = display_font_big
		self.font_small = display_font_small

		self.label_artist = self.font_big.render(self.artist, 1, self.color)
		self.label_song = self.font_small.render(self.song_title, 1, self.color)
		self.label_time = self.font_small.render("0:00", 1, self.color)
		self.label_alltime = self.font_small.render("/"+self.get_timestring(1), 1, self.color)

		self.old_timestring = "0:00"

	def get_timestring(self, percentcomp):
		n = (percentcomp*self.song_length)
		return "%d:%02d"%(int(n/60), int(n)%60)

	def gradualize_display(self, elapsed):
		out = [0]*fourier_resolution
		for i in range(fourier_resolution):
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
		surface.blit(self.scaled_art, (0,0));

		verts = self.generate_verts(heights, self.line_height, surface.get_width(), True)

		pygame.gfxdraw.filled_polygon(
			surface,
			verts,
			self.color)
		"""
		pygame.gfxdraw.aapolygon(
			surface,
			verts,
			self.color)
		"""
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

		surface.blit(self.label_song, (18, self.line_height-self.font_small.get_height()-self.font_big.get_height()-3))
		surface.blit(self.label_artist, (18, self.line_height-self.font_big.get_height()-8))

		if(self.old_timestring != self.get_timestring(percentcomp)):
			self.label_time = self.font_small.render(self.get_timestring(percentcomp), 1, self.bkgColor)

		surface.blit(self.label_time,
			(surface.get_width()-109, self.line_height-self.font_big.get_height()-8))
		surface.blit(self.label_alltime,
			(surface.get_width()-65, self.line_height-self.font_big.get_height()-8))



if __name__ == "__main__":
	pygame.init()
	"""
	visualizer = [
		BarVisualizer,
		PolygonVisualizer,
		ThresholdPolygonVisualizer,
		BulbVisualizer,
		BulbVisualizerAA,
		BulbVisualizerAAWireframe
		] [int(sys.argv[1])] () if len(sys.argv)>1 else BarVisualizer()
	"""
	running=True

	fps = 60
	length = 10.0

	window = pygame.display.set_mode((800,450))
	visualizer = VeryTrendyVisualizer(
			"S-SONG SENPAI",
			"IS-LIMBICS",
			pygame.image.load("./dunes.jpg"),
			pygame.font.Font("./Quicksand_regular.ttf", 20),
			pygame.font.Font("./Quicksand_light.ttf", 20),
			length
		)

	elapsed = 1.0/fps
	sumelapsed = 0.0
	lastupdate = time.time()
	while(sumelapsed <= length+2):
		if(sumelapsed < length):
			signal = make_random_noise()
		else:
			signal = [0.0]*fourier_resolution
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