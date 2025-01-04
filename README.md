# Whisper tools
These are tools that use whisper, ffmpeg etc to process foriegn language videos

## Compile and build Whisper.cpp
```
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
cmake -B build
cmake --build build --config Release
./models/download-ggml-model.sh large-v3
```

create a simlink so the main script can find main
```
ln -s ./build/bin/whisper-cli main
```

## Install brew and then install ffmpeg
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install FFmpeg
```

## Create a CSV file to do conversion, example headers:
`Source_File_Path|Source_File_Name|Subject_Name|Subject_Tag|Campaign`

Folders will be created at the location of CSV file

## Run output splitter to create folders, convert audio, and run whisper and split to final versions
```
python whisper_output_splitter.py -a all -p ~/Pictures/hfunds/content/HearOurStories/Interviews_Dec_8_HearOurStories.csv
```

## For debugging you can run an individual stage with the -a flag and you can modify other flags as follows

### To split to 5 words per line, and only first 60 seconds of the project name matching 'Irina', only processing the SRT generation step.
```
python whisper_output_splitter.py -a create_srt -m 5 -n 1 -d 60  -f "Irina"  -p ~/Pictures/hfunds/content/HearOurStories/Interviews_Dec_8_HearOurStories.csv
```

## FAQ

### Translations are repeating over and over again.
https://github.com/openai/whisper/discussions/81
This happens when the model is unsure about the output (according to the compression_ratio_threshold and logprob_threshold settings). The most common failure mode is that it falls into a repeat loop, where it likely triggers the compression_ratio_threshold. The default setting tries temperatures 0, 0.2, 0.4, 0.6, 0.8, 1.0 until it gives up, at which it is less likely to be in a repeat loop but is also less likely to be correct.
