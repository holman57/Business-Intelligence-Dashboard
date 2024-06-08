import dash
import pandas as pd
import numpy as np
from dash import Dash, dash_table, dcc, html, Input, Output, State
from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
import urllib

# https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior



print(conn_string)
ganymede_conn = urllib.parse.quote_plus(conn_string)
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={ganymede_conn}")
sql = "SELECT TOP (100) * FROM [Orders] ORDER BY NEWID();"
df = pd.read_sql(sql, engine)
timestamps = [x for x in sorted(df["OrderDate"])]
start = timestamps[0]
end = timestamps[-1]
start_date = pd.to_datetime(str(np.datetime64(f'{start.year}-{start.month:02d}-01')))
end_date = (pd.to_datetime(str(np.datetime64(f'{end.year}-{end.month:02d}-01')))
            + relativedelta(months=1))
dates = pd.date_range(start=start_date, end=end_date, freq='MS')
ticks = [str(date.strftime('%b %y')) for date in dates]
app = Dash(__name__)
range_slider = dcc.RangeSlider(min=0, max=len(ticks) - 1,
                               step=None,
                               marks={i: x for i, x in enumerate(ticks)},
                               value=[0, len(ticks) - 1])
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
download_csv = html.Button("Export csv", style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_xlsx = html.Button("Export xlsx", style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_component1 = dcc.Download()
download_component2 = dcc.Download()
app.layout = html.Div([
    html.H2("Example 17", style={"marginBottom": 20}),
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
    dff = df[df["OrderDate"].between(ticks[slider_value[0]], ticks[slider_value[1]])]
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
