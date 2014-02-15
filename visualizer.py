import pygame
import random
import time
import sys

fourier_resolution = 5

#list of values 0.0 to 1.0
def make_random_noise():
	return [ random.random() *(fourier_resolution-i)/fourier_resolution 
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
		return [self.display_fourier[i] + (self.operating_fourier[i] - self.display_fourier[i] ) * elapsed * self.smoothing_factor
								for i in range(fourier_resolution)] if self.smoothing_factor != -1 else self.operating_fourier

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
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		
		Visualizer.__init__(self,
			1, (lambda self, f, elapsed: f),
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
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		PolygonVisualizer.__init__(self,
						color,bkgColor,
						padding_external,padding_internal) 
		self.hscale = 15.0
		self.fatness_factor = 1.2

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


# class ThresholdBulbVisualizer(ThresholdPolygonVisualizer):



if __name__ == "__main__":
	pygame.init()
	
	window = pygame.display.set_mode((800,600), pygame.SRCALPHA)
	visualizer = [
		BarVisualizer,
		PolygonVisualizer,
		ThresholdPolygonVisualizer,
		BulbVisualizer] [int(sys.argv[1])]() if len(sys.argv)>1 else BarVisualizer()

	running=True

	fps = 60
	end = fps*10.0

	for i in range(int(end)+1):

		visualizer.render_to_screen(window, make_random_noise(), i/end, 1.0/fps)
		pygame.display.flip()

		time.sleep(1.0/fps)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				running=False

		if (not running):
			break
	time.sleep(1);

	pygame.quit()