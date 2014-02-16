#Visualization maths
import scipy
import scipy.signal
import numpy

def ezplot(data):
    return into_bins(remove_negative(generate_spectrum(data)), 10)

def kill_infinities(data):
    for i in range(len(data)):
        if not numpy.isfinite(data[i]):
            data[i] = 0
    return data

def generate_spectrum(data, stereo=True):
    data = numpy.fromstring(data, 'Int16')
    left = []
    right = []
    if (stereo):
        left = data[::2]
        right = data[1::2]
    else:
        left = data
        right = data
    left = left * scipy.signal.flattop(len(left))
    right = right * scipy.signal.flattop(len(right))
    left_fft = numpy.fft.fft(left)
    right_fft = numpy.fft.fft(right)
    left_fft = 20 * numpy.log10(numpy.absolute(left_fft))
    right_fft = 20 * numpy.log10(numpy.absolute(right_fft))
    spectrum = numpy.add(left_fft, right_fft)
    spectrum = kill_infinities(spectrum)
    spectrum = spectrum / (200.0)
    return spectrum

def remove_negative(spectrum):
    return spectrum[:len(spectrum)/2]

def into_bins(data, num_bins):
    binned = [None] * num_bins
    bin_size = len(data) / num_bins
    for i in range(num_bins):
        binned[i] = data[bin_size * i : bin_size * (i+1)].sum() / bin_size
    return binned

