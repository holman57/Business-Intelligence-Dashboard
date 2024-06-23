import dash
from dash import html, dcc, no_update, ctx, State
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_iconify import DashIconify
import dash_ag_grid as dag
import pandas as pd

full_filter_icon = DashIconify(
    icon="bx:filter",
    color="green",
    width=30,
    height=30
)

partial_filter_icon = DashIconify(
    icon="prime:filter-fill",
    color="green",
    width=20,
    height=20
)

checklist_all_values = [i for i in range(1, 21)]

filter = html.Div([
    dbc.Row([
        dbc.Col(dbc.Button("Select All", id='select-all-button', n_clicks=0, color="link")),
        dbc.Col(dbc.Button("Clear", id='clear-button', n_clicks=0, color="link"))
    ]),
    dbc.Row([
        dbc.Col(dbc.Input(id='input-value')),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Checklist(
                options=[{"label": f"Option {i}", "value": i} for i in range(1, 21)],
                value=checklist_all_values,
                id="checklist",
                style={'maxHeight': '180px', 'overflowY': 'scroll', 'accent-color': 'transparent'}))
    ]),
    dbc.Row([
        dbc.Col(dbc.Button("Cancel", id='cancel-button', outline=True, color="secondary", className="me-1")),
        dbc.Col(dbc.Button("Apply", id='apply-button', outline=True, color="success", className="me-1")),
    ],
        justify='end')
])

popover = html.Div(
    [
        dbc.Button(id="popover-target", children=full_filter_icon, n_clicks=0, color=None,
                   style={'background-color': 'transparent', 'border': 'none'}),
        dbc.Popover(
            id='popover',
            children=filter,
            target="popover-target",
            body=True,
            trigger="click",
            placement='right',
        )
    ]
)

# Define the data for the grid
ag_grid_data_df = pd.DataFrame([{"id": i, "value": i} for i in range(1, 21)], columns=['id', 'value'])

# Define the column definitions for the grid
ag_grid_column_defs = [
    {"headerName": "ID", "field": "id", "sortable": True, "filter": True},
    {"headerName": "Option", "field": "value", "sortable": True, "filter": True,
     "valueFormatter": {"function": "'Option ' + params.value"}}
]

# Create the AG Grid component
ag_grid = dag.AgGrid(
    id='my-ag-grid',
    rowData=ag_grid_data_df.to_dict('records'),
    columnDefs=ag_grid_column_defs
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(popover, width=5)
    ], justify="end"),
    dbc.Row([
        dbc.Col(ag_grid, width=5)
    ], justify="center"),
    dcc.Store(id='store-checklist-value', storage_type='memory')
])


@app.callback(
    Output("my-ag-grid", "rowData"),
    Input("store-checklist-value", 'data'),
)
def update_ag_grid(data):
    if data is not None:
        return ag_grid_data_df[ag_grid_data_df["value"].isin(data)].to_dict('records')
    return no_update


@app.callback(
    [Output("checklist", "options"), Output("checklist", "value")],
    Input("input-value", 'value'),
    prevent_initial_call=True
)
def update_checklist_by_input(value):
    if value is not None:
        return [{"label": f"Option {i}", "value": i} for i in range(1, 21) if value in f"Option {i}"], []


@app.callback(
    [Output("popover", "is_open"), Output("checklist", "value", allow_duplicate=True),
     Output("popover-target", "children"), Output("store-checklist-value", "data")],
    [Input("select-all-button", 'n_clicks'), Input("clear-button", "n_clicks"), Input("cancel-button", 'n_clicks'),
     Input("apply-button", "n_clicks")],
    [State("checklist", "options"), State("checklist", "value")],
    prevent_initial_call=True
)
def update_popover(select_all_button_n_clicks, clear_button_n_clicks, cancel_n_clicks, apply_n_clicks, options, value):
    if ctx.triggered_id == 'select-all-button':
        return no_update, checklist_all_values, no_update, no_update

    elif ctx.triggered_id == 'clear-button':
        return no_update, [], no_update, no_update

    elif ctx.triggered_id == 'cancel-button':
        return False, checklist_all_values, full_filter_icon, checklist_all_values

    elif ctx.triggered_id == 'apply-button':
        if len(value) == len(checklist_all_values):
            return False, no_update, full_filter_icon, value
        else:
            return False, no_update, partial_filter_icon, value

    return no_update


if __name__ == '__main__':
    app.run_server(debug=True)
