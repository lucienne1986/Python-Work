#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 16:37:50 2019

@author: lucienne
"""

import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import datetime
import wave

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 8192 # 2^12 samples for buffer
record_secs = 3 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)

print("recording audio and plotting")
frames = []

# loop through stream and append audio chunks to frame array
for ii in range(0,int((samp_rate/chunk)*record_secs)):
    data = stream.read(chunk)
    frames.append(data)
    # record data for plotting
    stream.start_stream()
    data = np.frombuffer(stream.read(chunk),dtype=np.int16)
    print(datetime.datetime.now())

print("finished recording")

#stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

# mic sensitivity correction and bit conversion
mic_sens_dBV = -47.0 # mic sensitivity in dBV + any gain
mic_sens_corr = np.power(10.0,mic_sens_dBV/20.0) # calculate mic sensitivity conversion factor

# (USB=5V, so 15 bits are used (the 16th for negatives)) and the manufacturer microphone sensitivity corrections
data = ((data/np.power(2.0,15))*5.25)*(mic_sens_corr) 

# compute FFT parameters
f_vec = samp_rate*np.arange(chunk/2)/chunk # frequency vector based on window size and sample rate
mic_low_freq = 100 # low frequency response of the mic
low_freq_loc = np.argmin(np.abs(f_vec-mic_low_freq))
fft_data = (np.abs(np.fft.fft(data))[0:int(np.floor(chunk/2))])/chunk
fft_data[1:] = 2*fft_data[1:]

max_loc = np.argmax(fft_data[low_freq_loc:])+low_freq_loc

# save the audio frames as .wav file
wavefile = wave.open(wav_output_filename,'wb')
wavefile.setnchannels(chans)
wavefile.setsampwidth(audio.get_sample_size(form_1))
wavefile.setframerate(samp_rate)
wavefile.writeframes(b''.join(frames))
wavefile.close()

# plot
plt.style.use('ggplot')
plt.rcParams['font.size']=18
fig = plt.figure(figsize=(13,8))
ax = fig.add_subplot(111)
plt.plot(f_vec,fft_data)
ax.set_ylim([0,2*np.max(fft_data)])
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [Pa]')
ax.set_xscale('log')
plt.grid(True)

# max frequency resolution 
plt.annotate(r'$\Delta f_{max}$: %2.1f Hz' % (samp_rate/(2*chunk)),xy=(0.7,0.92),\
             xycoords='figure fraction')

# annotate peak frequency
annot = ax.annotate('Freq: %2.1f'%(f_vec[max_loc]),xy=(f_vec[max_loc],fft_data[max_loc]),\
                    xycoords='data',xytext=(0,150),textcoords='offset points',\
                    arrowprops=dict(arrowstyle="->"),ha='center',va='bottom')
    
plt.savefig('fft_1kHz_signal.png',dpi=300,facecolor='#FCFCFC')
plt.show()