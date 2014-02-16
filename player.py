#Playing music
import pyaudio
import wave
import spectrum

#Command Line
import sys

CHUNK = 1024

def play_file(filename):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)
    
    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        print spectrum.generate_spectrum(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

play_file(sys.argv[1])
