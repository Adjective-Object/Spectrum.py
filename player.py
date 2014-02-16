#Playing music
import pyaudio
import wave

#Command Line
import sys
import subprocess as sp

import numpy
import spectrum
import pygame

WAV_CHUNK = 1024
MP3_CHUNK = 4096

def play_wav(filename, screen):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
    
    data = wf.readframes(WAV_CHUNK)
    
    while data != '':
        stream.write(data)
        print_spectrum(screen, spectrum.generate_spectrum(data))
        data = wf.readframes(WAV_CHUNK)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

def play_mp3(filename, screen):
    p = pyaudio.PyAudio()
    pipe = sp.Popen(["ffmpeg",
        "-i", sys.argv[1],
        "-f", "s16le",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        "-"],
        stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

    stream = p.open(format=pyaudio.paInt16,
        channels = 2,
        rate = 44100,
        output = True)
    
    data = pipe.stdout.read(MP3_CHUNK)
    while data != '':
        stream.write(data)
        print_spectrum(screen, spectrum.generate_spectrum(data))
        data = pipe.stdout.read(MP3_CHUNK)

def print_spectrum(screen, spec):
    spec = spectrum.remove_negative(spec)
    spec = spectrum.into_bins(spec, 100)
    scale = 1920.0/len(spec) + 1
    screen.fill((255, 255, 255))
    for i in range(len(spec)):
        pygame.draw.line(
                screen,
                (0, 0, 0),
                (int(i*scale), 1080),
                (int(i*scale), (1080 - spec[i] * 1080/250)))
    pygame.display.update()


def main():
    pygame.init()
    screen = pygame.display.set_mode((1920, 1080))
    extension = sys.argv[1].split(".")[-1].lower()
    if extension == "wav":
        play_wav(sys.argv[1], screen)
    elif extension == "mp3":
        play_mp3(sys.argv[1], screen)
    else:
        print "Unsupported file format!"
    
main()
