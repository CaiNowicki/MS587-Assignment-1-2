import os
import sys
import tkinter as tk
from tkinter import filedialog
from gtts import gTTS
import fitz  # PyMuPDF
from mutagen.mp3 import MP3
import threading
import re


# Define the main app class
class TalkyFiles(tk.Tk):
    def __init__(self):
        super().__init__()

        # Improved UX: Set window title and size
        self.title('TalkyFiles - Convert to Audio')
        self.geometry('400x220')

        # Create and place widgets
        self.create_widgets()

    def create_widgets(self):
        # Label for instructions
        self.label = tk.Label(self, text="Select a PDF or Text file to convert to audio")
        self.label.pack(pady=10)

        # Button to select PDF/Text file
        self.select_button = tk.Button(self, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

        # Label to display conversion progress 
        self.progress_label = tk.Label(self, text="")
        self.progress_label.pack(pady=5)

    def select_file(self):
        # File dialog to select PDF or TXT
        filetypes = [("PDF files", "*.pdf"), ("Text files", "*.txt")]
        self.file_path = filedialog.askopenfilename(defaultextension=".pdf", filetypes=filetypes)

        if self.file_path:
            self.select_button['state'] = 'disabled'  # Disable button during conversion
            self.thread = threading.Thread(target=self.convert_to_audio)
            self.thread.start()

    def sanitize_text(self, text):
        """Sanitize the text to handle special characters."""
        return re.sub(r'[^\x20-\x7E]+', '', text)


    def convert_to_audio(self):
        print("Inside convert_to_audio method")
        try:
            print("Inside Try block")
            self.progress_label['text'] = "Converting file to audio..."

            filename, extension = self.file_path.rsplit('.', 1)  # Get filename and extension
            print(f"Processing file {filename}")
            if extension.lower() == 'pdf':
                # PDF conversion process (same as before)
                doc = fitz.open(self.file_path)
                text = ""
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    text += page.get_text()
                doc.close()

            elif extension.lower() == 'txt':
                # Text file conversion
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

            else:
                raise ValueError("Unsupported file type. Please select a PDF or TXT file.")
            sanitized_text = self.sanitize_text(text)
            tts = gTTS(sanitized_text, lang='en')  
            audio_file = filename + '.mp3'  # Use the same base filename
            tts.save(audio_file)

                    # Verify if file exists after saving
            if os.path.isfile(audio_file):
                print(f"Audio file saved at: {audio_file}")
            else:
                print(f"Failed to save audio file at: {audio_file}")

            audio = MP3(audio_file)
            audio_length = audio.info.length

            # Success message now includes file type
            self.progress_label['text'] = f"Conversion Complete!\nAudio File: {audio_file}\nRuntime: {audio_length:.2f} seconds"

        except Exception as e:
            self.progress_label['text'] = f"Conversion Failed: {e}"
        finally:
            self.select_button['state'] = 'normal'  # Re-enable button   
            print("inside the finally exception")

# added function to convert without using the GUI
def convert_folder_batch(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.pdf', '.txt')): # check all the files in the folder to see if they are txt or pdf
            file_path = os.path.join(folder_path, filename)
            try:
                talky_files_instance = TalkyFiles()
                talky_files_instance.convert_to_audio(file_path)
                print(f"Converted: {filename}")
            except Exception as e:
                print(f"Failed to convert {filename}. Error: {e}")


# Run the app
if __name__ == "__main__":
    if len(sys.argv) >1: # if it's a folder, use the batch function
        folder_path = sys.argv[1]
        convert_folder_batch(folder_path)
    else:
        app = TalkyFiles()
        app.mainloop()