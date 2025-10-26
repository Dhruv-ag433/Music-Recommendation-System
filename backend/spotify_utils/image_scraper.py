import pandas as pd
import json
import time
import threading
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from queue import Queue

# Load credentials
with open("./credits/spotify_credits.json", "r") as file:
    creds = json.load(file)

client_id = creds["client_id"]
client_secret = creds["client_secret"]

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)
print("[✅] Spotify connection established.")

# Input/Output paths
input_csv = "./dataset/spotify_tracks_dataset.csv"
output_csv = "./dataset/spotify_track_images.csv"

# Load input data
df = pd.read_csv(input_csv)
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
            existing_df = pd.read_csv(output_csv)
            batch_df = pd.concat([existing_df, batch_df], ignore_index=True).drop_duplicates(subset=["track_id"])
        except FileNotFoundError:
            pass

        batch_df.to_csv(output_csv, index=False)
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
