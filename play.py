"""PyAudio Example: Play a wave file."""

import pyaudio
import wave
import sys
import numpy
from time import sleep

CHUNK_SIZE = 1024

wf = wave.open("odesza.wav", 'rb')
samplerate = wf.getframerate()
# instantiate PyAudio
p = pyaudio.PyAudio()

# open stream
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)


data = wf.readframes(CHUNK_SIZE)

# play stream continuously
chunk_num = 0
while data != '':
	print("chunk %s"%(chunk_num))
    stream.write(data)
    data = wf.readframes(CHUNK_SIZE)
    sleep(wf.getframerate() * CHUNK_SIZE)
    chunk_num++

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()