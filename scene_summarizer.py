import argparse
import os
import pprint
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

def read_srt_file_segments(file_path):
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

def analyze_emotions(segments):
    text = "\n".join([f"{seg['start_time']}: {seg['text']}" for seg in segments])
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

def analyze_questions(segments, question):
    text = "\n".join([f"{seg['start_time']} --> {seg['end_time']}: {seg['text']}" for seg in segments])
    # text = "\n".join([f"{seg['start_time']}: {seg['text']}" for seg in segments])
    prompt_text = (
       f"{question}"
        f"{text}"
    )
    client = OpenAI()
    completion = client.chat.completions.create(
        model=OPENAI_API_MODEL,
        messages=[
            {"role": "system", "content": "You are an transcription expert"},
            {"role": "user", "content": prompt_text}
        ],
        max_tokens=500,
        temperature=0.5
    )
    ##print(completion.choices[0].message)
    # print(completion.choices[0])
    print(completion.choices[0].message.content)
    # return completion.choices[0].message

# Function to generate an image using OpenAI API
def generate_image_from_text(prompt_text, image_size="1024x1792"):
    client = OpenAI()
    response = client.images.generate(
        api_key=OPENAI_API_KEY,
        prompt=prompt_text,
        n=1,
        size=image_size
    )
    return response["data"][0]["url"]

def load_srt_files_to_segments(srt_folder_path, number):
    srt_files = [f for f in os.listdir(srt_folder_path) if f.endswith('.srt')]
    if number:
        srt_files = srt_files[0:number]
    for srt_file in srt_files:
        srt_path = os.path.join(srt_folder_path, srt_file)
        segments = read_srt_file_segments(srt_path)
        return segments

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
    parser.add_argument('-p', '--prompt', type=int, help='The prompt number to run', required=False)
    parser.add_argument('-n', '--number', type=int, help='Max number of transcripts to import', required=False, default=None)



## add argument that pastes in a prompt number and run that prompt
## arguments: -p 1 or -p 2
## put in array called prompts
## help command
## create question, create a function "I want to ask prompt 1" and run that prompt (ending with :question= )

    prompts = [
        "Can you identify when a question is asked in the script and what the answer is.\n\n"
        "Format the output with timestamp\nQuestion: Answer: \n\n"
    ]
    def print_prompts():
        for index, prompt in enumerate(prompts):
            print(f"{index}: {prompt}")


    ## input from user
    args = parser.parse_args()

    # Note running twice will result
    if args.action in [Action.LOAD_SRT]:
        try:
            #run_open_ai_completion_as_role()
            segments = load_srt_files_to_segments(args.folder, args.number)
            emotional_segments = analyze_emotions(segments)
            print("\nDetected Emotional Segments:\n")
            pprint.pprint(emotional_segments.to_dict()['content'])
        except Exception as e:
            print(e)

    # if ali.action
    # if args.action in [Action.ASK_QUESTION]:
    #     try:
    #         segments = load_srt_files_to_segments(args.folder, args.model)
    #         qa_segments = analyze_questions(segments,question)
    #         print("\nQuestions and Answers Detected:\n")
    #         pprint.pprint(qa_segments)
    #     except Exception as e:
    #         print(f"Error during ASK_QUESTION: {e}")

# If user inputs a prompt number, replace the question with the prompt number in the array
    try:
        askPrompts = input("choose a prompt number:")
        print_prompts()

        segments = load_srt_files_to_segments(args.folder, args.number)
        qa_segments = analyze_questions(segments, prompts[int(askPrompts)])
        print("\nQuestions and Answers Detected:\n")
        # pprint.pprint(qa_segments)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        print(Exception, e)
        print(f"Error during ASK_QUESTION: {e}")



    # if args.action in [Action.ASK_QUESTION]:
    #     pass



if __name__ == '__main__':
    main()


