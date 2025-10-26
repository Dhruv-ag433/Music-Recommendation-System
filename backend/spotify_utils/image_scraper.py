import pandas as pd
import json
import os
import time
import threading
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from queue import Queue

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
INPUT_CSV = os.getenv("INPUT_CSV", "/app/dataset/spotify_tracks_dataset.csv")
OUTPUT_CSV = os.getenv("OUTPUT_CSV", "/app/dataset/spotify_track_images.csv")

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)
print("[✅] Spotify connection established.")

# Load input data
df = pd.read_csv(INPUT_CSV)
track_ids = df["track_id"].dropna().unique().tolist()

track_ids_to_process = track_ids[4500:]

# Thread-safe queue and lock
q = Queue()
output_data = []
lock = threading.Lock()

def fetch_image_worker():
    while True:
        track_id = q.get()
        if track_id is None:
            break
        try:
            track = sp.track(track_id)
            image_url = track['album']['images'][0]['url'] if track['album']['images'] else "https://pluspng.com/img-png/spotify-logo-png-spotify-music-app-icon-1024.jpg"
        except Exception as e:
            print(f"[❌] Error fetching {track_id}: {e}")
            image_url = None

        with lock:
            output_data.append({"track_id": track_id, "image_url": image_url})
            if len(output_data) % 500 == 0:
                save_batch()

        q.task_done()
        time.sleep(0.1)  # rate limit handling

def save_batch():
    global output_data
    if output_data:
        batch_df = pd.DataFrame(output_data)
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            batch_df = pd.concat([existing_df, batch_df], ignore_index=True).drop_duplicates(subset=["track_id"])
        except FileNotFoundError:
            pass

        batch_df.to_csv(OUTPUT_CSV, index=False)
        print(f"[💾] Saved batch of {len(output_data)} rows.")
        output_data = []  # Clear after saving

# Start worker threads
num_threads = 10
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=fetch_image_worker)
    t.start()
    threads.append(t)

# Enqueue all track IDs
for tid in track_ids_to_process:
    q.put(tid)

# Wait until all tasks are processed
q.join()

# Signal threads to stop
for _ in range(num_threads):
    q.put(None)
for t in threads:
    t.join()

# Final save for remaining data
save_batch()
print("[🏁] All image URLs fetched and saved.")
