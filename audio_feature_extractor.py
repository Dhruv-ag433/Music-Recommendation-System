import pandas as pd
import os
import time
import librosa
import numpy as np
import yt_dlp
from concurrent.futures import ThreadPoolExecutor, as_completed

AUDIO_DIR = "./audio"
DATASET_PATH = "./dataset/spotify_tracks_dataset.csv"
OUTPUT_PATH = "./dataset/spotify_tracks_with_audio_features.csv"
MAX_WORKERS = 8

os.makedirs(AUDIO_DIR, exist_ok=True)

def search_youtube(query):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch1',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                return f"https://www.youtube.com/watch?v={info['entries'][0]['id']}"
            return None
    except Exception as e:
        print(f"[YT ERROR] {query}: {e}")
    return None

def download_audio(url, filename):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(AUDIO_DIR, filename),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'ffmpeg_location': r'C:\\ffmpeg\\bin\\ffmpeg.exe'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return os.path.join(AUDIO_DIR, f"{filename}.mp3")
    except Exception as e:
        print(f"[DOWNLOAD ERROR] {url}: {e}")
        return None
    
def extract_audio_features(audio_path):
    try:
        y, sr = librosa.load(audio_path, offset=10, duration=60)
        
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        rms = np.mean(librosa.feature.rms(y=y))
        zcr = np.mean(librosa.feature.zero_crossing_rate(y))
        spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
        spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=y, sr=sr))
        spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfccs_mean = np.mean(mfcc, axis=1)
        rms_std = np.std(librosa.feature.rms(y=y))
        
        def safe_float(val):
            return float(val.item()) if isinstance(val, np.ndarray) and val.ndim > 0 else float(val)
        features = {
            "tempo": safe_float(tempo),
            "energy": float(rms),
            "speechiness": float(zcr),
            "acousticness": float(1.0 - min(spectral_rolloff / sr, 1.0)),
            "instrumentalness": float(1.0 if zcr < 0.04 and rms < 0.05 else 0.0),
            "liveness": float(min(rms_std * 10, 1.0)),
            "valence": float(np.clip(np.mean(mfccs_mean) / 100, 0, 1)),
            "danceability": float(np.clip(safe_float(tempo) / 200 + spectral_contrast / 100, 0, 1))
        }
        return features
    except Exception as e:
        print(f"[LIBROSA ERROR] {audio_path}: {e}")
        return None

def process_track(row):
    name = row['name']
    artist = row['artist']
    query = f"{name} {artist}"
    print(f"Searching: {query}")
    
    url = search_youtube(query)
    if not url:
        return None
    
    audio_filename = f"{row['track_id']}"
    audio_path = download_audio(url, audio_filename)
    if not audio_path:
        return None
    
    features = extract_audio_features(audio_path)
    
    time.sleep(1)
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    if features:
        row = row.to_dict()
        row.update(features)
        return row
    return None
      
def enrich_with_audio_features(csv_path):
    df = pd.read_csv(csv_path)
    enriched = []
    rows_processed = 0
    total = len(df)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_track, row): row for _, row in df.iterrows()}
    
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    enriched.append(result)
            except Exception as e:
                print(f"[THREAD ERROR] {e}")
            
            rows_processed += 1
            print(f"[{rows_processed}/{total}] Processed")
        
            if rows_processed % 100 == 0:
                df_enriched = pd.DataFrame(enriched)
                df_enriched.to_csv(OUTPUT_PATH, mode='a', header=not os.path.exists(OUTPUT_PATH), index=False)
                enriched = []
                print(f"Appended {rows_processed} rows to {OUTPUT_PATH}")
        
    if enriched:   
        df_enriched = pd.DataFrame(enriched)
        df_enriched.to_csv(OUTPUT_PATH, mode='a', header=not  os.path.exists(OUTPUT_PATH), index=False)
         
    print(f"\n Audio features saved to: {OUTPUT_PATH}")
    
if __name__ == '__main__':
    enrich_with_audio_features(DATASET_PATH)