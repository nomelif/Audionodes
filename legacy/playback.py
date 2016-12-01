'''
Original source: https://olivereberhard.wordpress.com/2013/11/24/python-class-for-super-simple-raw-audio-playback-using-pyaudio/
(modified)

Created on 15.11.2013

@author: oliver eberhard
'''
from struct import pack
from array import array
import pyaudio
 
"""
Class using Pyaudio for simple playback of raw audio-data represented by a float array.
The user only needs to create an object and call the play_chunk method.
 
"""
 
class Playback(object):
    '''
    classdocs
    '''
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16
    RATE = 41000
 
    def __init__(self):
        '''
        Constructor
        '''
        self.audioDevice = pyaudio.PyAudio()
        self.stream = self.audioDevice.open(format=Playback.FORMAT,
                                            channels=1,
                                            rate=Playback.RATE,
                                            output=True,
                                            frames_per_buffer=Playback.CHUNK_SIZE)
 
    def play_chunk(self, inputArray):
 
        if self.stream.is_stopped():
            self.stream = self.audioDevice.open(format=Playback.FORMAT,
                                                channels=1,
                                                rate=Playback.RATE,
                                                output=True,
                                                frames_per_buffer=Playback.CHUNK_SIZE)
 
        output = array('h')
 
        for i in range(len(inputArray)):
            # Check for Clips
            if int(inputArray[i]*32768) < -32767:
                output.append(-32767)
                print("clip at "+str(i))
            elif int(inputArray[i]*32768) > 32767:
                output.append(32767)
                print("clip at "+str(i))
            else:
                output.append(int(inputArray[i]*32767))
 
        # Converts to bitstream for output
        output = pack('<' + ('h'*len(output)), *output)
 
        self.stream.write(output)
 
    def stopStream(self):
 
        self.stream.stop_stream()
 
    def __del__(self):
        self.stream.close()
        self.audioDevice.terminate()
