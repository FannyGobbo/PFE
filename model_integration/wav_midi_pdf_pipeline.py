import os
import argparse
import subprocess
from music21 import converter
"""
Takes a wav in, basic-pitch(spotify) predicts midi,
split the audio using spleeter if specified
and mscore3 turns it into pdf.
Basically implements these 3 terminal commands in a script:

spleeter separate -p spleeter:5stems -o splitted file.mp3
basic-pitch ./midi audio.mp3
mscore3 path/to/file.mid -o filename.pdf
"""

def convert_wav_to_pdf(wav_file, pdf_file):
    # same as terminal command: $ basic-pitch midi/ path/file.wav
    # --force to overwrite
    wav_to_midi_process = ["basic-pitch", "--save-midi","./midi/", wav_file]
    subprocess.run(wav_to_midi_process)

    # midi file location, and pdf output file location
    midi_file = "midi/" + wav_file.split("/")[-1].split(".")[0] + "_basic_pitch" + ".mid"
    print(f"midi file location: {midi_file}")
    pdf_file = "sheets/" + pdf_file

    # Convert MusicXML to PDF using MuseScore tool
    subprocess.run(["mscore3", midi_file, "-o", pdf_file])

    print(f"Conversion complete. PDF saved to {pdf_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert WAV to MIDI  file and then to PDF.")
    parser.add_argument("input_file_path", help="Input wav full file path")
    parser.add_argument("output_pdf_name", help="Output PDF file name, it will generate the file in sheets/")
    parser.add_argument("--split", action='store_true', default=False, help="will split the input file using spleeter (5 new files generated, bass.wav, drums.wav, other.wav, piano.wav, vocals.wav)")
    args = parser.parse_args()

    SPLIT = args.split
    input_file = args.input_file_path
    pdf_file =  args.output_pdf_name

    if SPLIT:
        # splitting_wav_process = ["spleeter", "separate", "-p", "spleeter:5stems", "-o", "splitted", input_file]
        # subprocess.run(splitting_wav_process)
        folder_name = input_file.split('.')[0].split('/')[-1]
        split_path = "splitted/"+folder_name
        subprocess.run(["ls", split_path])
        choice = str(input("which instrument would you like to obtain a sheet of?: "))
        wav_file = split_path + "/" + choice
        while not os.path.exists(wav_file):
            print(f"---\nfile {wav_file} doesn't exist please choose again")
            subprocess.run(["ls", split_path])
            choice = str(input("which instrument would you like to obtain a sheet of: ?"))
            wav_file = split_path + "/" + choice

    # Convert wav file to PDF
    convert_wav_to_pdf(wav_file, pdf_file)
