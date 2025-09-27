from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api/v1")

# Allow requests from your Next.js frontend
origins = [
    "http://localhost:3000",  # dev frontend
    "https://localhost",  # nginx reverse proxy
    # "https://yourdomain.com",  # production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
