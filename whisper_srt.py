import faster_whisper
import math
from tqdm import tqdm

model = faster_whisper.WhisperModel("large-v3", device="cuda")

def convert_to_hms(seconds: float) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = math.floor((seconds % 1) * 1000)
    output = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"
    return output

def convert_seg(segment: faster_whisper.transcribe.Segment) -> str:
    return f"{convert_to_hms(segment.start)} --> {convert_to_hms(segment.end)}\n{segment.text.lstrip()}\n\n"

segments, info = model.transcribe("../../audio/African-french-interview-food-16K.WAV")

full_txt = []
timestamps = 0.0  # for progress bar
with tqdm(total=info.duration, unit=" audio seconds") as pbar:
    for i, segment in enumerate(segments, start=1):
        full_txt.append(f"{i}\n{convert_seg(segment)}")
        pbar.update(segment.end - timestamps)
        timestamps = segment.end
    if timestamps < info.duration: # silence at the end of the audio
        pbar.update(info.duration - timestamps)

with open("../../audio/African-french-interview-food-16K.srt", mode="w", encoding="UTF-8") as f:
    f.writelines(full_txt)


## Args/Kwargs.


## Ali's code 1) Add (extract) Prompts

from dotenv import load_dotenv
import os
import openai
from docx import Document  # For .docx files
from PyPDF2 import PdfReader  # For .pdf files

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL")


# Set your OpenAI API key
##openai.api_key = os.getenv("OPENAI_API_KEY")



# Function to read text from a plain text (.txt) file
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Function to read text from a Word (.docx) file
def read_docx_file(file_path):
    doc = Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


# Function to read text from a PDF file
def read_pdf_file(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


# Function to process multiple files and extract their contents
def extract_text_from_files(files):
    all_text = ""
    for file_path in files:
        if file_path.endswith('.txt'):
            all_text += read_txt_file(file_path) + "\n\n"
        elif file_path.endswith('.docx'):
            all_text += read_docx_file(file_path) + "\n\n"
        elif file_path.endswith('.pdf'):
            all_text += read_pdf_file(file_path) + "\n\n"
        else:
            print(f"Unsupported file format: {file_path}")
    return all_text


# Function to interact with OpenAI GPT-4 API and ask for prompts
def generate_prompts_from_text(text):
    prompt = (
        "You are a helpful assistant. Based on the following content, "
        "summarize and suggest potential prompts for discussion or analysis: \n\n"
        f"{text}\n\n"
        "Please list the suggested prompts in bullet points."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant specialized in summarization and prompt generation."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["choices"][0]["message"]["content"]


# Main function
def main():
    # Step 1: Specify the files to process
    files = [
        "example1.txt",
        "example2.docx",
        "example3.pdf"
    ]

    # Step 2: Extract text from the files
    extracted_text = extract_text_from_files(files)
    print("Extracted text from files successfully!")

    # Step 3: Send the extracted text to GPT-4 for prompt generation
    print("Generating prompts from GPT-4...")
    prompts = generate_prompts_from_text(extracted_text)

    # Step 4: Display the generated prompts
    print("\nGenerated Prompts:\n")
    print(prompts)


if __name__ == "__main__":
    main()






## Ali code 2) Add (Init) Prompts to Load an Existing GPT Model
def init_gpt_model(api_key, model, initial_prompt):
    import openai
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": initial_prompt}
        ]
    )
    return response

##load API
api_key = os.getenv('OPENAI_API_KEY')
model = os.getenv('OPENAI_API_MODEL', 'gpt-4')
initial_prompt = "You are a helpful assistant specialized in data extraction and analysis."

# Initialize GPT model with the prompt
response = init_gpt_model(api_key, model, initial_prompt)
print(response["choices"][0]["message"]["content"])






## Ali code 3)Integrate Google Drive API for clips

##step1 to install the library: pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
##step2 to Google Cloud Console




