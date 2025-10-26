import pandas as pd
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.spotify_utils.tracks_scraper import fetch_track_data
from backend.spotify_utils.audio_feature_extractor import  search_youtube, download_audio, extract_audio_features

COLUMNS = [
    "track_id", "name", "artist", "album", "release_year",
    "popularity", "duration_ms", "tempo", "energy", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence",
    "danceability", "image_url"
]

DATASET_PATH = "data/songs_dataset.csv"
AUDIO_DIR = "./audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def process_track_id(track_id: str):
    # Step 1: Get metadata
    metadata = fetch_track_data(track_id)
    if not metadata:
        print(f"[ERROR] Failed to fetch metadata for {track_id}")
        return None

    # Step 2: Download audio for features
    query = f"{metadata['name']} {metadata['artist']}"
    url = search_youtube(query)
    if not url:
        print(f"[YT SEARCH ERROR] Could not find audio for {query}")
        return None

    audio_filename = f"{track_id}.mp3"
    audio_path = download_audio(url, audio_filename)
    if not audio_path:
        print(f"[DOWNLOAD ERROR] Could not download audio for {query}")
        return None

    # Step 3: Extract features
    features = extract_audio_features(audio_path)

    # Cleanup temp file
    if os.path.exists(audio_path):
        os.remove(audio_path)

    # Step 4: Merge metadata + features
    if features:
        row = {**metadata, **features}
        return row
    return None