import dash
import pandas as pd
from dash import Dash, dash_table, dcc, html, Input, Output, State
import plotly.express as px


app = Dash(__name__)
df = px.data.gapminder()
range_slider = dcc.RangeSlider(
    value=[1987, 2007],
    step=5,
    marks={i: str(i) for i in range(1952, 2012, 5)})
dtable = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in sorted(df.columns)],
    sort_action="native",
    filter_action="native",
    editable=True,
    sort_mode="multi",
    column_selectable="single",
    page_action="native",
    page_size=10,
    style_table={"overflowX": "auto"})
download_csv = html.Button("Export csv", style={"marginTop": 20})
download_xlsx = html.Button("Export xlsx", style={"marginTop": 20})
download_component1 = dcc.Download()
download_component2 = dcc.Download()
app.layout = html.Div([
    html.H2("Example 15", style={"marginBottom": 20}),
    download_component1,
    download_component2,
    range_slider,
    download_csv,
    download_xlsx,
    dtable])


@app.callback(Output(dtable, "data"), Input(range_slider, "value"))
def update_table(slider_value):
    if not slider_value:
        return dash.no_update
    dff = df[df.year.between(slider_value[0], slider_value[1])]
    return dff.to_dict("records")


@app.callback(
    Output(download_component1, "data"),
    Input(download_csv, "n_clicks"),
    State(dtable, "derived_virtual_data"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")


@app.callback(
    Output(download_component2, "data"),
    Input(download_xlsx, "n_clicks"),
    State(dtable, "derived_virtual_data"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_excel, "filtered_xlsx.xlsx")


if __name__ == "__main__":
    app.run_server(debug=True)


