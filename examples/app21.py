import dash
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_ag_grid as dag
from dash import Dash, dash_table, dcc, html, Input, Output, State, no_update, ctx
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlalchemy as sa
import urllib
import numpy as np
from string import Template
import pandas as pd
pd.options.mode.chained_assignment = None


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)



print(conn_string)
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
    step=None,
    marks={i: x for i, x in enumerate(ticks)},
    value=[0, len(ticks) - 1])
derived_table = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in ["ShipCountry"] + list(derived_columns)],
    style_table={"overflowX": "auto"}
)
# full_filter_icon = DashIconify(
#     icon="bx:filter",
#     color="green",
#     width=30,
#     height=30
# )
# partial_filter_icon = DashIconify(
#     icon="prime:filter-fill",
#     color="green",
#     width=20,
#     height=20
# )
# checklist_all_values = [i for i in range(1, 21)]
# filter = html.Div([
#     dbc.Row([
#         dbc.Col(dbc.Button("Select All", id='select-all-button', n_clicks=0, color="link")),
#         dbc.Col(dbc.Button("Clear", id='clear-button', n_clicks=0, color="link"))
#     ]),
#     dbc.Row([
#         dbc.Col(dbc.Input(id='input-value')),
#     ]),
#     dbc.Row([
#         dbc.Col(
#             dcc.Checklist(
#                 options=[{"label": f"Option {i}", "value": i} for i in range(1, 21)],
#                 value=checklist_all_values,
#                 id="checklist",
#                 style={'maxHeight': '180px', 'overflowY': 'scroll', 'accent-color': 'transparent'}))
#     ]),
#     dbc.Row([
#         dbc.Col(dbc.Button("Cancel", id='cancel-button', outline=True, color="secondary", className="me-1")),
#         dbc.Col(dbc.Button("Apply", id='apply-button', outline=True, color="success", className="me-1")),
#     ],
#         justify='end')
# ])
# popover = html.Div(
#     [
#         dbc.Button(id="popover-target", children=full_filter_icon, n_clicks=0, color=None,
#                    style={'background-color': 'transparent', 'border': 'none'}),
#         dbc.Popover(
#             id='popover',
#             children=filter,
#             target="popover-target",
#             body=True,
#             trigger="click",
#             placement='right',
#         )
#     ]
# )



# ag_grid_data_df = pd.DataFrame([{"id": i, "value": x} for i, x in enumerate(df.columns)], columns=['id', 'value'])
# ag_grid_column_defs = [
#     {"headerName": "ID", "field": "id", "sortable": True, "filter": True},
#     {"headerName": "Option", "field": "value", "sortable": True, "filter": True,
#      "valueFormatter": {"function": "'Option ' + params.value"}}
# ]
ag_grid_column_defs = []
for col in df.columns:
    ag_grid_column_defs.append({
        "headerName": col,
        "field": col,
        "sortable": True,
        "filter": True})
ag_grid = dag.AgGrid(
    id='my-ag-grid',
    columnDefs=ag_grid_column_defs,
    dashGridOptions={"pagination": True})

# dtable = dash_table.DataTable(
#     columns=[{"name": i, "id": i} for i in sorted(df.columns)],
#     sort_action="native",
#     filter_action="native",
#     editable=True,
#     sort_mode="multi",
#     column_selectable="single",
#     page_action="native",
#     page_size=10,
#     style_cell={"textAlign": "left"},
#     style_table={"overflowX": "auto"})

