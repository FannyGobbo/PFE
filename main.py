import os



####################################################################################################### MAIN RUN FUNCTION

def run (filepath, id):
    # do split
    
    # do choice
    
    # do predict to midi
    
    # do midi to sheet => save to results/<id>/ 
    folder_path = os.path.join('results', id)
    os.makedirs(folder_path)
    
    # PLACEHOLDERS
    file_path = os.path.join(folder_path, "toto")
    with open(file_path, 'w') as f:
        pass
    
    file_path = os.path.join(folder_path, "tutu")
    with open(file_path, 'w') as f:
        pass
    
    return True
