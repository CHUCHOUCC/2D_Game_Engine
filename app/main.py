from fastapi import FastAPI

app = FastAPI(title="2D Engine")


@app.get("/health")
def health():
    return {"ok": True}
