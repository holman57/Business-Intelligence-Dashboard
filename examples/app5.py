# https://dash.plotly.com/datatable
# https://pandas.pydata.org/docs/user_guide/reshaping.html
# https://dev.to/wesleycheek/storing-your-data-in-a-plotly-dash-data-dashboard-1e3o
# https://medium.com/innovation-res/how-to-build-an-app-using-dash-plotly-and-python-and-deploy-it-to-aws-5d8d2c7bd652

from dash import Dash, Input, Output, callback, dash_table
import pandas as pd
import dash_bootstrap_components as dbc
import pyodbc

# df = pd.read_csv('https://git.io/Juf1t')

print(conn_string)
ganymede_conn = pyodbc.connect(conn_string)
sql = "SELECT * FROM [dbo].[customers];"
df = pd.read_sql(sql, ganymede_conn)
print(df)
ganymede_conn.close()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Label('Test Dataframe'),
    dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='tbl'),
    dbc.Alert(id='tbl_out'),
])


@callback(Output('tbl_out', 'children'), Input('tbl', 'active_cell'))
def update_graphs(active_cell):
    return str(active_cell) if active_cell else "Click the table"


if __name__ == "__main__":
    app.run(debug=True)
