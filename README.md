# PFE
Transcription automatique de musique en partitions

## Auteurs
Louis BOUCHEREAU - Alan COURTEL - Fanny GOBBO - Hugo MOSSER \
Etudiants en 3ème année d'Ingénieur informatique - spécialité IA


## Objectif
Le but de ce projet est, dans un premier temps, d’arriver à séparer les pistes des différents instruments dans une musique. Ensuite, il s’agira de générer une partition pour un instrument donné en fonction de la piste isolée.

## PRÉ-REQUIS

### Librairies Python 
Flask : `pip install flask`\
Torch : `pip install torch`\
Librosa : `pip install librosa`\
Midiutil : `pip install midiutil`\
Music21 : `pip install music21`

Il est possible qu'il faille installer uuid\
uuid : `pip install uuid`


### MuseScore

Afin de produire les partitions au format pdf, il faudra installer MuseScore : 

`sudo apt install musescore3`


