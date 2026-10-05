from fastapi import FastAPI

app = FastAPI(title="Motor 2D")


@app.get("/health")
def health():
    return {"ok": True}
