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
from flask import Flask, send_from_directory, jsonify, render_template_string
import os

app = Flask(__name__, static_folder=".", static_url_path="")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DASH_DIR = os.path.join(BASE_DIR, "graphs", "overwatch")
OPTS_DIR = os.path.join(BASE_DIR, "graphs", "opts")


# -----------------------------
# LIST FILES
# -----------------------------
def list_files(folder):
    return sorted([
        f for f in os.listdir(folder)
        if f.endswith(".html")
    ])


# -----------------------------
# REFRESH LOGIC
# -----------------------------
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
        fig.write_html("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/opts/"+ticker+"_opts.html",config={"responsive": True})
        return options_df



# -----------------------------
# API: REFRESH OPTS
# -----------------------------
@app.route("/api/refresh-opts", methods=["POST"])
def api_refresh_opts():
    try:
        refreshopts()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -----------------------------
# API: DASH TABS
# -----------------------------
@app.route("/api/dash-tabs")
def dash_tabs():
    return jsonify(list_files(DASH_DIR))


# -----------------------------
# API: OPTS FILES
# -----------------------------
@app.route("/api/opts-files")
def opts_files():
    return jsonify(list_files(OPTS_DIR))


# -----------------------------
# STATIC FILE SERVING
# -----------------------------
@app.route("/graphs/<folder>/<file>")
def graphs(folder, file):
    return send_from_directory(os.path.join("graphs", folder), file)


@app.route("/images/<path:filename>")
def images(filename):
    return send_from_directory("images", filename)


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


if __name__ == "__main__":
    app.run(debug=True)
