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

app = FastAPI()

from pydantic import BaseModel
import json

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


def plot_near_money_option_oi(ticker,min_days_out=3,max_days_out=14,strike_pct=0.02,return_df=True):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if hist.empty:
        raise ValueError(f"No price data found for {ticker}")
    ref_price = np.round(float(hist.iloc[-1]["Close"]),2)
    lower_strike = ref_price * (1 - strike_pct)
    upper_strike = ref_price * (1 + strike_pct)
    today = datetime.now().date()
    min_date = today + timedelta(days=min_days_out)
    max_date = today + timedelta(days=max_days_out)
    all_options = []
    for exp_str in stock.options:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
        if (exp_date < min_date)|(exp_date > max_date):
            continue
        chain = stock.option_chain(exp_str)
        calls = chain.calls.copy()
        calls = calls[calls["strike"]>=ref_price]
        calls["option_type"] = "Call"
        puts = chain.puts.copy()
        puts = puts[puts["strike"]<=ref_price]
        puts["option_type"] = "Put"
        df = pd.concat([calls, puts])
        df["expiration"] = pd.to_datetime(exp_str)
        df = df[(df["strike"] >= lower_strike)& (df["strike"] <= upper_strike)]
        all_options.append(df)

    options_df = pd.concat(all_options, ignore_index=True)
    options_df["openInterest"] = (options_df["openInterest"].fillna(0).astype(float))
    options_df["volume"] = (options_df["volume"].fillna(0).astype(float))

    fig = px.scatter_3d(
        options_df,
        x="expiration",
        y="strike",
        z="openInterest",
        color="option_type",
        color_discrete_map={
            "Call": "#00FF88",
            "Put": "#FF4444"
        },
        size="volume",
        size_max=25,
        template="plotly_dark",
        hover_data={
            "contractSymbol": True,
            "bid": ":.2f",
            "ask": ":.2f",
            "lastPrice": ":.2f",
            "volume": True,
            "openInterest": True
        },
            title=(
                f"{ticker} Opts "
                f"(Exp {min_days_out} - {max_days_out} Days, "
                f"{ref_price} ±{strike_pct:.0%})"
            )
        )
    
    fig.update_layout(
        showlegend=False,
        scene=dict(
            xaxis_title="Exp Dt",
            yaxis_title="Strike Price",
            zaxis_title="Open Interest"
        ),
        width=None,
        height=None,
        autosize=True,
        margin=dict(l=20,r=20,t=40,b=20)
    )
    # fig.show()

    if return_df:
        fig.write_html("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/opts/"+ticker+"_opts.html",config={"responsive": True})
        return options_df

@app.post("/generate_plot/{tab}")
def generate_plot_endpoint(tab):

    optsdf = plot_near_money_option_oi(tab)

    return {
        "success": True
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
        "success": True,
        "markers": markers
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
