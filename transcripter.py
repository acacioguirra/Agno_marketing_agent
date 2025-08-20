import os
import glob
import subprocess
from groq import Groq
from dotenv import load_dotenv
import tempfile
import json 

load_dotenv()
VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.webm')

def is_video_file(filename):
    return filename.lower().endswith(VIDEO_EXTENSIONS)

def extract_audio(video_path, output_dir):
    audio_path = os.path.join(output_dir, os.path.splitext(os.path.basename(video_path))[0] + '.wav')
    subprocess.run([
        'ffmpeg', '-y', '-i', video_path,
        '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', audio_path
    ], check=True)
    return audio_path

def transcribe_audio(audio_path):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    with open(audio_path, 'rb') as audio_file:
        return client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            response_format="text"
        )

def build_transcripts_json(transcripts_dir, output_json):
    data = {}
    for subfolder in os.listdir(transcripts_dir):
        subfolder_path = os.path.join(transcripts_dir, subfolder)
        if os.path.isdir(subfolder_path):
            data[subfolder] = {}
            for filename in os.listdir(subfolder_path):
                if filename.endswith('.txt'):
                    file_path = os.path.join(subfolder_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        transcript_text = f.read()
                    key = os.path.splitext(filename)[0]
                    data[subfolder][key] = transcript_text

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Arquivo JSON criado em: {output_json}")

def main(folder_path):
    videos_dir = os.path.join(folder_path, 'videos')
    transcripts_dir = os.path.join(folder_path, 'transcripts')
    os.makedirs(transcripts_dir, exist_ok=True)

    video_files = []
    video_map = {}

    for subfolder in os.listdir(videos_dir):
        subfolder_path = os.path.join(videos_dir, subfolder)
        if os.path.isdir(subfolder_path):
            for f in glob.glob(os.path.join(subfolder_path, '*')):
                if is_video_file(f):
                    video_files.append(f)
                    video_map[f] = subfolder

    if not video_files:
        print("Nenhum vídeo encontrado nas subpastas de 'videos'.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        for video_file in video_files:
            print(f"Processando: {video_file}")
            try:
                audio_path = extract_audio(video_file, tmpdir)
                transcript = transcribe_audio(audio_path)
                subfolder = video_map[video_file]
                transcript_subdir = os.path.join(transcripts_dir, subfolder)
                os.makedirs(transcript_subdir, exist_ok=True)
                transcript_file = os.path.join(
                    transcript_subdir,
                    os.path.splitext(os.path.basename(video_file))[0] + '.txt'
                )
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcript)
                print(f"Transcrição salva em: {transcript_file}")
            except Exception as e:
                print(f"Erro ao processar {video_file}: {e}")

    # Gera o arquivo JSON após todas as transcrições
    output_json = os.path.join(folder_path, 'transcripts.json')
    build_transcripts_json(transcripts_dir, output_json)

if __name__ == "__main__":
    main(r"C:\Users\Acaci\Documents\ASIMOV_IA\AI_AGENT_AGNO - Projeto")