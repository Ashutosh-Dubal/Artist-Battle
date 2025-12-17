import os
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table
import plotly.express as px

from src.spotify_client import SpotifyClient
from src.features import build_artist_features
from src.scoring import score_battle
from src.plots import make_radar_fig, make_contrib_bar_fig

app = Dash(__name__)
app.title = "Artist Battle (DS)"

app.layout = html.Div(
    style={"maxWidth": "1100px", "margin": "40px auto", "fontFamily": "Arial"},
    children=[
        html.H1("🎵 Artist Battle (Data-Driven)"),

        html.Div(
            style={"display": "flex", "gap": "12px", "alignItems": "end"},
            children=[
                html.Div([
                    html.Label("Artist A"),
                    dcc.Input(id="artist-a", type="text", value="Daft Punk", style={"width": "260px"}),
                ]),
                html.Div([
                    html.Label("Artist B"),
                    dcc.Input(id="artist-b", type="text", value="The Weeknd", style={"width": "260px"}),
                ]),
                html.Div([
                    html.Label("Top N tracks"),
                    dcc.Slider(id="top-n", min=5, max=20, step=1, value=10,
                               marks={5:"5", 10:"10", 15:"15", 20:"20"}),
                ], style={"width": "320px"}),

                html.Button("FIGHT", id="fight-btn", n_clicks=0, style={"height": "40px", "padding": "0 16px"})
            ],
        ),

        html.Hr(),

        dcc.Loading(
            type="default",
            children=html.Div(id="summary", style={"fontSize": "18px", "marginBottom": "12px"})
        ),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
            children=[
                dcc.Graph(id="radar-fig"),
                dcc.Graph(id="contrib-fig"),
            ],
        ),

        html.H3("Feature Table"),
        dash_table.DataTable(
            id="feature-table",
            page_size=10,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "8px", "whiteSpace": "normal", "height": "auto"},
        ),
    ]
)

@app.callback(
    Output("summary", "children"),
    Output("radar-fig", "figure"),
    Output("contrib-fig", "figure"),
    Output("feature-table", "data"),
    Output("feature-table", "columns"),
    Input("fight-btn", "n_clicks"),
    State("artist-a", "value"),
    State("artist-b", "value"),
    State("top-n", "value"),
    prevent_initial_call=True
)
def run_battle(n_clicks, artist_a, artist_b, top_n):
    # 1) Fetch + build features
    sp = SpotifyClient()  # reads env vars internally
    df_features, details = build_artist_features(sp, artist_a, artist_b, top_n=top_n)

    # 2) Score battle (normalized + weights + contributions)
    result = score_battle(df_features)

    # 3) Build figures
    radar_fig = make_radar_fig(result["normalized_features"])
    contrib_fig = make_contrib_bar_fig(result["contributions"])

    # 4) Summary text
    winner = result["winner"]
    margin = result["margin"]
    summary = f"🏆 Winner: {winner} (score margin: {margin:.2f})"

    # 5) Table
    table_df = result["normalized_features"].copy()
    table_df.insert(0, "artist", table_df.index)
    data = table_df.to_dict("records")
    columns = [{"name": c, "id": c} for c in table_df.columns]

    return summary, radar_fig, contrib_fig, data, columns


if __name__ == "__main__":
    # Dash runs locally; users type into the UI and it updates.
    app.run_server(debug=True)