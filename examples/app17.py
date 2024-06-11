import dash
import pandas as pd
import numpy as np
from dash import Dash, dash_table, dcc, html, Input, Output, State
from dateutil.relativedelta import relativedelta
import sqlalchemy as sa
import urllib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
# https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior



print(conn_string)
ganymede_conn = urllib.parse.quote_plus(conn_string)
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={ganymede_conn}")
sql = "SELECT TOP (1000) * FROM [Orders] ORDER BY NEWID();"
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
range_slider = dcc.RangeSlider(
    min=0, max=len(ticks) - 1,
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
    dcc.Graph(id='histogram-interaction'),
    range_slider,
    download_component1,
    download_component2,
    download_csv,
    download_xlsx,
    dtable,
    dcc.Graph(id='pie-interaction'),

    # dcc.Interval(
    #     id='interval-component',
    #     interval=1000,
    #     n_intervals=0
    # )
])


@app.callback([Output(dtable, "data"),
               Output('histogram-interaction', 'figure'),
               Output('pie-interaction', 'figure')
               ], Input(range_slider, "value"))
def update_table(slider_value):
    if not slider_value:
        return dash.no_update
    dff = df[df["OrderDate"].between(dates[slider_value[0]], ticks[slider_value[1]])]
    dfc = dff["ShipCountry"].value_counts().rename_axis('ShipCountry').reset_index(name='Frequency')
    dfs = dff["ShipVia"].value_counts().rename_axis('ShipVia').reset_index(name='Frequency')
    fig1 = px.bar(dfc, x="ShipCountry", y="Frequency", title="Histogram")
    # fig2 = go.Figure(data=[go.Pie(labels=dfc["Frequency"], values=dfc["CustomerID"], hole=.3)])
    # fig2 = px.pie(dfc, values=dfc["Frequency"], names=dfc["ShipCountry"])
    # fig3 = px.pie(dfs, values=dfs["Frequency"], names=dfs["ShipVia"])
    fig2 = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])
    fig2.add_trace(go.Pie(
            values=dfc["Frequency"],
            labels=dfc["ShipCountry"],
            # domain=dict(x=[0, 0.5]),
            name="Country"),
        row=1, col=2)
    fig2.add_trace(go.Pie(
            values=dfs["Frequency"],
            labels=dfs["ShipVia"],
            # domain=dict(x=[0.5, 1.0]),
            name="ShipVia"),
        row=1, col=1)
    return dff.to_dict("records"), fig1, fig2


# @app.callback(Output('histogram-interaction', 'figure'),
#               [Input('interval-component', 'n_intervals'),
#                Input(range_slider, "value")])
# def update_graph_live(n_intervals, slider_value):
#     dfc = df[df["OrderDate"].between(dates[slider_value[0]], ticks[slider_value[1]])]["CustomerID"].value_counts().rename_axis('CustomerID').reset_index(name='Frequency')
#     fig = px.bar(dfc, x="CustomerID", y="Frequency", title="Histogram")
#     return fig


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
