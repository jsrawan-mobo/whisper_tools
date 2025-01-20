import argparse
import os
from os.path import join, dirname

import pysrt
from enum import Enum
from openai import OpenAI

from dotenv import load_dotenv

# Example usage
dotenv_path = join(dirname(__file__), '.env')
load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_MODEL = os.environ.get("OPENAI_API_MODEL")
print(OPENAI_API_KEY)
print(OPENAI_API_MODEL)


from whisper_output_splitter import read_projects, create_project, extract_audio, extract_srt

def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content


def run_open_ai_completion_as_role(role="user", content="write a haiku about ai"):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        store=True,
        messages=[
            {"role": role, "content": content}
        ]
    )
    print(completion.choices[0].message)




def read_srt_file(file_path):
    subs = pysrt.open(file_path)
    segments = []

    for sub in subs:
        segments.append({
            "index": sub.index,
            "start_time": sub.start.to_time(),  # Convert timestamp to time object
            "end_time": sub.end.to_time(),
            "text": sub.text.replace('\n', ' ')  # Clean up multiline text
        })

    return segments


def analyze_emotions(text):
    prompt_text = (
        "Analyze the following text and identify emotional segments such as sadness, joy, fear, anger, and hope. "
        "Return only the emotional segments along with their corresponding emotions:\n\n"
        f"{text}"
    )
    client = OpenAI()
    completion = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert emotion detector."},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=500,
        temperature=0.5
    )
    return completion.choices[0].message


def load_srt_files_to_model(srt_folder_path, saved_model_name):
    srt_files = [f for f in os.listdir(srt_folder_path) if f.endswith('.srt')]
    for srt_file in srt_files:
        srt_path = os.path.join(srt_folder_path, srt_file)
        segments = read_srt_file(srt_path)

        subtitle_text = "\n".join([f"{seg['start_time']}: {seg['text']}" for seg in segments])
        emotional_segments = analyze_emotions(subtitle_text)
        print("\nDetected Emotional Segments:\n", emotional_segments)

        # Use OpenAI completions
        client = OpenAI()
        # completion = client.chat.completions.create(
        #     model=OPENAI_API_MODEL,
        #     store=True,
        #     messages=[
        #         {"role": "user", "content": "Can you load the SRT file which has 3 rows for #index#timestamp#text#"}
        #     ]
        # )
        # print(completion.choices[0].message)

        # file = client.files.create(file=open(srt_path, "rb"), purpose="batch")
        #
        # completion = client.chat.completions.create(
        #     model=OPENAI_API_MODEL,
        #     store=True,
        #     messages=[
        #         {"role": "system", "content": "You are assistant that can read and analyze this file SRT file which has 3 rows for #index#timestamp#text#"},
        #         {"role": "user", "content": f"Load  {file.id}"}]
        # )
        # print(completion.choices[0].message)
        break

# # Function to generate an image using OpenAI API
# def generate_image_from_text(api_key, prompt_text, image_size="1024x1792"):
#     response = openai.Image.create(
#         api_key=api_key,
#         prompt=prompt_text,
#         n=1,
#         size=image_size
#     )
#     return response["data"][0]["url"]


class Action(Enum):
    ALL = 'all'
    LOAD_SRT = 'load_srt'
    INIT_GPT = 'init_gpt'
    EXTRACT_SCENE = 'extract_scene'
    ASK_QUESTION = 'ask_question'


def main():
    parser = argparse.ArgumentParser(description='Process a mpeg file source and creates a project file with SRT and AUDIO assests')
    parser.add_argument('-a', '--action', type=Action, choices=list(Action), help='The action type', required=True)
    parser.add_argument('-f', '--folder', type=str, help='The path to the SRT files', required=True)
    parser.add_argument('-l', '--model', type=str, default="srt_scenes_model_v1", help='GPT Model to load or init', required=False)

    args = parser.parse_args()

    # Note running twice will result
    if args.action in [Action.LOAD_SRT]:
            try:
                #run_open_ai_completion_as_role()
                load_srt_files_to_model(args.folder, args.model)

            except Exception as e:
                print(e)

    if args.action in [Action.ASK_QUESTION]:
        pass



if __name__ == '__main__':
    main()