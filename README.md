# PFE
Music Sheet generation for a given instrument from a mixed music

## Objectif
Le but de ce projet est, dans un premier temps, d’arriver à séparer les pistes des différents instruments dans une musique. Ensuite, il s’agira de générer une partition pour un instrument donné en fonction de la piste isolée.

## Alan (spleeter, basic-pitch, mscore3 integration)

### objectif

- spleeter [(from deezer)](https://github.com/deezer/spleeter) pour split les musiques selon instruments dans des fichiers wav.
- basic-pitch [(from spotify)](https://github.com/spotify/basic-pitch) pour produire fichiers midi à partir des fichiers wav.
- mscore3 [(musescore)](https://ourcodeworld.com/articles/read/1408/how-to-install-musescore-3-in-ubuntu-2004) pour génerer les pdf à partir des midi.

### pour le moment

- splitting à la main:

	spleeter separate -p spleeter:5stems -o splitted file.mp3
	
	note: le modeles spleeter sont trop lourds à push :/

- wav to pdf automatique:

	python3 wav_midi_pdf_pipeline.py [-h] input_wav_path output_pdf_name

### example usage
	
	spleeter separate -p spleeter:5stems -o splitted audiofiles/symphony_instrumental_1st_half.wav

	python3 wav_midi_pdf_pipeline.py splitted/symphony_instrumental_1st_half/piano.wav symphony_piano.pdf

### TODO

input: mp3/wav  

apply spleeter 5stems -> seperated instruments in wav files

for each instrument:

	- apply basic pitch -> midi file
	- apply mscore3 to midi file -> pdf sheet music

### Tools: how to use
#### Split instruments in different mp3 files

spleeter separate -p spleeter:5stems -o splitted file.mp3:  
note: audio can crash the cpu, so cut if necessary

#### Predict midi from audio

basic-pitch . audio.mp3 --sonify-midi  
basic-pitch -h: help about mp3 to midi model

#### Generate pdf sheet from midi file

mscore3 file.mid -o output.pdf

---