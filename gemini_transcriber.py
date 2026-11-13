from dotenv import load_dotenv
from google import genai

def gemini_extract_srt(audio_path, gemini_model):
    load_dotenv()
    client = genai.Client()

    uploaded_file = client.files.upload(file=audio_path)
    print("Uploaded audio file to Gemini successfully")

    prompt = (
        "Transcribe the spoken audio and translate it into English"
        "Only include the translated English, not the original text"
        "Output strictly in valid SRT subtitle format (index, 00:00:00,000 --> 00:00:00,000, and text). "
        "Do not include conversational preamble or markdown backticks."
    )

    response = client.models.generate_content(
        model=gemini_model, contents=[uploaded_file, prompt]
    )

    srt_file_path = f"{audio_path}.srt"
    with open(srt_file_path, "w") as f:
        f.write(response.text.strip())