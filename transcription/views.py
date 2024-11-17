from django.shortcuts import render

# Create your views here.
import os
import yt_dlp as youtube_dl
import ffmpeg
import wave
import json
from django.shortcuts import render
from django.http import HttpResponse
from .forms import YouTubeLinkForm
from vosk import Model, KaldiRecognizer

def extract_audio(video_file, audio_file):
    print(f"Extracting audio from {video_file} to {audio_file}")
    ffmpeg.input(video_file).output(audio_file).run()
    print(f"Audio extracted to {audio_file}")

def transcribe_audio(audio_file):
    model = Model("model")
    wf = wave.open(audio_file, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))
        else:
            results.append(json.loads(rec.PartialResult()))

    results.append(json.loads(rec.FinalResult()))
    return results

def save_transcription(transcription, output_file):
    with open(output_file, 'w') as f:
        for result in transcription:
            if 'text' in result:
                f.write(result['text'] + '\n')

def download_video(youtube_url, output_file):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_file,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    print(f"Downloaded video to {output_file}")

def transcribe_view(request):
    if request.method == 'POST':
        form = YouTubeLinkForm(request.POST)
        if form.is_valid():
            youtube_url = form.cleaned_data['youtube_url']
            video_file = 'temp_video.wav'
            audio_file = 'temp_audio.wav'
            output_text_file = 'transcription.txt'

            download_video(youtube_url, video_file)
            extract_audio(video_file, audio_file)
            transcription = transcribe_audio(audio_file)
            save_transcription(transcription, output_text_file)

            with open(output_text_file, 'r') as f:
                transcription_text = f.read()
            print('i have reached till here ')
            #os.remove(video_file)
            #os.remove(audio_file)
            #os.remove(output_text_file)

            return HttpResponse(transcription_text, content_type='text/plain')
    else:
        form = YouTubeLinkForm()

    return render(request, 'transcription/form.html', {'form': form})
