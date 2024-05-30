import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

app = dash.Dash()

options = [
    {"label": "New York City", "value": "NYC"},
    {"label": "Montreal", "value": "MTL"},
    {"label": "San Francisco", "value": "SF"},
]

app.layout = html.Div(
    id="dropdown-container",
    children=[
        dcc.Dropdown(
            id="dropdown",
            options=options,
            value=["MTL", "NYC"],
            multi=True,
        ),
        html.Button("SELECT ALL", id="select-all", n_clicks=0),
    ],
)


@app.callback(Output("dropdown", "value"), Input("select-all", "n_clicks"))
def select_all(n_clicks):
    return [option["value"] for option in options]


if __name__ == "__main__":
    app.run_server(debug=True)