from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from backend.spotify_utils.process_new import process_track_id
import os
    
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

DATA_PATH = os.getenv("DATA_PATH", "./dataset")
DATASET_PATH = os.path.join(DATA_PATH, "spotify_tracks_with_audio_features.csv")
df = pd.read_csv(DATASET_PATH)

feature_cols = ['tempo', 'energy', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'danceability']

scaler = StandardScaler()
df_features = scaler.fit_transform(df[feature_cols])
knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
knn_model.fit(df_features)

def recommend_by_name(song_name, num_recommendations=10):
    match = df[df['name'].str.contains(song_name, case=False, na=False)]
    
    if match.empty:
        return []
    
    index = match.index[0]
    song_vector = df_features[index].reshape(1, -1)
    
    distance, indices = knn_model.kneighbors(song_vector, n_neighbors=num_recommendations+1)
    
    recommendations = []
    for idx in indices[0]:
        if idx != index:
            track = df.iloc[idx]
            recommendations.append({
                "name": track['name'],
                "artist": track['artist'],
                "image_url": track.get('image_url', ''),
                "track_id": track.get('track_id', '')
            })
    return recommendations[:num_recommendations]

def recommend_by_artist(artist_name, num_recommendations=10):
    artist_tracks = df[df['artist'].str.contains(artist_name, case=False, na=False)]
    
    if artist_tracks.empty:
        return []
    
    recommendations = artist_tracks.head(num_recommendations).to_dict(orient='records')
    result = []
    for track in recommendations:
        result.append({
            "name": track['name'],
            "artist": track['artist'],
            "image_url": track.get('image_url', ''),
            "track_id": track.get('track_id', '')
        })
    return result

def recommend_by_track_id(track_id, num_recommendations=10):
    global df, df_features, knn_model

    new_entries = []

    # Step 1: Add the input track if not in dataset
    if track_id not in df['track_id'].values:
        new_row = process_track_id(track_id)
        if new_row:
            new_entries.append(new_row)

    # Step 2: Save & retrain if dataset updated
    if new_entries:
        df = pd.concat([df, pd.DataFrame(new_entries)], ignore_index=True)
        df.to_csv(DATASET_PATH, index=False)

        df_features = scaler.fit_transform(df[feature_cols])
        knn_model.fit(df_features)

    # Step 3: Get the track name & artist for KNN recommendation
    track_data = df.loc[df['track_id'] == track_id].iloc[0]
    track_name = track_data['name']
    artist_name = track_data['artist']

    # Step 4: Use recommend_by_name to get recommendations
    results = recommend_by_name(track_name, num_recommendations)

    return results

def recommend(track_id=None, song_name=None, artist_name=None, num_recommendations=10):
    if track_id:
        return recommend_by_track_id(track_id, num_recommendations)
    elif song_name:
        return recommend_by_name(song_name, num_recommendations)
    elif artist_name:
        return recommend_by_artist(artist_name, num_recommendations)
    else:
        return []
    