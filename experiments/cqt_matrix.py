import librosa
import numpy as np
import matplotlib.pyplot as plt

# Load the audio file
audio_file = '幸せになって悪いか。(piano transcribe).mp3'
y, sr = librosa.load(audio_file, sr=None, mono=True)  # Ensure mono channel and original sample rate

# Take only the first 10 seconds of audio
duration = 5  # seconds
y_10s = y[:sr * duration]  # Take the first `sr * duration` samples

# Compute the Constant-Q Transform (CQT) for the first 10 seconds
CQT = librosa.cqt(y_10s, sr=sr)

# Visualize the CQT matrix
plt.figure(figsize=(12, 6))
librosa.display.specshow(librosa.amplitude_to_db(np.abs(CQT), ref=np.max),
                          sr=sr, x_axis='time', y_axis='cqt_note')
plt.colorbar(format='%+2.0f dB')
plt.title('Constant-Q Transform (CQT) - First 10 Seconds')
plt.show()

print(CQT, np.array(CQT).shape, 'Frequence_bins X Timesteps')