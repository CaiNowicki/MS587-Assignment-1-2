import sys
import os
from talky_files import convert_folder_batch

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Run batch conversion on <folder_path>")
    else:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            convert_folder_batch(folder_path)
        else:
            print(f"{folder_path} is not a valid directory")
