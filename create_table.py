import psycopg2

DATABASE_URL = "postgresql://postgres.wgfdietplnezpkbzkukq:music_recom123@aws-1-ap-northeast-1.pooler.supabase.com:5432/postgres"

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS songs (
    track_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    release_year INT,
    popularity INT,
    duration_ms INT,
    tempo FLOAT,
    energy FLOAT,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    danceability FLOAT,
    image_url TEXT
);
""")

conn.commit()
cur.close()
conn.close()

print("✅ songs table created with full schema")