import argparse
import itertools
import os
import re
from copy import copy
from enum import Enum
from pathlib import Path
from typing import List, Tuple

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize


class Action(Enum):
    ALL = 'ALL'
    CREATE_PROJECT = 'create_project'
    EXTRACT_AUDIO = 'extract_audio'
    EXTRACT_SRT = 'extract_srt'

def convert_srt_time_to_seconds(srt_time) -> float:
    hours, minutes, seconds, milliseconds = map(float, re.split('[:,]', srt_time))
    return hours * 3600 + minutes * 60 + seconds + milliseconds/1000

def convert_seconds_to_srt_time(seconds) -> str:
    _hours = int(seconds // 3600)
    _minutes = int((seconds % 3600) // 60)
    _seconds = int(seconds) % 60
    return f"{_hours:02}:{_minutes:02}:{_seconds:06.3f}".replace('.', ',')



def split_sentence_on_conjunction(sentence):
    """
    Drop a conjunction and split sentence into two parts
    And that's how small groups became, let's say, chat rooms in Pirețele and I was in all the chat rooms and if I could, if I needed, I would bring them.
    """
    conjunctions = {'and', 'but', 'or', 'nor', 'for', 'yet', 'so'}
    words = word_tokenize(sentence)

    if len(words) < 10:
        return [sentence]

    for i in range(4, len(words) - 4):
        if words[i] in conjunctions:
            first_part = ' '.join(words[:i]).strip()
            second_part = ' '.join(words[i:]).strip()
            return split_sentence_on_conjunction(first_part) + split_sentence_on_conjunction(second_part)

    return [sentence]


def split_text_into_chunks(text, total_duration):
    # Define the tokenizer to split on commas, periods, and question marks
    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'[^.?|,-]+[?!]?')
    # Future version to start allowing for numbers no to be split i.e. 50,000
    # tokenizer = RegexpTokenizer(r'([?!.|-]+|^\d+,^\d+|(?:[?!]))', gaps=True)

    # Anything but a split char, then capture.  Anything missing in capture is dropped
    sentences = tokenizer.tokenize(text)
    total_words = len(re.split(r'\s+', text))

    sentences = list(itertools.chain(*[split_sentence_on_conjunction(sent) for sent in sentences]))

    # Create the final list of chunks with their respective durations
    final_chunks = []
    current_chunks = []
    min_words = 2
    min_remaining_words = 3
    remaining_length = total_words

    for k, sent in enumerate(sentences):
        current_chunks.append(sent.strip())
        current_sent = ' '.join(current_chunks)
        current_length = len(re.split(r'\s+', current_sent))
        remaining_length -= current_length

        if current_length > min_words and remaining_length > min_remaining_words or k == len(sentences) - 1:

            calc_duration = total_duration * current_length / total_words
            #print(f"${calc_duration} = {total_duration} * {current_length} / {total_words}")
            current_sent = current_sent[0].upper() + current_sent[1:]
            final_chunks.append((current_sent.strip(), calc_duration))
            current_chunks = []

    #print(len(final_chunks), final_chunks)
    return final_chunks



def split_transcript(transcript, max_words=7) -> str:
    # Extract start and end times from the transcript
    # times = re.search(r'\[(.*?) --> (.*?)\]', transcript)

    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*)', re.MULTILINE )
    matches = pattern.findall(transcript)
    if not matches:
        raise ValueError("Invalid transcript format: missing time information")
    output = ""
    new_index = 0
    for match in matches:
        index, start_time_str, end_time_str, text = match
        start_time = convert_srt_time_to_seconds(start_time_str)
        end_time = convert_srt_time_to_seconds(end_time_str)

        chunks = split_text_into_chunks(text, end_time - start_time)

        # Calculate the start and end times for each chunk
        chunk_times = []
        timeline = 0
        for i in range(len(chunks)):
            chunk_times.append(
                            (start_time + timeline,
                            start_time + timeline + chunks[i][1]))
            timeline += chunks[i][1]


        # Construct the output
        for (chunk_txt, duration), times in zip(chunks, chunk_times):
            new_index += 1
            output += f"{new_index}\n"
            output += f"{convert_seconds_to_srt_time(times[0])} --> {convert_seconds_to_srt_time(times[1])}\n"
            output += f"{chunk_txt}\n\n"

    # Construct the output
    return output


