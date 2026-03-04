# Technicall Finance Analysis

#%% libraries
import talib  #Finance Library
import yfinance as  yf
import Descarga_Precios as dp
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt


#%% DASH
def contar_rachas_negativas(serie):
    contador = 0
    rachas = []

    for valor in serie:
        if valor < 0:
            contador += 1
        else:
            if contador > 0:
                rachas.append(contador)
                contador = 0

    # por si la serie termina en negativo
    if contador > 0:
        rachas.append(contador)
    return rachas



# -----------------------------
# Data Loader
# -----------------------------
def load_data(symbol:str,year,month):
    year=int(year)
    month=int(month)  
    '''
    I had to use int() to avoid the format error for date that 
    theowed me '''
    df=dp.data(symbol, start=f'{year}-{month:02d}-01')
    if df is None or df.empty:
        return go.Figure()
    
    'Check if there are columns with all the elements NaN. it it is so, drop them'
    #if df.columns[df.isna().all()].shape[0]!=0:
    #    df.dropna(axis=1,how ='all', inplace=True) #Give us the columns whose all elements are NaN#Give us the columns whose all elements are NaN
    #else:
    #    pass
    df=df.xs(symbol, level=1, axis=1).copy()
    'Drop rows with any NaN values'
    #df.dropna(inplace=True)
    
    
    close = df.loc[:,"Close"].values
    high = df.loc[:,"High"].values
    low = df.loc[:,"Low"].values


    # Overlap Indicators
    df["SMA_20"] = talib.SMA(close, timeperiod=20)
    df["EMA_20"] = talib.EMA(close, timeperiod=20)
    df["BB_UPPER"], df["BB_MIDDLE"], df["BB_LOWER"] = talib.BBANDS(close)

    # Momentum Indicators
    df["RSI"] = talib.RSI(close, timeperiod=14)
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = talib.MACD(close)
    df["STO_K"], df["STO_D"] = talib.STOCH(high, low, close)

    return df


# -----------------------------
# Dash App
# -----------------------------
app = dash.Dash(__name__)
app.title = "TA-Lib Momentum & Overlap Dashboard"

app.layout = html.Div(
    style={"padding": "20px", "backgroundColor": "black", "color": "white"},
    children=[
        html.H2("Technical Indicator Dashboard"),
        html.P('Los datos se basan en los precios en pesos de las acciones'),
        html.P('Acción'),
        dcc.Dropdown(
            id="symbol",
            options=[
                {"label": "Pampa", "value": "PAMP.BA"},
                {"label": "Aluar", "value": "ALUA.BA"},
                {"label": "IRSA", "value": "IRSA.BA"},
                {"label": "YPFD", "value": "YPFD.BA"},
                {"label": "Cresud", "value": "CRES.BA"},
                {"label": "Comercial", "value": "COME.BA"},
                {"label": "Cepu", "value": "CEPU.BA"},
                {"label": "BYMA", "value": "BYMA.BA"},
                {"label": "Macro", "value": "BMA.BA"},
                {"label": "Bco. Frances", "value": "BBAR.BA"},
                {"label": "Mirgor", "value": "MIRG.BA"},
                {"label": "Metrogas", "value": "METR.BA"},
                {"label": "Loma Negra", "value": "LOMA.BA"},
                {"label": "Galicia", "value": "GGAL.BA"},
                {"label": "Edenror", "value": "EDN.BA"},
                {"label": "Valo", "value": "VALO.BA"},
                {"label": "Ternium", "value": "TXAR.BA"},
                {"label": "Transener", "value": "TRAN.BA"},
                {"label": "TGSU", "value": "TGSU2.BA"},
                {"label": "TGNO", "value": "TGNO4.BA"},
                {"label": "Telecom", "value": "TECO2.BA"},
                {"label": "Supervill", "value": "SUPV.BA"},

            ],
            value="ALUA.BA",
            clearable=False,
        style={'width':'150px', 'backgroundColor': 'black', 'color': 'yellow'}),

        html.Div(
            style={'display':'flex', 'gap':'10px'},
            children=[
                html.Br(),
                html.P('Año de Inicio'),

                dcc.Dropdown(
                id="year",
                options=[f'{y}' for y in range(2015,2026)],
                value='2025',
                clearable=False,
                style={"width": "150px", 'backgroundColor': 'black', 'color': 'yellow'}
                    ),

                html.P('Mes de Inicio'),
                dcc.Dropdown(
                id="month",
                options=[f'{m}' for m in range(1,13)],
                value='1',
                clearable=False,
                style={"width": "150px", 'backgroundColor': 'black', 'color': 'yellow'}
                    )
            ]
        ),


        dcc.Graph(id="chart"),
    ],
)



