import pygame
import random
import time

fourier_resolution = 100

#list of values 0.0 to 1.0
def make_random_noise():
	return [ random.random()*(fourier_resolution-i)/fourier_resolution for i in range(fourier_resolution)]

class Visualizer:
	def __init__():
		pass

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		pass

class BarVisualizer(Visualizer):
	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		self.color = color
		self.bkgColor = bkgColor
		self.padding_external = padding_external
		self.padding_internal = padding_internal

		self.previous_fourier = [0]*fourier_resolution;

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)
		rectwidth = (
			(	operatingdim[0] -
				self.padding_internal * (fourier_resolution-1)
			) / fourier_resolution)

		fourier = [
			self.previous_fourier[i] + (fourier[i]-self.previous_fourier[i])*1.4*elapsed
			for i in range(fourier_resolution)]
		self.previous_fourier = fourier

		surface.fill(self.bkgColor)

		for x in range(fourier_resolution):
			pygame.draw.rect(
				surface,
				self.color,
				pygame.Rect(
					self.padding_external+(rectwidth + self.padding_internal)*x,
					surface.get_height()/2-operatingdim[1]/2 * fourier[x],
					rectwidth,
					operatingdim[1]/2 * fourier[x]
				))

		pygame.draw.rect(
			surface,
			self.color,
			pygame.Rect(
				self.padding_external,
				surface.get_height()/2 + self.padding_internal,
				operatingdim[0] * percentcomp,
				10
			)
		)



class PolygonVisualizer(Visualizer):
	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		self.color = color
		self.bkgColor = bkgColor
		self.padding_external = padding_external
		self.padding_internal = padding_internal

		self.previous_fourier = [0]*fourier_resolution;

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)

		fourier = [
			self.previous_fourier[i] + (fourier[i]-self.previous_fourier[i])*1.4*elapsed
			for i in range(fourier_resolution)]
		self.previous_fourier = fourier

		surface.fill(self.bkgColor)

		poly = [
			(self.padding_external + operatingdim[0], surface.get_height()/2),
			(self.padding_external, surface.get_height()/2)
		]
		w = operatingdim[0]/(fourier_resolution+2.0)
		for x in range(fourier_resolution):
			poly.append( (
				self.padding_external+ w*x + w/2,
				surface.get_height()/2 - operatingdim[1]/2 * fourier[x]
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

class BulbVisualizer(Visualizer):
	def __init__(self,
			color=pygame.Color(32, 32, 32, 255),
			bkgColor=pygame.Color(16, 16, 16, 1),
			padding_external=50,
			padding_internal=5):
		self.color = color
		self.bkgColor = bkgColor
		self.padding_external = padding_external
		self.padding_internal = padding_internal

		self.previous_fourier = [0]*fourier_resolution

		self.bulbs = [0.0]*fourier_resolution
		self.display_bulbs = [0.0]*fourier_resolution

	def render_to_screen(self, surface, fourier, percentcomp, elapsed):
		operatingdim = (surface.get_width()-self.padding_external*2,
							surface.get_height()-self.padding_external*2)


		for i in range(fourier_resolution):
			self.bulbs[i] = max(self.bulbs[i]-elapsed, 0)
			self.bulbs[i] = max( self.bulbs[i], fourier[i]*(fourier[i] > 10 * self. previous_fourier[i]) )
		self.previous_fourier = fourier

		for i in range(fourier_resolution):
			self.display_bulbs[i] += (self.bulbs[i]-self.display_bulbs[i]) * (2*elapsed)

		surface.fill(self.bkgColor)

		poly = [
			(self.padding_external + operatingdim[0], surface.get_height()/2),
			(self.padding_external, surface.get_height()/2)
		]
		w = operatingdim[0]/(fourier_resolution+2.0)
		for x in range(fourier_resolution):
			poly.append( (
				self.padding_external+ w*x + w/2,
				surface.get_height()/2 - operatingdim[1]/2 * self.display_bulbs[x]
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
		
	

if __name__ == "__main__":
	pygame.init()
	
	window = pygame.display.set_mode((800,600), pygame.SRCALPHA)
	visualizer = BulbVisualizer()

	running=True

	fps = 60
	end = fps*10.0

	for i in range(int(end)+1):

		visualizer.render_to_screen(window, make_random_noise(), i/end, 1.0/fps)
		pygame.display.flip()

		time.sleep(1.0/fps)

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				running=False

		if (not running):
			break
	time.sleep(1);

	pygame.quit()