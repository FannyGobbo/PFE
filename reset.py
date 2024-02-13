import os
import shutil
import sys

def reset_uploads():
    uploads_dir = 'uploads'
    for item in os.listdir(uploads_dir):
        item_path = os.path.join(uploads_dir, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)

def reset_results():
    results_dir = 'results'
    for item in os.listdir(results_dir):
        item_path = os.path.join(results_dir, item)
        if os.path.isfile(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
            
def reset_folders(directory):
    if directory == 'all':
        # Reset both uploads and results directories
        reset_uploads()
        reset_results()
    elif directory == 'upl':
        # Reset uploads directory
        reset_uploads()
    elif directory == 'res':
        # Reset results directory
        reset_results()
    else:
        print("Invalid argument\nUse 'upl' for upload folder, 'res' for results folder, or 'all' for both")


#######################################################################################################

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reset.py [all / res / upl]")
        sys.exit(1)
    
    directory = sys.argv[1]
    reset_folders(directory)
