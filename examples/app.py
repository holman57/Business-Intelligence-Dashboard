from flask import Flask
import pyodbc
import pandas as pd
from IPython.display import HTML

# https://panel.holoviz.org/


app = Flask(__name__)


@app.route('/')
def flask_app():
    conn_string = (f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                   f"Server=tcp:ganymede5.database.windows.net;"
                   f"Initial Catalog=Northwind;"
                   f"Database=Northwind;"
                   f"Uid=europa;"
                   f"Pwd=@QuDxfx5ZEWNzjzx%XKEFv;"
                   f"Encrypt=yes;"
                   f"TrustServerCertificate=no;"
                   f"Connection Timeout=30;"
                   f"Port=1433;")
    print(conn_string)
    ganymede_conn = pyodbc.connect(conn_string)
    sql = "SELECT TOP (3) * FROM [dbo].[orders];"
    df = pd.read_sql(sql, ganymede_conn)
    print(df)
    ganymede_conn.close()
    return ("<html>"
            "<head>"
            "<style>"
            "#dash_app {"
            "   width: -webkit-fill-available;"
            "   height: -webkit-fill-available;"
            "   border: none;"
            "}"
            "</style>"
            "</head>"
            "<body>"
            + df.to_html(classes='table table-stripped') +
            "<iframe id='dash_app' src='http://127.0.0.1:8050/' title='dash iframe injection'></iframe>"
            "</body>"
            "</head>"
            "</html>")


if __name__ == "__main__":
    app.run()
