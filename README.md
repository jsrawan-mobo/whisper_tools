### Compile and build Whisper.cpp
brew install FFmpeg
make
./models/download-ggml-model.sh large-v3-turbo


### Get Audio File Ready

ffmpeg -i ../../audio/African-french-interview-food-16K-Short.m4a -acodec pcm_s16le -ar 16000 ../../audio/African-french-interview-food-16K-Short.wv



### Convert Audio to English 

```
./main -l en -ot 420000 -ml 60  -m models/ggml-large-v3.bin -f ../../audio/20241107_170246_slava_final.wav -osrt
```

```
./main -tr -l en -lpt 2.0  -ot 10000 -osrt -m models/ggml-large-v3-turbo.bin -f ~/Pictures/hfunds/campaigns/Hear_Our_Stories/Olga_Full_Interview/20241107_173956_olga_final.wa
```

https://github.com/openai/whisper/discussions/81
This happens when the model is unsure about the output (according to the compression_ratio_threshold and logprob_threshold settings). The most common failure mode is that it falls into a repeat loop, where it likely triggers the compression_ratio_threshold. The default setting tries temperatures 0, 0.2, 0.4, 0.6, 0.8, 1.0 until it gives up, at which it is less likely to be in a repeat loop but is also less likely to be correct.
### 
