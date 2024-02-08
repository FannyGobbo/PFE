import pandas as pd
from midiutil import MIDIFile
"""
TODO:
"""

def create_midi_from_notes(note_list, output_file="output.mid", tempo=100):
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
        note_start /= 43447
        note_end /= 43447

        # Convert second time values to quarter notes
        # quarter note duration, get the tempo in bps (/60) then take the inverse
        quarter_note_duration_s = 1 / (TEMPO / 60)
        note_start_time_quarter_notes = note_start / quarter_note_duration_s
        note_duration_quarter_notes = (note_end - note_start) / quarter_note_duration_s
        # print(f'note start: {note_start_time_quarter_notes}\tduration: {note_duration_quarter_notes}\tpitch : {note_pitch}')

        # Add the note using the converted time values
        midi.addNote(track, 0, note_pitch, note_start_time_quarter_notes, note_duration_quarter_notes, volume=100)

    # Write the MIDI data to a file
    with open(output_file, "wb") as midi_file:
        midi.writeFile(midi_file)

if __name__ == '__main__':
    # Load the CSV file into a DataFrame
    df = pd.read_csv("../datasets/musicnet/musicnet/train_labels/1727.csv", delimiter=",")

    # Extract the required columns: start_time, end_time, note
    note_list = df[["start_time", "end_time", "note"]].values.tolist()

    # Print the first few rows to verify the data
    print(note_list[:5])  # Adjust the slice as per your need
    TEMPO = 100

    # Call the function to create the MIDI file
    create_midi_from_notes(note_list, "midi_from_notes.mid", tempo=TEMPO)