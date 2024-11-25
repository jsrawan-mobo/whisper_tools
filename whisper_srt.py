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
