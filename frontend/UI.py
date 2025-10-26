import streamlit as st
import requests
import os

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000/recommend")
st.title("🎵 Music Recommendation System")

# Inputs
track_id = st.text_input("Enter Spotify Track ID:")
song_name = st.text_input("Enter Song Name:")
artist_name = st.text_input("Enter Artist Name:")
num_recommendations = st.slider("Number of Recommendations", 1, 20, 10)

# Button
if st.button("Get Recommendations"):
    if track_id or song_name or artist_name:
        with st.spinner("Fetching recommendations..."):
            payload = {
                "track_id": track_id if track_id else None,
                "name": song_name if song_name else None,
                "artist": artist_name if artist_name else None,
                "num_recommendations": num_recommendations
            }
            try:
                res = requests.post(FASTAPI_URL, json=payload)
                data = res.json()

                recommendations = data.get("recommendations", [])

                if recommendations:
                    st.success(f"Top {len(recommendations)} Recommendations:")

                    for i in range(0, len(recommendations), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j < len(recommendations):
                                rec = recommendations[i + j]
                                with cols[j]:
                                    if rec.get("image_url"):
                                        st.image(rec["image_url"], width=120)
                                    spotify_url = f"https://open.spotify.com/track/{rec['track_id']}"
                                    st.markdown(f"### [{rec['name']}]({spotify_url})", unsafe_allow_html=True)
                                    st.write(f"**Artist:** {rec['artist']}")
                else:
                    st.warning("No recommendations found.")
            except Exception as e:
                st.error(f"Error connecting to API: {e}")
    else:
        st.info("Please enter a Track ID, Song Name, or Artist Name.")