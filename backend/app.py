from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import recommendation as recommendation

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TrackRequest(BaseModel):
    name: str = None
    artist: str = None
    num_recommendations: int = 10
    
@app.post("/recommend")
def recommend_tracks(req: TrackRequest):
    result = recommendation.recommend(req.name, req.artist, req.num_recommendations)
    return {"recommendations": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)