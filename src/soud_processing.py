##### NEW VERSION FOR TEST IN TEST_MODEL.IPYNB #########

import librosa
import soundfile as sf
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np


def read_mp3(file):
    signal, sr = librosa.load(file,sr=None)
    return signal,sr

def read_audio(file):
    signal,sr = sf.read(file)
    while True: 
        sd.play(signal,sr)
        sd.wait()

def apply_cqt(signal, sr):
    cqt = librosa.cqt(signal,sr=sr)
    return cqt

def print_cqt(cqt,sr):
    librosa.display.specshow(librosa.amplitude_to_db(cqt,ref=np.max), sr=sr, x_axis='time', y_axis='cqt_note')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Constant Q power spectrum')
    plt.tight_layout()
    plt.show()

def calculate_fft(signal,sr):
    fft = np.fft.fft(signal)
    magnitudes = np.abs(fft)
    frequency = np.fft.fftfreq(len(fft), 1/sr)
    return magnitudes, frequency

def filtrer_frequences(magnitudes, freq, fmax=25000):
    # Garder seulement les fréquences inférieures à fmax
    indices = np.where(freq <= fmax)
    magnitudes_filtrées = magnitudes[indices]
    freq_filtrées = freq[indices]

    return magnitudes_filtrées, freq_filtrées



def print_spectrum(magnitudes,frequency):
    plt.figure(figsize=(10,4))
    plt.plot(frequency,magnitudes)
    plt.title('Spectre Audio')
    plt.xlabel('Fréquence (Hz)')
    plt.ylabel('Magnitude')
    plt.xlim(0, 25000)  # Limiter à 25 kHz
    plt.show()

def afficher_waveform(signal, sr):
    plt.figure(figsize=(10, 4))
    librosa.display.waveshow(signal, sr=sr)
    plt.title('Waveform du Son')
    plt.xlabel('Temps (s)')
    plt.ylabel('Amplitude')
    plt.show()



file = "better-lost_91bpm_C_major.wav"
signal,sr = read_mp3(file)
afficher_waveform(signal, sr)
cqt = apply_cqt(signal,sr)
#print_cqt(cqt,sr)
read_audio(file)

magnitudes, frequency = calculate_fft(signal,sr)
magnitudes_filtrées, freq_filtrées = filtrer_frequences(magnitudes, frequency)

#print_spectrum(magnitudes_filtrées,freq_filtrées)