# -----------------------------
# Callback
# -----------------------------
@app.callback(
    Output("chart", "figure"),
    Input("symbol", "value"),
    Input("year", "value"),
    Input("month", "value")
)

def update_chart(symbol,year,month):
    df = load_data(symbol,year,month)
    fig = make_subplots(
        rows=5,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.2, 0.25, 0.25],
        vertical_spacing=0.06,
        subplot_titles=("BOLLINGER", "RSI", "MACD", "HISTOGRAMA","RACHAS"),
    )

    # ---- Candlestick ----
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    # ---- Overlap Indicators ----
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], name="SMA 20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], name="EMA 20"), row=1, col=1)

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_UPPER"],
            name="BB Upper",
            line=dict(dash="dot"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["BB_LOWER"],
            name="BB Lower",
            line=dict(dash="dot"),
        ),
        row=1,
        col=1,
    )

    # ---- RSI ----
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", row=2, col=1)

    # ---- MACD ----
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"), row=3, col=1)
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="Signal"), row=3, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df["MACD_HIST"], name="Histogram"), row=3, col=1
    )

    # ---- HISTO ----
    vp_20 = df['Close'].pct_change(periods=20).dropna()
    if not vp_20.empty:
        fig.add_trace(
            go.Histogram(
                x=vp_20,
                nbinsx=50,
                histnorm='probability density',
                name='Var %',
                marker=dict(color='#8A2BE2', line=dict(color='white', width=0.5)),
                opacity=0.85,
            ),
            row=4,
            col=1,
        )

        # Add a vertical line at the last vp_20 value for reference
        try:
            last_vp = float(vp_20.iloc[-1])
        except Exception:
            last_vp = float(vp_20.values[-1])

        fig.add_vline(
            x=last_vp,
            row=4,
            col=1,
            line=dict(color='red', dash='dash'),
            annotation_text=f"Último: {last_vp:.2%}",
            annotation_font=dict(color='red'),
            annotation_position='top right',
        )
        # Estadísticas para mostrar en la esquina superior derecha del histograma
        mean_v = vp_20.mean()
        std_v = vp_20.std()
        kurt_v = vp_20.kurtosis()  #It give us the excess kurtosis not the kurtosis
        skew_v = vp_20.skew()

        stats_text = (
            f"Media: {mean_v:.2%}" + "<br>"
            + f"Desv: {std_v:.2%}" + "<br>"
            + f"Curtosis: {kurt_v:.2f}" + "<br>"
            + f"Asimetría: {skew_v:.2f}"
        )

        fig.add_annotation(
            x=0.98,
            y=0.14,
            xref='paper',
            yref='paper',
            text=stats_text,
            showarrow=False,
            align='right',
            font=dict(color='white', size=11),
            bgcolor='rgba(20,20,20,0.6)',
            bordercolor='white',
            borderwidth=0.5,
        )

            # ---- Rachas Negativas ----
    #Genero las Rachas Negativas
    rachas_negativas=contar_rachas_negativas(df['Close'].pct_change().dropna().values)

    if len(rachas_negativas)>0:
        fig.add_trace(
            go.Histogram(
                x=rachas_negativas,
                nbinsx=50,
                histnorm='probability density',
                name='Var %',
                marker=dict(color='#008B8B', line=dict(color='white', width=0.5)),
                opacity=0.85,
            ),
            row=5,
            col=1,
        )

        # Add a vertical line at the last vp_20 value for reference
        last_racha =rachas_negativas[-1]

        fig.add_vline(
            x=last_racha,
            row=5,
            col=1,
            line=dict(color='red', dash='dash'),
            annotation_text=f"Último: {last_racha}",
            annotation_font=dict(color='red'),
            annotation_position='top right',
        )


    fig.update_layout(
        height=900,
        xaxis_rangeslider_visible=False,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white'),
        legend=dict(orientation='h', font=dict(color='white')),
    )

    # Make axis labels and gridlines visible on dark background
    fig.update_xaxes(color='white', showgrid=False)
    fig.update_yaxes(color='white', gridcolor='gray')

    return fig


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8050)


# %%
