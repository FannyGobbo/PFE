import os
import inference
from inference import convert_audio_to_midi

def run (filepath, id):
    ######################## INIT
    # create folders
    res_folder_path = os.path.join('results', id)
    os.makedirs(res_folder_path)
    midi_folder_path = os.path.join(res_folder_path, 'midi')
    os.makedirs(midi_folder_path) 
    split_folder_path = os.path.join(res_folder_path, 'splited-sources')
    os.makedirs(split_folder_path)

    # PLACEHOLDER
    os.system(f"cp temp/1727.wav {split_folder_path}")
    
    ######################## SPLITTER
    
    
    

    
    ######################## TRACK TO MIDI
    
    for file in os.listdir(split_folder_path):
        filepath = os.path.join(split_folder_path, file)
        convert_audio_to_midi(filepath, midi_folder_path)
    
    ######################## MIDI TO SHEET MUSIC 
    
    # PLACEHOLDER 
    # os.system(f"cp temp/out.midi {midi_folder_path}")
    
    for file in os.listdir(midi_folder_path):
        file_path = os.path.join(midi_folder_path, file)
        if os.path.isfile(file_path):
            filename = os.path.basename(file)
            pdf_filename = os.path.splitext(filename)[0] + '.pdf'
            pdf_filepath = os.path.join(res_folder_path, pdf_filename)
            os.system(f"mscore3 {file_path} -o {pdf_filepath} 2>> /dev/null")
    
    # PLACEHOLDER
    file_path = os.path.join(res_folder_path, "toto")
    with open(file_path, 'w') as f:
        pass
    
    # PLACEHOLDER
    file_path = os.path.join(res_folder_path, "tutu")
    with open(file_path, 'w') as f:
        pass
