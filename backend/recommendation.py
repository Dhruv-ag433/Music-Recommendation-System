import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("./dataset/spotify_tracks_with_audio_features.csv")

feature_cols = ['tempo', 'energy', 'speechiness', 'acousticness',
                'instrumentalness', 'liveness', 'valence', 'danceability']

scaler = StandardScaler()
df_features = scaler.fit_transform(df[feature_cols])
knn_model = NearestNeighbors(n_neighbors=10, metric='cosine')
knn_model.fit(df_features)

def recommend_by_audio(song_name, num_recommendations=10):
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

def recommend(song_name=None, artist_name=None, num_recommendations=10):
    if song_name:
        return recommend_by_audio(song_name, num_recommendations)
    elif artist_name:
        return recommend_by_artist(artist_name, num_recommendations)
    else:
        return []
    