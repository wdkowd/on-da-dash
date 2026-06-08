from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

IMAGE_DIR = Path('/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/images')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():

    png_files = list(IMAGE_DIR.glob("*.png"))

    if not png_files:
        return {"last_update": 0}

    latest_time = max(
        f.stat().st_mtime
        for f in png_files
    )

    return {"last_update": latest_time}

HTML_DIR = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs")
@app.get("/plot/{filename}")
def get_plot(filename: str):

    plot_path = HTML_DIR / filename

    if not plot_path.exists():
        return JSONResponse(
            {"error": "plot not found"},
            status_code=404
        )

    return FileResponse(plot_path)

@app.get("/image/{filename}")
def image(filename: str):

    image_path = IMAGE_DIR / filename

    if not image_path.exists():
        return JSONResponse(
            {"error": "File not found"},
            status_code=404
        )

    return FileResponse(image_path)

@app.get("/tabs")
def tabs():

    files = sorted(
        [
            f.name
            for f in IMAGE_DIR.glob("*dripL.png")
        ],
        key=lambda x: (x.split("_")[0])
    )

    return {
        "files": files
    }