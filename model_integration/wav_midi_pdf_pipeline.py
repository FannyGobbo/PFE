import argparse
import subprocess
from music21 import converter
"""
Takes a wav in, basic-pitch(spotify) predicts midi,
and mscore3 turns it into pdf.
Basically implements these 2 terminal commands in a script:

basic-pitch ./midi audio.mp3
mscore3 path/to/file.mid -o filename.pdf

USAGE: wav_midi_pdf_pipeline.py [-h] input_wav_path output_pdf_name

    Convert WAV to MIDI file and then to PDF.

    positional arguments:
    input_wav_path   Input wav full file path
    output_pdf_name  Output PDF file name, it will generate the file in sheets/

    optional arguments:
    -h, --help       show this help message and exit
"""

def convert_wav_to_pdf(wav_file, pdf_file):
	# same as terminal command: $ basic-pitch midi/ path/file.wav
    wav_to_midi_process = ["basic-pitch", "./midi/", wav_file]
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
    parser.add_argument("input_wav_path", help="Input wav full file path")
    parser.add_argument("output_pdf_name", help="Output PDF file name, it will generate the file in sheets/")
    args = parser.parse_args()

    wav_file = args.input_wav_path
    pdf_file =  args.output_pdf_name

    # Convert wav file to PDF
    convert_wav_to_pdf(wav_file, pdf_file)
