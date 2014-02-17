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

class Player:
    TYPE_MP3 = "MP3"
    TYPE_WAV = "WAV"
    MP3_CHUNK = 4096
    WAV_CHUNK = 4096
    def __init__(self, filename, extension):
        self.extension = extension
        self.filename = filename
        self.p = pyaudio.PyAudio()
        self.open_file()
        self.make_stream()
        self.data = ''
        self.next_frame()
    def open_file(self):
        if (self.extension == self.TYPE_MP3):
            self.pipe = sp.Popen(["ffmpeg",
                "-i", self.filename,
                "-f", "s16le",
                "-acodec", "pcm_s16le",
                "-ar", "44100",
                "-ac", "2",
                "-"],
                stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        elif (self.extension == self.TYPE_WAV):
            self.wf = wave.open(self.filename, 'rb')
    def make_stream(self):
        if (self.extension == self.TYPE_MP3):
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels = 2,
                rate = 44100,
                output = True)
        elif (self.extension == self.TYPE_WAV):
            self.stream = self.p.open(
                format = self.p.get_format_from_width(self.wf.getsampwidth()),
                channels = self.wf.getnchannels(),
                rate = self.wf.getframerate(),
                output = True)

    def next_frame(self):
        if (self.extension == self.TYPE_MP3):
            self.data = self.pipe.stdout.read(self.MP3_CHUNK)
            self.stream.write(self.data)
        elif (self.extension == self.TYPE_WAV):
            self.data = self.wf.readframes(self.WAV_CHUNK)
            self.stream.write(self.data)

    def get_data(self):
        return self.data

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

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

