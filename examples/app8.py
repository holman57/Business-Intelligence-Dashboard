import pandas as pd
import dash
from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import urllib
import sqlalchemy as sa

# https://stackoverflow.com/questions/60273619/show-pandas-dataframe-in-webpage-and-dynamically-filter-using-dash


print(conn_string)
params = urllib.parse.quote_plus(conn_string)
ganymede_engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
sql = "SELECT TOP (100) * FROM [dbo].[orders];"
df = pd.read_sql(sql, ganymede_engine)

PAGE_SIZE = 15
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(value='', id='filter-input', placeholder='Filter', debounce=True),
    dash_table.DataTable(
        id='datatable-paging',
        columns=[
            {"name": i, "id": i} for i in df.columns  # sorted(df.columns)
        ],
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom',
        sort_action='custom',
        sort_mode='single',
        sort_by=[]
    )
])


@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', 'page_current'),
     Input('datatable-paging', 'page_size'),
     Input('datatable-paging', 'sort_by'),
     Input('filter-input', 'value')])
def update_table(page_current, page_size, sort_by, filter_string):
    # Filter
    dff = df[df.apply(lambda row: row.str.contains(filter_string, regex=False).any(), axis=1)]
    # Sort if necessary
    if len(sort_by):
        dff = dff.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )

    return dff.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


if __name__ == '__main__':
    app.run_server()