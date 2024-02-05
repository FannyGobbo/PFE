import pandas as pd
from midiutil import MIDIFile

# Load the CSV file into a DataFrame
df = pd.read_csv("../datasets/musicnet/musicnet/train_labels/1727.csv", delimiter=",")

# Extract the required columns: start_time, end_time, note
note_list = df[["start_time", "end_time", "note"]].values.tolist()

# Print the first few rows to verify the data
print(note_list[:5])  # Adjust the slice as per your need

def create_midi_from_notes(note_list, output_file="output.mid", tempo=120):
    # Create a MIDIFile object
    midi = MIDIFile(1, deinterleave=False)

    # Add a track to the MIDI file
    track = 0
    time = 0
    midi.addTrackName(track, time, "Sample Track")

    # Set tempo (in beats per minute)
    midi.addTempo(track, time, tempo)

    # Iterate over each note in the list of lists and add it to the MIDI file
    for note_start, note_end, note_pitch in note_list:
        # convert to seconds, WTF ?????? pourquoi c'est des 100_000ème de seconde
        note_start /= 100_000
        note_end /= 100_0000

        # Convert second time values to quarter notes
        # 120 bpm = 2bps = 1b per 0.5 seconds (beat = quarter note)
        quarter_note_duration_s = 0.5
        note_start_time_quarter_notes = note_start / quarter_note_duration_s
        note_duration_quarter_notes = (note_end - note_start) / quarter_note_duration_s
        # print(f'note start: {note_start_time_quarter_notes}\tduration: {note_duration_quarter_notes}\tpitch : {note_pitch}')

        # Add the note using the converted time values
        midi.addNote(track, 0, note_pitch, note_start_time_quarter_notes, note_duration_quarter_notes, volume=100)


    # Write the MIDI data to a file
    with open(output_file, "wb") as midi_file:
        midi.writeFile(midi_file)


# Call the function to create the MIDI file
create_midi_from_notes(note_list, "midi_from_notes.mid")