def read_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    return content

# Custom action type to validate against allowed actions
def action_type(action):
    try:
        return Action(action)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid action: {action}. Allowed actions are: {', '.join([a.value for a in Action])}")


def get_project_names(project_csv_path, source_mpeg_folder, source_mpeg_name, subject_name, subject_tag, campaign):

    source_mpeg_file = os.path.join(source_mpeg_folder, source_mpeg_name)
    file_date = source_mpeg_name.split("_")[0]
    project_output_path = os.path.dirname(project_csv_path, f"{file_date}_{subject_tag}_{subject_name}_{campaign}")
    project_mpeg_file = f"{subject_name}_FULL.mpeg"
    project_audio_file = f"{subject_name}_FULL.wav"
    project_srt_file = f"{subject_name}_FULL.srt"


    return project_output_path, source_mpeg_file, project_mpeg_file, project_audio_file, project_srt_file

def create_project(project_csv_path):
    # Open CSV with columns Source_File_Path	Source_File_Name	Subject_Name	Subject_Tag	Campaign
    # Read each row and create a project folder with the following structure:
    with open(project_csv_path, 'r') as file:
        for row in file:
            source_mpeg_folder, source_mpeg_name, subject_name, subject_tag, campaign = row.strip().split(',')
            (project_output_path, source_mpeg_file, project_mpeg_file, project_audio_file, project_srt_file) = get_project_names(
                project_csv_path, source_mpeg_folder, source_mpeg_name, subject_name, subject_tag, campaign)
            os.makedirs(project_output_path)

            # Copy the source file to the project folder
            project_mpeg_path = os.path.join(project_output_path, project_mpeg_file)
            copy(source_mpeg_file, project_mpeg_path)

    return project_audio_file, project_mpeg_file, project_audio_file, project_srt_file

def extract_audio(mpeg_path, project_audio_file) -> str:
    # Takes a mpeg file and extracts audio in prepration for srt
    ffmpeg_1 = f"ffmpeg -i {mpeg_path} -vn -acodec copy {project_audio_file}.aac"
    ffmpeg_2 = f"ffmpeg -i {project_audio_file}.aac  -acodec pcm_s16le -ar 16000 {project_audio_file}.wav"

    os.system(ffmpeg_1)
    os.system(ffmpeg_2)
    return f"{project_audio_file}.wav"


def extract_srt(project_audio_file, project_srt_file, max_words):
    # Takes an audio file and create an optimized srt file
    audio_path =  Path(project_audio_file)
    whisper_cmd = "./whisper.cpp/main -l en -lpt 2.0 -osrt -m models/ggml-large-v3.bin -f ${audio_path.stem}.wav"
    os.system(whisper_cmd)
    srt_file_path = f"{audio_path.stem}.srt"
    file_content = read_file(srt_file_path)
    file_output = split_transcript(file_content, max_words=max_words)

    output_file_path = Path(srt_file_path)
    output_file_path = output_file_path.with_name(output_file_path.stem + '_optimized.srt')
    with output_file_path.open('w') as output_file:
        output_file.write(file_output)



def main():
    parser = argparse.ArgumentParser(description='Process a mpeg file source and creates a project file with SRT and AUDIO assests')

    parser.add_argument('-a', '--action', type=Action, choices=list(Action), help='The action type', required=True)
    parser.add_argument('-p', '--project_csv_file', type=str, help='The path to the project file to process', required=True)
    parser.add_argument('-m', '--max_words', type=int, default=7, help='Maximum number of words per chunk')
    args = parser.parse_args()

    nltk.download('punkt')
    nltk.download('punkt_tab')

    # Note running twice will result
    if args.action == Action.CREATE_PROJECT or Action.ALL:
        project_audio_file, project_mpeg_file, project_audio_file, project_srt_file = create_project(args.project_csv_file)

    if args.action == Action.EXTRACT_AUDIO or Action.ALL:
        wav_input_path = extract_audio(project_mpeg_file, project_audio_file)

    if args.action == Action.EXTRACT_AUDIO or Action.ALL:
        extract_audio(wav_input_path, project_srt_file)

if __name__ == '__main__':
    main()

