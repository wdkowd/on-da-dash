from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import plotly.express as px
import numpy as np
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

import server_helps as sh

app = FastAPI()



app = FastAPI()

ZZ_DIR = Path('/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/zz')
JSON_DIR_MRKS = "/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/"
HTML_DIR_OPTS = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/opts")
HTML_DIR_PLT = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/overwatch")
HTML_DIR_LOGODDS = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/logodds")
HTML_DIR_MNMXMA = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/mnmxma")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/status")
def status():

    zz_files = list(ZZ_DIR.glob("*.html"))

    if not zz_files:
        return {"last_update": 0}

    latest_time = max(
        f.stat().st_mtime
        for f in zz_files
    )

    return {"last_update": latest_time}



@app.get("/plotOpts/{filename}")
def get_plot(filename: str):

    plot_path = HTML_DIR_OPTS / filename

    if not plot_path.exists():
        return JSONResponse(
            {"error": "plot not found"},
            status_code=404
        )

    return FileResponse(plot_path)

@app.get("/plotLogOdds/{filename}")
def get_plot(filename: str):

    plot_path = HTML_DIR_LOGODDS / filename

    if not plot_path.exists():
        return JSONResponse(
            {"error": "plot not found"},
            status_code=404
        )

    return FileResponse(plot_path)

@app.get("/plotMnMxma/{filename}")
def get_plot(filename: str):

    plot_path = HTML_DIR_MNMXMA / filename

    if not plot_path.exists():
        return JSONResponse(
            {"error": "plot not found"},
            status_code=404
        )

    return FileResponse(plot_path)

@app.get("/zz/{filename}")
def zz(filename: str):

    image_path = ZZ_DIR / filename

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
            for f in HTML_DIR_PLT.glob("*_dash.html")
        ],
        key=lambda x: str(x.split("_")[0])
    )

    return {
        "files": files
    }

@app.get("/dash/{filename}")
def dash(filename: str):

    dash_path = HTML_DIR_PLT / filename

    if not dash_path.exists():
        return JSONResponse(
            {"error": "dash not found"},
            status_code=404
        )

    return FileResponse(dash_path)


    
@app.post("/generate_opts_plot/{tab}")
def generate_plot_endpoint(tab):

    optsdf = sh.plot_near_money_option_oi(tab)

    return {
        "success": True
    }

@app.post("/api/purge-markers")
def purge_markers():

    purge = sh.purgeMarkers()

    return {
        "success": purge
    }

@app.post("/api/save-markers/{filename}")
def save_markers(filename: str, data: dict):

    markers = {
        "marker_1": data.get("marker_1"),
        "marker_2": data.get("marker_2"),
        "marker_3": data.get("marker_3"),
        "datetime": data.get("datetime")
    }

    with open(JSON_DIR_MRKS+filename+".json", "w") as f:
        json.dump(markers, f, indent=4)

    return {
        "success": True
    }

@app.get("/api/get-markers/{filename}")
async def get_markers(filename: str):

    # print(f"Marker request received: {filename}")

    json_file = JSON_DIR_MRKS+filename+".json"

    # print(f"Looking for JSON file: {json_file}")

    try:

        with open(
            json_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        # print(f"Loaded marker data: {data}")

        return data

    except json.JSONDecodeError as e:

        print(f"Invalid JSON: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON: {e}"
        )

    except Exception as e:

        print(f"Error reading marker file: {e}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
