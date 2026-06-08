from fastapi import FastAPI
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
            for f in HTML_DIR.glob("*_dash.html")
        ],
        key=lambda x: (x.split("_")[0])
    )

    return {
        "files": files
    }

@app.get("/dash/{filename}")
def dash(filename: str):

    dash_path = HTML_DIR / filename

    if not dash_path.exists():
        return JSONResponse(
            {"error": "dash not found"},
            status_code=404
        )

    return FileResponse(dash_path)

def plot_near_money_option_oi(ticker,days_out=14,strike_pct=0.02,return_df=True):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="5d")
    if hist.empty:
        raise ValueError(f"No price data found for {ticker}")
    ref_price = np.round(float(hist.iloc[-1]["Close"]),2)
    lower_strike = ref_price * (1 - strike_pct)
    upper_strike = ref_price * (1 + strike_pct)
    today = datetime.now().date()
    max_date = today + timedelta(days=days_out)
    all_options = []
    for exp_str in stock.options:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
        if exp_date > max_date:
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
            f"(Exp ≤ {days_out} Days, "
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
        fig.write_html("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/"+ticker+"_opts.html",config={"responsive": True})
        return options_df

@app.post("/generate_plot/{tab}")
def generate_plot_endpoint(tab):

    optsdf = plot_near_money_option_oi(tab)

    return {
        "success": True
    }