from typing import Dict, Tuple

from dash import Dash, html, dash_table
import pandas as pd
import plotly.express as px


def dataframe_to_dash_datable(
    df: pd.DataFrame,
    separator: str = "_",
    properties: Dict = {},
    column_properties: Dict = {},
) -> Tuple:
    column_dicts, column_renaming = [], []
    for column in df.columns:
        if isinstance(column, (list, tuple)):
            column_str = [str(x) for x in column if pd.notnull(x)]
            if "" in column_str:
                n_empty = column_str.count("")
                column_str.remove("")
                column_str = [""]*n_empty + column_str
            column_id = f"{separator}".join([x for x in column_str if x != ""])
        else:
            column_id = str(column)
        column_renaming.append(column_id)
        column_dict = {"id": column_id, "name": column_str, **properties}
        if column_id in column_properties:
            column_dict.update(column_properties[column_id])
        column_dicts.append(column_dict)
    df.columns = column_renaming
    df = df.to_dict("records")
    return df, column_dicts

# App
app = Dash(__name__, title="Multi-index data")
server = app.server
data = px.data.gapminder()
data["country"] = (
    "[" + data["country"] + "](https://en.wikipedia.org/wiki/" + data["country"].str.replace(" ", "_") + ")"
)
data = data.sort_values(["continent", "country", "year"])
data = data.pivot(
    index=["continent", "country"],
    columns="year",
    values=["gdpPercap", "pop"],
).round(2).reset_index()
data, columns = dataframe_to_dash_datable(
    data, column_properties={"country": {"presentation": "markdown"}}
)

app.layout = html.Div(
    children=[
        dash_table.DataTable(
            data=data,
            columns=columns,
            sort_action="native",
            sort_mode="single",
            filter_action="native",
            merge_duplicate_headers=True,
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)

