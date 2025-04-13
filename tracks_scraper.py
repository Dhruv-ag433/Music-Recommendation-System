from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import time
import json

with open("./credits/spotify_credits.json", "r") as file:
    creds = json.load(file)
    
client_id = creds["client_id"]
client_secret = creds["client_secret"]

auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

print("[✅] Spotify connection established.")

def fetch_track_data(track_id):
    try:
        track = sp.track(track_id)
        
        data = {
            "track_id": track_id,
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "release_year": track['album']['release_date'][:4],
            "popularity": track['popularity'],
            "duration_ms": track['duration_ms'],
        }
        return data
    
    except Exception as e:
        print(f"Error fetching {track_id}: {e}")
        return None

def get_track_ids_from_query(query, max_results=250):
    
    all_track_ids = []
    limit = 50  # Spotify max per request
    for offset in range(0, max_results, limit):
        try:
            results = sp.search(q=query, type='track', limit=limit, offset=offset)
            track_ids = [item['id'] for item in results['tracks']['items']]
            all_track_ids.extend(track_ids)

            # Break early if no more tracks are returned
            if len(track_ids) < limit:
                break

            time.sleep(0.2)  # slight delay to avoid rate limits
        except Exception as e:
            print(f"Error in query '{query}' at offset {offset}: {e}")
            break

    return all_track_ids

def scrape_tracks(queries, max_per_query=5, save_path="./dataset/spotify_tracks_dataset.csv"):
    all_tracks = []
    
    for query in queries:
        print(f"\n[🎵] Fetching tracks for: {query}")
        track_ids = get_track_ids_from_query(query, max_results=max_per_query)

        for tid in track_ids:
            track_data = fetch_track_data(tid)
            if track_data:
                all_tracks.append(track_data)
            time.sleep(0.3)  # Respect rate limits
        
        time.sleep(30)

    df = pd.DataFrame(all_tracks)
    try:
        existing_df = pd.read_csv(save_path)
        df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['track_id'])
    except FileNotFoundError:
        pass
    
    df.to_csv(save_path, index=False)
    
def process_in_batches(search_queries, batch_size=10, wait_time=60):
    total_queries = len(search_queries)
    
    for i in range(search_queries, total_queries, batch_size):
        search_batch = search_queries[i:i + batch_size]
        scrape_tracks(search_batch, max_per_query=300)
        
        print(f"Waiting for {wait_time} seconds before next batch")
        time.sleep(wait_time)
    
if __name__ == "__main__":
    
    indian_artists = [
    "Arijit Singh", "Shreya Ghoshal", "Anuv Jain", "Darshan Raval", "Neha Kakkar",
    "AUR", "Jubin Nautiyal", "Sonu Nigam", "Rahat Fateh Ali Khan", "Sidhu Moosewala",
    "Diljit Dosanjh", "Badshah", "Honey Singh", "Kaka", "Papon", "Mohit Chauhan"
]
    genres = [
    "bollywood", "punjabi", "bhojpuri", "romantic", "sad", "lofi", "indie india", 
    "pop", "rock", "hip hop", "folk", "acoustic", "dance", "instrumental", "chill"
]
    english_artists = [
    "Taylor Swift", "Drake", "The Weeknd", "Ed Sheeran", "Billie Eilish", 
    "Dua Lipa", "Adele", "Imagine Dragons", "Coldplay", "Post Malone"
]
    moods = [
    "workout", "sleep", "party", "study", "focus", "travel", "meditation", 
    "nostalgia", "heartbreak", "love"
]
    search_queries = []

    search_queries.extend(indian_artists)
    search_queries.extend(english_artists)
    
    for genre in genres:
        search_queries.append(f"{genre} songs")

    for mood in moods:
        search_queries.append(f"{mood} songs")
        
    for year in range(2000, 2026, 2):
        search_queries.append(f"year:{year}")
    
    search_queries.append("year:2025")

    process_in_batches(search_queries, batch_size=10, wait_time=300)