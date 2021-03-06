import pyaudio
import numpy as np

p = pyaudio.PyAudio()

volume = 0.5     # range [0.0, 1.0]
fs = 44100       # sampling rate, Hz, must be integer
duration = 5   # in seconds, may be float
freq = [i for i in range(10000, 20000, 100)]        # sine frequency, Hz, may be float


for f in freq:
# generate samples, note conversion to float32 array
    print (f)
    samples = (np.sin(2*np.pi*np.arange(fs*duration)*f/fs)).astype(np.float32)

# for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=fs,
                    output=True)

    # play. May repeat with different volume values (if done interactively)
    print ("Writing")
    stream.write(volume*samples)

    print ("Done")
    stream.stop_stream()
    stream.close()

p.terminate()
