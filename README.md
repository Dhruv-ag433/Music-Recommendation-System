
# 🎵 Music Recommendation System

A content-based recommendation engine that suggests similar songs based on metadata, lyrics, and artist profiles. Built to provide personalized music suggestions without relying on user-uploaded audio or collaborative filtering.

---

## 🚀 Overview

This project aims to deliver meaningful music recommendations using a content-based approach. It analyzes the features of a selected song — including its **lyrics**, **genre**, **tempo**, **mood**, and **artist** — to suggest songs with similar characteristics.

---

## 🔍 Key Features

- 🎧 **Content-Based Filtering**  
  Recommendations based on song attributes like lyrics, genre, and artist.

- 🧠 **NLP on Lyrics**  
  Lyrics are vectorized using `TF-IDF` to compare the semantic similarity between songs.

- 🔎 **Metadata Matching**  
  Filters and ranks songs based on metadata like genre, tempo, and mood.

- 📊 **Artist-Based Suggestions**  
  Considers artist style and genre consistency when ranking recommendations.

- 🌐 **Streamlit Frontend**  
  An interactive and responsive UI to search and receive recommendations.

---

## 🛠️ Tech Stack

| Component    | Tools / Libraries                            |
|--------------|-----------------------------------------------|
| Language     | Python 3.8+                                   |
| Frontend     | Streamlit                                     |
| Backend      | FastAPI (optional for API deployment)         |
| ML/NLP       | Scikit-learn, Pandas, Numpy, TfidfVectorizer  |
| Data Sources | Custom dataset + Spotify API (metadata)       |

---

## 📁 Folder Structure

```
music-recommender/
│── backend/
│   │── main.py              # FastAPI entry point (APIs run here)
│   │── spotify_utils.py     # Functions to fetch songs from Spotify API
│   │── recommender.py       # Recommendation logic (dataset + hybrid methods)
│   │── models/              # (optional) ML models, embeddings, etc.
│
│── frontend/
│   │── app.py               # Streamlit UI
│
│── data/
│   │── songs_dataset.csv    # Dataset (songs + metadata + lyrics)
│
│── requirements.txt         # Dependencies
│── README.md

```

---

## 📦 Installation

### 🔧 Prerequisites

- Python 3.8+
- Create a virtual environment (recommended)

### 📥 Clone the Repository

```bash
git clone https://github.com/your-username/music-recommendation-system.git
cd music-recommendation-system
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the App

```bash
cd ui
streamlit run main.py
```

The app will launch in your default browser. Enter a song name and get instant recommendations!

---

## 📊 How It Works

1. **Lyrics Vectorization:** Uses `TfidfVectorizer` to embed lyrics into numerical space.
2. **Metadata Filtering:** Narrows down candidates based on genre, tempo, mood, etc.
3. **Similarity Matching:** Calculates cosine similarity between songs.
4. **Ranking & Display:** Top N matches are presented to the user via the UI.

---

## 📈 Future Enhancements

- 🎵 Add collaborative filtering based on user preferences
- 🗣️ Add multilingual lyrics support
- 🧠 Integrate deep learning models for mood classification
- 📱 Mobile app frontend

---

## 🙋‍♂️ Author

**Dhruv Agarwal**  
📧 dhruv.agarwal433@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/dhruvagrawal433)

---

⭐ If you like this project, consider starring it and sharing it with others!
