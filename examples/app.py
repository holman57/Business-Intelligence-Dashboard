from flask import Flask
import pyodbc
import pandas as pd


app = Flask(__name__)


@app.route('/')
def flask_app():

    print(conn_string)
    ganymede_conn = pyodbc.connect(conn_string)
    sql = "SELECT TOP (3) * FROM [dbo].[orders];"
    df = pd.read_sql(sql, ganymede_conn)
    print(df)
    ganymede_conn.close()
    return df.to_html() + "<div id='context'></div>"


if __name__ == "__main__":
    app.run()
