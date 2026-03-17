from fastapi import FastAPI

app = FastAPI(title="FitCoach Backend")

@app.get("/")
async def root():
    return {"message": "FitCoach backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}