from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import plotly.express as px
import numpy as np
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import json

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



def purgeMarkers():
    folder = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/")

    for json_file in folder.glob("*.json"):
        try:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            data["marker_1"] = None
            data["marker_2"] = None
            data["marker_3"] = None
            data["datetime"] = datetime.now(timezone.utc).isoformat()

            with json_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    return(True)

