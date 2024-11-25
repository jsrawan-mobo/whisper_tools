import argparse
import itertools
import re
from pathlib import Path
from typing import List, Tuple

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize



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
            print(f"${calc_duration} = {total_duration} * {current_length} / {total_words}")
            current_sent = current_sent[0].upper() + current_sent[1:]
            final_chunks.append((current_sent.strip(), calc_duration))
            current_chunks = []

    print(len(final_chunks), final_chunks)
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

def main():
    parser = argparse.ArgumentParser(description='Read a file and store its content in a variable.')
    parser.add_argument('-s', '--srt_file', type=str, help='The path to the file to be read', required=True)
    parser.add_argument('-m', '--max_words', type=int, default=7, help='Maximum number of words per chunk')
    args = parser.parse_args()

    nltk.download('punkt')
    nltk.download('punkt_tab')

    file_content = read_file(args.srt_file)
    file_output = split_transcript(file_content, max_words=args.max_words)

    output_file_path = Path(args.srt_file)
    output_file_path = output_file_path.with_name(output_file_path.stem + '_optimized.srt')
    with output_file_path.open('w') as output_file:
        output_file.write(file_output)


if __name__ == '__main__':
    main()

