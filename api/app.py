from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
from google.generativeai.types import generation_types
from flask import Flask, request, stream_with_context
import pytube
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

def get_video_id(uri: str) -> str:
    return pytube.extract.video_id(uri)

def list_transcripts(video_id: str):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    generated = []
    manual = []
    # iterate over all available transcripts
    for transcript in transcript_list:
        if transcript.is_generated:
            generated.append(transcript.language_code)
        else:
            manual.append(transcript.language_code)
    return {"generated": generated, "manual": manual}

def get_default_language(transcripts_list) -> str:
    generated = transcripts_list.get('generated', [])
    manual = transcripts_list.get('manual', [])
    assert generated or manual, "No transcripts found"
    if not generated:
        if manual:
            return manual[0]
    return generated[0]
    

def transcript_to_text(transcript) -> str:
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)
    return text_formatted

def get_transcript(video_id: str, language: str = None):
    available_transcripts = list_transcripts(video_id)
    if not language:
        language = get_default_language(available_transcripts)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages = [language])
    return transcript

def summarize_text(video_id: str):
    transcript = get_transcript(video_id)
    genai.configure(api_key=os.getenv('GOOGLE_AI_API_KEY'))
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = 'Summarize this transcript and structure it into chapters. Write the summary and chapters in the input language. Format output as: {"chapters": ["title": "CHAPTER_TITLE", "start": "START_TIMESTAMP", "end": "END_TIMESTAMP"}], "summary": "VIDEO_SUMMARY"}.'
    response = model.generate_content(
        f'{prompt}. Transcript: {transcript}',
        generation_config= generation_types.GenerationConfig(
            response_mime_type = 'application/json',
            candidate_count = 1
        ),
        stream = True
    )
    for chunk in response:
        yield chunk.text

@app.route("/", methods=["GET"])
def home():
    return 'Hola caracola'

@stream_with_context
@app.route("/<path:path>", methods=["GET"])
def summarize(path):
    uri = request.full_path.strip("/")
    try:
        video_id = get_video_id(uri)
    except pytube.exceptions.RegexMatchError:
        return "Invalid URI", 400
    return summarize_text(video_id)