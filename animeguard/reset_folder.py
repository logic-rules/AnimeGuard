import os
import shutil
def reset_folder(folder):
    shutil.rmtree(folder, ignore_errors=True) # deletes the folder as a whole
    os.makedirs(folder, exist_ok=True) # brand-new folder