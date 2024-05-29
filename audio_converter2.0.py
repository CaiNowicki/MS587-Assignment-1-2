# code in this file mostly borrowed from
# https://medium.com/coinmonks/how-to-convert-pdfs-into-audiobooks-using-openais-text-to-speech-api-f7a3b589babe
# with some updates to run as .py script instead of in a Jupyter notebook

import pdfplumber
import re
from pathlib import Path
import openai
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from moviepy.editor import concatenate_audioclips, AudioFileClip
#load variables from .env file
load_dotenv()

def pdf_to_markdown(pdf_path):
    print("Debug - opening the PDF and converting it to markdown")
    # Open the PDF file at the given path
    with pdfplumber.open(pdf_path) as pdf:
        markdown_content = ""
        # Loop through each page in the PDF
        for page in pdf.pages:
            # Extract text from each page
            text = page.extract_text()
            if text:
                # Format the text with basic Markdown: double newline for new paragraphs
                markdown_page = text.replace('\n', '\n\n')
                # Add a separator line between pages
                markdown_content += markdown_page + '\n\n---\n\n'

        return markdown_content

def markdown_to_plain_text(markdown_text):
    print("Debug - markdown to plain text")
    # Remove Markdown URL syntax ([text](link)) and keep only the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown_text)

    # Remove Markdown formatting for bold and italic text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold with **
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic with *
    text = re.sub(r'\_\_([^_]+)\_\_', r'\1', text)  # Bold with __
    text = re.sub(r'\_([^_]+)\_', r'\1', text)      # Italic with _

    # Remove Markdown headers, list items, and blockquote symbols
    text = re.sub(r'#+\s?', '', text)  # Headers
    text = re.sub(r'-\s?', '', text)   # List items
    text = re.sub(r'>\s?', '', text)   # Blockquotes

    return text

# text to audio converter will only handle up to 4096 characters
# longer files need to be chunked

def split_text(text, max_chunk_size=4000):
    print("Debug - chunking text")
    chunks = []  # List to hold the chunks of text
    current_chunk = ""  # String to build the current chunk

    # Split the text into sentences and iterate through them
    for sentence in text.split('.'):
        sentence = sentence.strip()  # Remove leading/trailing whitespaces
        if not sentence:
            continue  # Skip empty sentences

        # Check if adding the sentence would exceed the max chunk size
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + "."  # Add sentence to current chunk
        else:
            chunks.append(current_chunk)  # Add the current chunk to the list
            current_chunk = sentence + "."  # Start a new chunk

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def text_to_speech(input_text, output_file, model="tts-1-hd", voice="nova"):
    print("Debug - running text to speech conversion model")
    # use OpenAI to convert the file to audio
    # Initialize the OpenAI client
    api_key = os.environ.get("OPENAI_API_KEY")
    client = openai.OpenAI()
    client.api_key = api_key

    # Make a request to OpenAI's Audio API with the given text, model, and voice
    response = client.audio.speech.create(
        model=model,      # Model for text-to-speech quality
        voice=voice,      # Voice type
        input=input_text  # The text to be converted into speech
    )

    # Define the path for the output audio file
    speech_file_path = Path(output_file)

    # Stream the audio response to the specified file
    response.stream_to_file(speech_file_path)

    # Print confirmation message after saving the audio file
    print(f"Audio saved to {speech_file_path}")

def convert_chunks_to_audio(chunks, output_folder):
    print("Debug - convert each chunk to audio")
    audio_files = []  # List to store the paths of generated audio files

    # Iterate over each chunk of text
    for i, chunk in enumerate(chunks):
        # Define the path for the output audio file
        output_file = os.path.join(output_folder, f"chunk_{i+1}.mp3")

        # Convert the text chunk to speech and save as an audio file
        text_to_speech(chunk, output_file)

        # Append the path of the created audio file to the list
        audio_files.append(output_file)

    return audio_files  # Return the list of audio file paths

def combine_audio_with_moviepy(folder_path, output_file):
    print("Debug - combine chunked audio into single file")
    audio_clips = []  # List to store the audio clips

    # Iterate through each file in the given folder
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith('.mp3'):
            # Construct the full path of the audio file
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_path}")

            try:
                # Create an AudioFileClip object for each audio file
                clip = AudioFileClip(file_path)
                audio_clips.append(clip)  # Add the clip to the list
            except Exception as e:
                # Print any errors encountered while processing the file
                print(f"Error processing file {file_path}: {e}")

    # Check if there are any audio clips to combine
    if audio_clips:
        # Concatenate all the audio clips into a single clip
        final_clip = concatenate_audioclips(audio_clips)
        # Write the combined clip to the specified output file
        final_clip.write_audiofile(output_file)
        print(f"Combined audio saved to {output_file}")
    else:
        print("No audio clips to combine.")

# Define the input PDF file path
pdf_path = 'Animorphs/PDF/Ani 02.0 - The Visitor - K. A. Applegate.pdf'

# Convert PDF to Markdown
markdown_content = pdf_to_markdown(pdf_path)

# Convert Markdown to plain text
plain_text = markdown_to_plain_text(markdown_content)

# Split the plain text into smaller chunks (if needed)
chunks = split_text(plain_text)

# Convert chunks of text to audio files
output_folder = 'output/audio'
audio_files = convert_chunks_to_audio(chunks, output_folder)

# Combine audio files into a single audio file (if needed)
output_file = 'output/combined_audio_vol2.mp3'
combine_audio_with_moviepy(output_folder, output_file)