import re

def split_transcript(transcript, max_words=7):
    # Extract start and end times from the transcript
    times = re.search(r'\[(.*?) --> (.*?)\]', transcript)
    start_time = float(times.group(1))
    end_time = float(times.group(2))
    
    # Extract the words from the transcript
    words = re.findall(r'\b\w+\b', transcript)
    num_words = len(words)
    
    # Calculate the total time and time per word
    total_time = end_time - start_time
    time_per_word = total_time / num_words
    
    # Split the words into chunks
    chunks = [words[i:i+max_words] for i in range(0, len(words), max_words)]
    
    # Calculate the start and end times for each chunk
    chunk_times = [(start_time + i*max_words*time_per_word, 
                    start_time + (i+1)*max_words*time_per_word) for i in range(len(chunks))]
    
    # Construct the output
    output = ""
    for chunk, times in zip(chunks, chunk_times):
        output += f"[{times[0]:.3f} --> {times[1]:.3f}] {' '.join(chunk)}\n"
    
    return output

#transcript = "[00:00.000 --> 00:04.320] The example text provided is split into chunks with the specified maximum word limit, and interpolated times are calculated based on the assumption of 150 words per minute."
#print(split_transcript(transcript))