download_csv = html.Button("Export csv", style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_xlsx = html.Button("Export xlsx", style={"paddingTop": 5, "paddingBottom": 5, "margin": 5})
download_component1 = dcc.Download()
download_component2 = dcc.Download()
app.layout = html.Div(children=[
    dcc.Graph(id='header-interaction'),
    range_slider,
    download_component1,
    download_component2,
    download_csv,
    download_xlsx,
    derived_table,
    ag_grid,
    # dtable
    # dbc.Row([dbc.Col(popover, width=5)], justify="end"),
    # dbc.Row([dbc.Col(ag_grid, width=5)], justify="center"),
    # dcc.Store(id='store-checklist-value', storage_type='memory'),
])


@app.callback([
    # Output(dtable, "data"),
               Output(derived_table, "data"),
               Output(ag_grid, "rowData"),
               Output('header-interaction', 'figure')
               ], [Input(range_slider, "value")])
def update_table(slider_value):
    if not slider_value:
        return dash.no_update
    dff = df[df["OrderDate"].between(dates[slider_value[0]], ticks[slider_value[1]])]
    dfc = dff["ShipCountry"].value_counts().rename_axis('ShipCountry').reset_index(name='Frequency')
    orders_total = dff.pivot_table(index='OrderDate', columns='ShipCountry', values='Freight').sum().round(2)
    order_count = dff.pivot_table(index='OrderID', columns='ShipCountry', aggfunc='size').sum()
    customer_count = dff.groupby('ShipCountry')['CustomerID'].nunique()
    dff['ShipTime'] = dff['ShippedDate'] - dff['OrderDate']
    dff['ShipTime'] = dff['ShipTime'].dt.total_seconds() // 3600
    order_time = dff.pivot_table(index='OrderDate', columns='ShipCountry', values='ShipTime').sum()
    subset = dff.loc[(dff['ShipRegion'].isin(['SP', 'ID', 'RJ', 'OR', 'WA'])) & (dff['ShipVia'] > 1)]
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
    df_out = dff.to_dict("records")

    return derived_data.to_dict("records"), df_out, fig1


@app.callback(
    Output(download_component1, "data"),
    Input(download_csv, "n_clicks"),
    State(ag_grid, "derived_virtual_data"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_csv, "filtered_csv.csv")


@app.callback(
    Output(download_component2, "data"),
    Input(download_xlsx, "n_clicks"),
    State(ag_grid, "derived_virtual_data"),
    prevent_initial_call=True)
def download_data(n_clicks, data):
    dff = pd.DataFrame(data)
    return dcc.send_data_frame(dff.to_excel, "filtered_xlsx.xlsx")


#
# @app.callback(
#     Output("my-ag-grid", "rowData"),
#     Input("store-checklist-value", 'data'),
# )
# def update_ag_grid(data):
#     if data is not None:
#         return ag_grid_data_df[ag_grid_data_df["value"].isin(data)].to_dict('records')
#     return no_update
#
#
# @app.callback(
#     [Output("checklist", "options"), Output("checklist", "value")],
#     Input("input-value", 'value'),
#     prevent_initial_call=True
# )
# def update_checklist_by_input(value):
#     if value is not None:
#         return [{"label": f"Option {i}", "value": i} for i in range(1, 21) if value in f"Option {i}"], []
#
#
# @app.callback(
#     [Output("popover", "is_open"), Output("checklist", "value", allow_duplicate=True),
#      Output("popover-target", "children"), Output("store-checklist-value", "data")],
#     [Input("select-all-button", 'n_clicks'), Input("clear-button", "n_clicks"), Input("cancel-button", 'n_clicks'),
#      Input("apply-button", "n_clicks")],
#     [State("checklist", "options"), State("checklist", "value")],
#     prevent_initial_call=True
# )
# def update_popover(select_all_button_n_clicks, clear_button_n_clicks, cancel_n_clicks, apply_n_clicks, options, value):
#     if ctx.triggered_id == 'select-all-button':
#         return no_update, checklist_all_values, no_update, no_update
#
#     elif ctx.triggered_id == 'clear-button':
#         return no_update, [], no_update, no_update
#
#     elif ctx.triggered_id == 'cancel-button':
#         return False, checklist_all_values, full_filter_icon, checklist_all_values
#
#     elif ctx.triggered_id == 'apply-button':
#         if len(value) == len(checklist_all_values):
#             return False, no_update, full_filter_icon, value
#         else:
#             return False, no_update, partial_filter_icon, value
#
#     return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
    print()
