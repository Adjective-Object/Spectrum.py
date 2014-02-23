#Playing music
import pyaudio
import wave

#Command Line
import sys
import subprocess as sp

import numpy
import fft_helper as ffth
import pygame

import mutagen.mp3 #lib to deal with metadata


WAV_CHUNK = 1024
MP3_CHUNK = 4096


def wav_filelength(fname):
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

class Player:
    TYPE_MP3 = "MP3"
    TYPE_WAV = "WAV"
    MP3_CHUNK = 4096
    WAV_CHUNK = 4096
    def __init__(self, filename, extension, realstream = True):
        self.extension = extension
        self.filename = filename
        self.p = pyaudio.PyAudio()
        self.open_file()
        self.stream=None

        self.calc_song_length(filename)

        if realstream:
            self.make_stream()

        self.data = ''

        self.next_frame()

    def calc_song_length(self, filename):
        if (filename.split(".")[-1].lower() == "mp3"):
            audio = mutagen.mp3.MP3(filename)
            self.length = audio.info.length
            self.sample_rate = audio.info.sample_rate
            self.chunksize = self.MP3_CHUNK
        elif (self.extension == self.TYPE_WAV):
            self.length = wav_filelength(filename)
            self.sample_rate  = self.wf.getsampwidth()
            self.chunksize = self.WAV_CHUNK

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
                rate = self.sample_rate,
                output = True)

        elif (self.extension == self.TYPE_WAV):
            self.stream = self.p.open(
                format = self.p.get_format_from_width(self.wf.getsampwidth()),
                channels = self.wf.getnchannels(),
                rate = self.wf.getframerate(),
                output = True)

    def get_current_time(self):
        return float(self.readsamples)/self.length_samples * self.length

    def next_frame(self):
        if (self.extension == self.TYPE_MP3):
            self.data = self.pipe.stdout.read(self.MP3_CHUNK)
            if self.stream:
                self.stream.write(self.data)
        elif (self.extension == self.TYPE_WAV):
            self.data = self.wf.readframes(self.WAV_CHUNK)
            if self.stream:
                self.stream.write(self.data)

    def get_data(self):
        return self.data

    def close(self):
        if self.stream:
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
        print_spectrum(screen, ffth.generate_spectrum(data))
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
        print_spectrum(screen, ffth.generate_spectrum(data))
        data = pipe.stdout.read(MP3_CHUNK)

def print_spectrum(screen, spec):
    spec = ffth.remove_negative(spec)
    spec = ffth.into_bins(spec, 100)
    scale = 1920.0/len(spec) + 1
    screen.fill((255, 255, 255))
    for i in range(len(spec)):
        pygame.draw.line(
                screen,
                (0, 0, 0),
                (int(i*scale), 1080),
                (int(i*scale), (1080 - spec[i] * 1080/250)))
    pygame.display.update()

