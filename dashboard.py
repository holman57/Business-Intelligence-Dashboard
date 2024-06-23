import dash
import dash_ag_grid as dag
from dash import Dash, dash_table, dcc, html, Input, Output, State, no_update, ctx
from dateutil.relativedelta import relativedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlalchemy as sa
import urllib
import numpy as np
from string import Template
import pandas as pd
pd.options.mode.chained_assignment = None



ganymede_conn = urllib.parse.quote_plus(conn_string)
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={ganymede_conn}")
sql = """
    SELECT TOP (1000) * 
    FROM [Orders] 
    WHERE [OrderDate] BETWEEN '1997-01-01' AND '1997-12-31'
    ORDER BY NEWID();
"""
df = pd.read_sql(sql, engine)
derived_columns = df["ShipCountry"].unique()
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
    id='range-slider-interaction',
    step=None,
    marks={i: x for i, x in enumerate(ticks)},
    value=[0, len(ticks) - 1])
derived_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in ["ShipCountry"] + list(derived_columns)],
    style_table={"overflowX": "auto"},
    id='derived-table-interaction')
ag_grid_column_defs = []
for col in df.columns:
    ag_grid_column_defs.append({
        "headerName": col,
        "field": col,
        "sortable": True,
        "filter": True})
ag_grid = dag.AgGrid(
    columnSize="autoSize",
    id='ag-grid-interaction',
    columnDefs=ag_grid_column_defs,
    style={"height": None},
    dashGridOptions={
        "pagination": True,
        "domLayout": "autoHeight",
        "paginationPageSizeSelector": [10, 20, 50, 100, 1000],
        "paginationPageSize": 10})
download_csv = html.Button(
    "Export csv",
    id="download-csv-button",
    style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_xlsx = html.Button(
    "Export xlsx",
    id="download-xlsx-button",
    style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_component1 = dcc.Download(id='dcc-component-csv-download')
download_component2 = dcc.Download(id='dcc-component-xlsx-download')
app.layout = html.Div(children=[
    dcc.Graph(id='header-interaction'),
    range_slider,
    download_component1,
    download_component2,
    download_csv,
    download_xlsx,
    derived_table,
    ag_grid
])


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


@app.callback([
        Output('ag-grid-interaction', "rowData")
    ], [
        Input('range-slider-interaction', "value")
    ])
def update_table(slider_value):
    if not slider_value:
        return dash.no_update
    dff = df[df["OrderDate"].between(dates[slider_value[0]], ticks[slider_value[1]])]

    return [dff.to_dict("records")]


@app.callback([
        Output('derived-table-interaction', "data"),
        Output('header-interaction', 'figure')
    ], [
        Input('ag-grid-interaction', "virtualRowData")
    ],
    prevent_initial_call=True)
def update_table(ag_filtered):
    if not ag_filtered:
        return dash.no_update
    dff_filtered = pd.DataFrame(ag_filtered)
    dfc = dff_filtered["ShipCountry"].value_counts().rename_axis('ShipCountry').reset_index(name='Frequency')
    orders_total = dff_filtered.pivot_table(index='OrderDate', columns='ShipCountry', values='Freight').sum().round(2)
    order_count = dff_filtered.pivot_table(index='OrderID', columns='ShipCountry', aggfunc='size').sum()
    customer_count = dff_filtered.groupby('ShipCountry')['CustomerID'].nunique()
    dff_filtered['ShipTime'] = pd.to_datetime(dff_filtered['ShippedDate']) - pd.to_datetime(dff_filtered['OrderDate'])
    dff_filtered['ShipTime'] = dff_filtered['ShipTime'].dt.total_seconds() // 3600
    order_time = dff_filtered.pivot_table(index='OrderDate', columns='ShipCountry', values='ShipTime').sum()
    subset = dff_filtered.loc[
        (dff_filtered['ShipRegion'].isin(['SP', 'ID', 'RJ', 'OR', 'WA'])) & (dff_filtered['ShipVia'] > 1)]
    subset_ShipViaSP_total = subset.pivot_table(
        index='OrderDate', columns='ShipCountry', values='Freight').sum().round(2)
    orders_total.name = "Orders Total"
    order_count.name = "Orders"
    customer_count.name = "Customers"
    order_time.name = "Processing Time"
    subset_ShipViaSP_total.name = "VIP Orders"
    derived_data = pd.concat([
        orders_total,
        order_count,
        customer_count,
        order_time,
        subset_ShipViaSP_total
    ], axis=1).reset_index().T.reset_index()
    cols = derived_data.iloc[0]
    derived_data = derived_data[1:]
    derived_data.columns = cols
    fig1 = make_subplots(rows=1, cols=2,
                         specs=[[{"type": "bar"}, {"type": "pie"}]],
                         subplot_titles=["Bar", "Pie"])
    fig1.add_trace(go.Bar(
        x=dfc["ShipCountry"],
        y=dfc["Frequency"],
        name="Country"),
        row=1, col=1)
    fig1.add_trace(go.Pie(
        labels=dfc["ShipCountry"],
        values=dfc["Frequency"],
        name="Country"),
        row=1, col=2)
    fig1.update_xaxes(domain=[0, 0.66], row=1, col=1)
    fig1.update_layout(autosize=True, margin=dict(t=0, b=0, l=0, r=0),
                       legend=dict(
                           yanchor="bottom",
                           y=0.01,
                           xanchor="right",
                           x=1.08))

    return derived_data.to_dict("records"), fig1


@app.callback(
    Output(download_component1, "data"),
    Input(download_csv, "n_clicks"),
    State(ag_grid, "virtualRowData"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")


@app.callback(
    Output(download_component2, "data"),
    Input(download_xlsx, "n_clicks"),
    State(ag_grid, "virtualRowData"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_excel, "filtered_xlsx.xlsx")


if __name__ == "__main__":
    app.run_server(debug=True)
