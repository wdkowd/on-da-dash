from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from filelock import FileLock

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
    folder = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/markers/")

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

def sendMarkers():
    folder = Path("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/markers/")

    for json_file in folder.glob("*.json"):
        try:
            with json_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            data["datetime"] = datetime.now(timezone.utc).isoformat()

            with json_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    return(True)

def get_latest_zzdf():
    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/zz/zzDF.json'
    lock = FileLock(f"{json_path}.lock")
    with lock:
        df = pd.read_json(
            json_path,
            orient="records"
        )
    return df

def get_latest_live(fname):
    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/lives/'+fname+"_live.json"
    lock = FileLock(f"{json_path}.lock")
    with lock:
        with open(json_path, 'r') as f:
            data = json.load(f)            
    df = pd.json_normalize(data)
    return(df)

def get_latest_ldo(fname):
    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/ldo/'+fname+"_ldo.json"
    lock = FileLock(f"{json_path}.lock")
    with lock:
        df = pd.read_json(
            json_path,
            orient="records"
        )
    return df

def getMrkrsJson(ttr):
    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/markers/'+str(ttr).upper()+'.json'
    lock = FileLock(f"{json_path}.lock")
    with lock:
        with open(json_path, 'r') as f:
            data = json.load(f)            
    livejson = pd.json_normalize(data)
    return(livejson)

def updateMrkrsZZ():
    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/zz/zzDF.json'
    df = pd.read_json(json_path,orient="records")

    allmrks = pd.DataFrame()
    for ttr in df['tck']:
        dashJson = getMrkrsJson(ttr)
        dashDF = dashJson[['marker_1','marker_2','marker_3']].T
        dashDF.columns=['mrkVals']
        dashDF['tck']=ttr
        dashDF['has_mrkrs'] = sum(dashDF['mrkVals'].isna()==False)>0
        allmrks = pd.concat([allmrks,dashDF[['tck','has_mrkrs']].drop_duplicates()])

    newZZMrks = pd.merge(df,allmrks,on=['tck'],suffixes=['_old','']).drop(columns=['has_mrkrs_old'])

    json_path = '/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/jsons/zz/zzDF.json'
    lock = FileLock(f"{json_path}.lock")
    with lock:
        newZZMrks.to_json(
            json_path,
            orient="records",
            date_format="iso"
        )
    return(True)



def get_closest_options(symbol, strkPrice, currPrice, expOutreach=2):
    symbol = symbol.upper()

    ticker = yf.Ticker(symbol)

    # Get available expiration dates
    expirations = ticker.options

    if not expirations:
        raise ValueError(f"No options available for {symbol}")

    # display(expirations[2])
    # Use the nearest expiration
    expiration = expirations[expOutreach]

    chain = ticker.option_chain(expiration)

    calls = chain.calls.copy()
    puts = chain.puts.copy()

    # Combine calls and puts
    calls["option_type"] = "call"
    puts["option_type"] = "put"

    if strkPrice > currPrice:
        options = pd.concat([calls], ignore_index=True)
    elif strkPrice < currPrice:
        options = pd.concat([puts], ignore_index=True)
    else:
        options = pd.concat([calls, puts], ignore_index=True)

    # Find strikes closest to the supplied price
    strikes = sorted(options["strike"].unique())

    lower_strikes = [s for s in strikes if s <= strkPrice]
    upper_strikes = [s for s in strikes if s >= strkPrice]

    selected_strikes = []

    if lower_strikes:
        selected_strikes.append(max(lower_strikes))

    if upper_strikes:
        selected_strikes.append(min(upper_strikes))

    # Remove duplicate if price exactly equals a strike
    # selected_strikes = sorted(set(selected_strikes))

    result = options[options["strike"].isin(selected_strikes)].copy()

    # Useful columns
    result = result[
        [
            "contractSymbol",
            "option_type",
            "strike",
            "lastPrice",
            "bid",
            "ask",
            "volume",
            "openInterest",
            "impliedVolatility"
        ]
    ]

    return result.reset_index(drop=True)



def get_option_history(contract_symbol):
    option = yf.Ticker(contract_symbol)

    df = (option.history(
        period="5d",
        interval="1m"
    )).reset_index()
    df['date']= df['Datetime'].dt.date
    df['time']= df['Datetime'].dt.time
    df['contSym'] = contract_symbol

    if df.empty:
        raise ValueError(
            f"No historical data found for option {contract_symbol}"
        )

    return df


def plot_option_ohlc(fig,row,col,totMrks,df):
    traceName = df['contSym'].values[0]
    fig.add_trace(
            go.Candlestick(
                name=traceName[-13:-8]+'_'+traceName[-8:-3].lstrip("0")+'.'+traceName[-3:-1],
                x=df["Datetime"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"]
            ),row=row,col=col)
    
    if totMrks==1:
        fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        title = traceName[:-15]+'_'+traceName[-13:-8]+'_'+traceName[-8:-3].lstrip("0")+'.'+traceName[-3:-1],
        # hovermode="x unified",
        margin=dict(l=5, r=3, t=30, b=3)
        )
    return fig

def plotOptsPrice(tck,strk,curr,expOut,returnDts,fig,row,col,totMrks):
    df = get_closest_options(tck,strk,curr,expOut)

    df2 = get_option_history(
        str(df['contractSymbol'][0])
    ).reset_index()

    fig = plot_option_ohlc(fig,row,col,totMrks,df2[df2['date'].isin(df2['date'].drop_duplicates()[-returnDts:])])
    
    return(fig)

def plotAllMrkOpts(tck):
    mrkrsDf = getMrkrsJson(tck)
    livesDf = get_latest_live(tck)
    mrkrsub = mrkrsDf[['marker_1','marker_2','marker_3']].T[0].dropna()

    fig = make_subplots(rows=len(mrkrsub),cols=1,shared_xaxes=True,vertical_spacing=0.03)
    for i, m in enumerate(mrkrsub.sort_values(ascending=False)):
        if m is not None:
            fig = plotOptsPrice(fig=fig,row=i+1,col=1,tck=tck, strk=m,curr=livesDf['currPrice'][0],expOut=3,returnDts=1,totMrks=len(mrkrsub))
    if len(mrkrsub)>1:
        fig.update_layout(
            template="plotly_dark",
            showlegend=False,
            # title = tck,
            # hovermode="x unified",
            margin=dict(l=5, r=3, t=3, b=3)
        )

    fig.update_xaxes(
        rangeslider_visible=False
    )
    fig.write_html("/Users/kiran/Documents/STONKZ/semiSober/on-da-dash/graphs/opts/"+tck+"_opts.html",config={"responsive": True,'displayModeBar': False})
    # fig.show()
    return True