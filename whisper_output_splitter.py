import argparse
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


# def split_text_into_chunks(text, total_duration) -> List[Tuple[str, float]]:
#     # https://stackoverflow.com/questions/61757407/how-to-ignore-punctuation-in-between-words-using-word-tokenize-in-nltk
#
#     from nltk.tokenize import RegexpTokenizer
#
#     # punctuation = r',\.!\?]?'
#     # regexp_tokenizer = RegexpTokenizer(r'\w+' + punctuation + r'\w+?|[^\s]+?', False)
#     # regexp_tokenizer = RegexpTokenizer(r'\w+|\$[\d\.]+|[\.?]') # Any word, including special cases followed by a seprator
#     #
#     # sentences = regexp_tokenizer.tokenize(text)
#
#     # sentences = sent_tokenize(text)
#
#     print(sentences)
#     # Calculate the duration per sentence
#     duration_per_sentence = total_duration / len(sentences)
#
#     final_chunks = []
#     for k, sentence in enumerate(sentences):
#         # Tokenize the sentence into words
#         words = word_tokenize(sentence)
#
#         # Split the sentence into chunks by commas with minimum chunk len
#         min_chunk_words = 2
#         chunk = []
#         for word in words:
#             chunk.append(word)
#             if word in [',', '.', '!', '?']: #and len(chunk) >= min_chunk_words:
#                 print(f"{sentence}--{k}")
#                 final_chunks.append((' '.join(chunk), duration_per_sentence))
#                 chunk = []
#
#         # Add any remaining words as a chunk
#         if chunk:
#             final_chunks.append((' '.join(chunk), duration_per_sentence))
#
#     return final_chunks


def split_text_into_chunks(text, total_duration):
    # Define the tokenizer to split on commas, periods, and question marks

    from nltk.tokenize import RegexpTokenizer
    tokenizer = RegexpTokenizer(r'[^,?.|]+[,?.!]?') # Anything but a split char, then capture

    # Tokenize the text into chunks
    sentences = tokenizer.tokenize(text)

    # Calculate the duration per chunk
    duration_per_chunk_avg = total_duration / len(sentences)
    total_words = len(re.split('\s+', text))

    # Create the final list of chunks with their respective durations
    final_chunks = []
    for sent in sentences:
        calc_duration = duration_per_chunk_avg * len(re.split('\s+', sent))/total_words
        final_chunks.append((sent.strip(), calc_duration))

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
        chunk_times = [(start_time + (chunks[i-1][1] if i > 0 else 0),
                        start_time + chunks[i][1]) for i in range(len(chunks))]

        # Construct the output
        for (chunk_txt, duration), times in zip(chunks, chunk_times):
            new_index += 1
            output += f"{new_index}\n{convert_seconds_to_srt_time(times[0])} --> {convert_seconds_to_srt_time(times[1])}\n{chunk_txt.strip()}\n\n"

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

