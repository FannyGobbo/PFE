import torch
import librosa
import argparse
import subprocess
import numpy as np
import torch.nn as nn
from midiutil import MIDIFile
"""
audio -> midi -> pdf
USAGE:
    python3 inference.py -h
"""

class TransformerModel(nn.Module):
    def __init__(self, input_size, output_size, num_layers=3, hidden_size=128, num_heads=2, dropout=0.1):
        super(TransformerModel, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        # Define transformer layers
        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=input_size,
            nhead=num_heads,
            dim_feedforward=hidden_size,
            dropout=dropout,
            batch_first=True 
        )
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)

        # Output layer
        self.output_layer = nn.Linear(input_size, output_size)

    def forward(self, src):
        output = self.transformer_encoder(src)
        output = self.output_layer(output)
        return output


def convert_to_notes(matrix, timestep):
    notes = []

    # Iterate through each row (note pitch) in the matrix
    for pitch_idx, pitch_row in enumerate(matrix):
        start_time = None

        # Iterate through each column (timestep) in the row
        for timestep_idx, value in enumerate(pitch_row):
            # if note is playing
            if value == 1:
                # Record the start time if not already set
                if start_time is None:
                    start_time = timestep_idx * timestep

                # if we're at the end of the row record the note
                if (timestep_idx + 1) == len(pitch_row):
                    end_time = (timestep_idx + 1) * timestep
                    pitch = pitch_idx
                    notes.append([round(start_time, 2), round(end_time, 2), pitch])
                    start_time = None

            # if we have a start_time AND value was not 1 (so 0) then record the note
            elif start_time is not None:
                end_time = timestep_idx * timestep
                pitch = pitch_idx
                notes.append([round(start_time, 2), round(end_time, 2), pitch])
                start_time = None

    # sort by start time
    sorted_notes = sorted(notes, key=lambda x: x[0])       
    return sorted_notes


def create_midi_from_notes(note_list, output_file_path, tempo=100):
    # Create a MIDIFile object
    midi = MIDIFile(1, deinterleave=False)

    # Add a track to the MIDI file
    track = 0
    time = 0
    midi.addTrackName(track, time, "Sample Track")

    # Set tempo (in beats per minute)
    midi.addTempo(track, time, tempo)

    # Set program number to change the instrument (40 is violi)
    # midi.addProgramChange(track, time, 0, 40)

    # Iterate over each note in the list of lists and add it to the MIDI file
    for note_start, note_end, note_pitch in note_list:
        # convert to seconds, WTF ??????
        # note_start /= 43447
        # note_end /= 43447

        # Convert second time values to quarter notes
        # quarter note duration, get the tempo in bps (/60) then take the inverse
        quarter_note_duration_s = 1 / (tempo / 60)
        note_start_time_quarter_notes = note_start / quarter_note_duration_s
        note_duration_quarter_notes = (note_end - note_start) / quarter_note_duration_s
        # print(f'note start: {note_start_time_quarter_notes}\tduration: {note_duration_quarter_notes}\tpitch : {note_pitch}')

        # Add the note using the converted time values
        midi.addNote(track, 0, note_pitch, note_start_time_quarter_notes, note_duration_quarter_notes, volume=100)

    # Write the MIDI data to a file
    with open(output_file_path, "wb") as midi_file:
        midi.writeFile(midi_file)
    print(f'MIDI file created : {output_file_path}')

    return output_file_path


def convert_audio_to_midi(input_file: str, output_folder_path: str):
    filename = input_file.split('.')[0].split('/')[-1]
    output_file_path = output_folder_path + '/' + filename + '.mid'

    # --- load audio --- 
    # --------------------------------------------------------
    audio_data, sr = librosa.load(input_file, sr=None)

    #  --- load model ---
    # --------------------------------------------------------
    # Create an instance of your model
    model = TransformerModel(input_size=128, output_size=128)
    # Load the model's state_dict
    model.load_state_dict(torch.load('trained_model.pth', map_location=torch.device('cpu')))

    # --- transform audio --- 
    # --------------------------------------------------------
    C0_freq = 16.35	# starting frequency
    sr = 44100      # Sampling rate
    TIMESTEP = 0.10 # Desired TIMESTEP in seconds
    hop_length = int(sr * TIMESTEP)
    cqt_data = librosa.cqt(audio_data, fmin=C0_freq, n_bins=125, sr=sr, hop_length=hop_length)
    zeros = np.zeros((3, cqt_data.shape[1]))
    cqt_data = np.vstack((cqt_data, zeros))
    cqt_transposed = np.abs(np.transpose(cqt_data))
    cqts_tensor = torch.tensor(cqt_transposed, dtype=torch.float32)

    # --- inference through model --- 
    # --------------------------------------------------------
    print('running inference...')
    with torch.no_grad():
        model.eval()  # Set the model to evaluation mode
        output = model(cqts_tensor)
    output_np = output.cpu().numpy() 
    output_np = np.transpose(output_np)
    NOTE_THRESHOLD = 0.5
    output_np = np.where(output_np > NOTE_THRESHOLD, 1, 0)

    # --- convert to midi ---
    # --------------------------------------------------------
    print('converting to note events...')
    note_events = convert_to_notes(output_np, 0.1)
    print('converting to midi...')
    midi_file = create_midi_from_notes(note_events, output_file_path)

    return midi_file


from music21 import midi
from music21 import stream
import os

def convert_midi_to_pdf(midi_file, pdf_file):    
    # Load MIDI file
    mf = midi.MidiFile()
    mf.open(midi_file)
    mf.read()
    mf.close()

    # Create a stream from MIDI file
    score = midi.translate.midiFileToStream(mf)

    # Create a temporary MusicXML file
    xml_file = "temp.musicxml"
    score.write("musicxml", xml_file)

    # Convert MusicXML to PDF using MuseScore
    os.system(f"musescore {xml_file} -o {pdf_file}")

    # Remove temporary MusicXML file
    os.remove(xml_file)
    print(f'created pdf from midi : {pdf_file}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert WAV to MIDI  file and then to PDF.")
    parser.add_argument("input_file_path", help="Input wav full file path")
    parser.add_argument("output_midi_name", help="Output midi file name")
    parser.add_argument("--split", action='store_true', default=False, help="will split the input file using spleeter (5 new files generated, bass.wav, drums.wav, other.wav, piano.wav, vocals.wav)")
    args = parser.parse_args()

    SPLIT = args.split
    input_file = args.input_file_path
    output_midi_name =  args.output_midi_name

    midi_file = convert_audio_to_midi(input_file, output_midi_name, SPLIT)
    pdf_file = midi_file.split('.')[0] + '.pdf' 
    subprocess.run(["mscore3", midi_file, "-o", pdf_file])
