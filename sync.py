import os
import psycopg2
import psycopg2.extras

def get_existing_track_ids():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    print("Connected successfully!!")
    cur = conn.cursor()
    cur.execute("SELECT track_id FROM songs;")
    ids = {row[0] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return ids

def sync_csv_to_db(df):
    df = df.copy()

    # 🔐 Sanitize track_id
    df["track_id"] = df["track_id"].astype(str).str.strip()
    df = df[df["track_id"].notna()]
    df = df[df["track_id"] != ""]
    df = df[df["track_id"].str.lower() != "nan"]

    existing_ids = get_existing_track_ids()

    new_rows = df[~df["track_id"].isin(existing_ids)]

    print("[SYNC DEBUG] Existing IDs:", len(existing_ids))
    print("[SYNC DEBUG] New rows detected:", len(new_rows))

    if new_rows.empty:
        return

    conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")
    cur = conn.cursor()

    records = list(
        new_rows[[
            "track_id", "name", "artist", "album", "release_year",
            "popularity", "duration_ms", "tempo", "energy",
            "speechiness", "acousticness", "instrumentalness",
            "liveness", "valence", "danceability", "image_url"
        ]].itertuples(index=False, name=None)
    )

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO songs (
            track_id, name, artist, album, release_year,
            popularity, duration_ms, tempo, energy,
            speechiness, acousticness, instrumentalness,
            liveness, valence, danceability, image_url
        )
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING;
        """,
        records,
        page_size=1000
    )

    conn.commit()
    cur.close()
    conn.close()