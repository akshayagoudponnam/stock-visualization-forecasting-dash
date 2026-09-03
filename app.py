import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
import numpy as np
from datetime import date

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Stock Forecasting App"

# Define the app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1(
                "Welcome to the Stock Dash App!",
                style={'textAlign': 'center', 'color': 'white'}
            ),
            width=12
        )
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col([
            html.Label("Input stock code:", style={'color': 'white'}),
            dbc.Input(
                id="stock-code-input",
                placeholder="e.g., AAPL",
                type="text",
                style={'width': '60%', 'display': 'inline-block'}
            ),
            dbc.Button(
                "Submit",
                id="submit-button",
                color="warning",
                style={'margin-left': '10px', 'display': 'inline-block'}
            )
        ], width=6)
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col([
            html.Label("Start Date", style={'color': 'white'}),
            dcc.DatePickerSingle(
                id='start-date-picker',
                date=date(2021, 6, 1),
                display_format="DD/MM/YYYY"
            )
        ], width=6)
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col(
            dbc.Button(
                "Stock Price",
                id="stock-price-button",
                color="success",
                style={'width': '100%'}
            ),
            width=4
        ),
        dbc.Col(
            dbc.Button(
                "Forecast",
                id="forecast-button",
                color="success",
                style={'width': '100%'}
            ),
            width=4
        )
    ], style={'marginBottom': '20px'}),

    dbc.Row([
        dbc.Col(dcc.Graph(id="stock-graph"), width=12)
    ])
], fluid=True, style={'backgroundColor': '#00796b', 'padding': '20px'})


# Callback to display stock price data
@app.callback(
    Output("stock-graph", "figure"),
    Input("stock-price-button", "n_clicks"),
    State("stock-code-input", "value"),
    State("start-date-picker", "date")
)
def display_stock_price(n_clicks, stock_code, start_date):
    if n_clicks is None or not stock_code:
        return go.Figure()

    try:
        stock_data = yf.download(stock_code.upper(), start=start_date)

        if stock_data.empty:
            raise ValueError(
                "Invalid stock code or no data available for the selected date range."
            )

        stock_data.reset_index(inplace=True)
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])

        fig = go.Figure(data=[
            go.Scatter(
                x=stock_data['Date'],
                y=stock_data['Close'],
                mode='lines',
                name=stock_code
            )
        ])
        fig.update_layout(
            title=f'Stock Prices for {stock_code.upper()}',
            xaxis_title='Date',
            yaxis_title='Close Price'
        )
        return fig

    except Exception as e:
        print(f"Error fetching data: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text="Error: Invalid stock code or data not available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="red")
        )
        return fig


# Callback to display forecast data
@app.callback(
    Output("stock-graph", "figure", allow_duplicate=True),
    Input("forecast-button", "n_clicks"),
    State("stock-code-input", "value"),
    State("start-date-picker", "date"),
    prevent_initial_call=True
)
def forecast_stock_price(n_clicks, stock_code, start_date):
    if n_clicks is None or not stock_code:
        return go.Figure()

    try:
        stock_data = yf.download(stock_code.upper(), start=start_date)

        if stock_data.empty:
            raise ValueError(
                "Invalid stock code or no data available for the selected date range."
            )

        stock_data.reset_index(inplace=True)
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])

        # The project report explicitly uses a random-walk mock forecast.
        forecast_dates = pd.date_range(
            stock_data['Date'].iloc[-1] + pd.Timedelta(days=1),
            periods=30
        )
        forecast_prices = (
            stock_data['Close'].iloc[-1]
            + (np.random.randn(30).cumsum() * 2)
        )

        forecast_df = pd.DataFrame({
            'Date': forecast_dates,
            'Close': forecast_prices
        })

        # Plot historical and forecasted data
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data['Date'],
            y=stock_data['Close'],
            mode='lines',
            name=f'{stock_code.upper()} Historical'
        ))
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Close'],
            mode='lines',
            name=f'{stock_code.upper()} Forecast',
            line=dict(dash='dash')
        ))
        fig.update_layout(
            title=f'{stock_code.upper()} Price Forecast',
            xaxis_title='Date',
            yaxis_title='Price'
        )
        return fig

    except Exception as e:
        print(f"Error fetching or processing data: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text="Error: Could not generate forecast",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=20, color="red")
        )
        return fig


# Run the app
if __name__ == "__main__":
    # The report uses app.run_server(debug=True).
    # app.run(debug=True) is the current Dash-compatible equivalent.
    app.run(debug=True)
