import os
import numpy as np
import music21
import librosa

# Load audio file
#y, sr = librosa.load("data/DSD100/Sources/Dev/053 - Actions - Devil's Words/vocals.wav")
y, sr = librosa.load("data/DSD100/Sources/Dev/053 - Actions - Devil's Words/bass.wav")
#y, sr = librosa.load("data/DSD100/Mixtures/Dev/053 - Actions - Devil's Words/mixture.wav")
y_origin = y
e1=1000000
e2=e1+2815*1000
#y = y[e1:e2]
#print(y.shape, np.max(y), np.min(y), np.mean(np.abs(y)), np.median(y))

# Separate harmonics and percussives into two waveforms
y_harmonic, y_percussive = librosa.effects.hpss(y)

# Beat track on the percussive signal
tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)
print(tempo, beat_frames)

#print(len(y_origin)/librosa.get_duration(y=y_origin, sr=sr) / (tempo/60) / 4) # Number of frames for a 16th
hop_length = int(len(y_origin)/librosa.get_duration(y=y_origin, sr=sr) / (tempo/60) / 4) # 4 estimates/beat
#print("hop_length =", hop_length, " number of beats:", hop_length*librosa.get_duration(y=y_origin, sr=sr)*4)

# Estimate pitch using piptrack
pitches, magnitudes = librosa.core.piptrack(y=y_harmonic, sr=sr, hop_length=hop_length, threshold=1, ref=np.mean)

# Select the pitch with the maximum magnitude for each frame
estimated_pitch = np.argmax(magnitudes, axis=0)

# Create a Stream object from music21
stream = music21.stream.Stream()
part = music21.stream.Part()
part.clef = music21.clef.TrebleClef()
part.timeSignature = music21.meter.TimeSignature('3/4')
part.keySignature = music21.key.KeySignature(2)
part.makeAccidentals(inPlace=True)
part.insert(0, music21.instrument.Bass())

# Initialize variables to keep track of the current pitch and duration
current_pitch = None
current_duration = 0
amp_threshold = 0.03
amplitudes = np.abs(y_harmonic)
#print(amplitudes.shape, estimated_pitch.shape, pitches.shape)
#print(estimated_pitch)

# Add notes to the part based on the estimated pitch
for frame, pitch_value in enumerate(estimated_pitch):
	amplitude = np.mean(amplitudes[frame*hop_length : (frame+1)*hop_length-1])
	
	# If silence, add a Rest
	print(amplitude)
	if amplitude < amp_threshold or pitch_value == 0:
		# Beginning of a silence
		if current_pitch is not None:
			tmp_note = music21.note.Note(current_pitch, quarterLength=current_duration)
			part.append(tmp_note)
			current_duration = 0
		
		# Continued silence
		current_duration += 0.25
		current_pitch = None
		continue
		
	# Convert the pitch value to a pitch name if it isn't a Rest
	pitch_name = music21.pitch.Pitch()
	pitch_name.frequency = pitch_value
	pitch_name.accidental = music21.pitch.Accidental(round(pitch_name.alter))
	pitch_name.octave += 3
	
	# Add or prolongate a Note
	if current_pitch is not None and round(pitch_name.ps, 2) == round(current_pitch.ps, 2):
		current_duration += 0.25
	# If the pitch changes, add the previous note (if any) and start a new note
	else:
		if current_pitch is not None:
			tmp_note = music21.note.Note(current_pitch, quarterLength=current_duration)
			part.append(tmp_note)
		else:
			tmp_note = music21.note.Rest(quarterLength=current_duration)
			part.append(tmp_note)

		# Start a new note with the current pitch
		current_pitch = pitch_name
		current_duration = 0.25

# Add the last note to the part
if current_pitch is not None:
	tmp_note = music21.note.Note(current_pitch, quarterLength=current_duration)
	part.append(tmp_note)

# Add the part to the stream
stream.append(part)

# Create a MusicXML file	
file_path = 'out.mxl'
stream.write('musicxml', fp=file_path)
stream.write('midi', fp="out.midi")
print(f"File saved: {file_path}")

# Convert to PDF using MuseScore batch mode
os.system(f"mscore3 {file_path} -o out.pdf 2>> /dev/null")
print("PDF saved: out.pdf")

