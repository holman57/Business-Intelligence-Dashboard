from flask import Flask
import pyodbc
import pandas as pd


app = Flask(__name__)


@app.route('/')
def flask_app():
    conn_string = (f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                   f"Server=tcp:ganymede5.database.windows.net;"
                   f"Initial Catalog=Northwind;"
                   f"Database=Northwind;"
                   f"Uid=europa;"
                   f"Pwd=*pe!xo4*eaXIXUsF;"
                   f"Encrypt=yes;"
                   f"TrustServerCertificate=no;"
                   f"Connection Timeout=30;"
                   f"Port=1433;")
    print(conn_string)
    ganymede_conn = pyodbc.connect(conn_string)
    sql = "SELECT TOP (20) * FROM [dbo].[orders];"
    df = pd.read_sql(sql, ganymede_conn)
    print(df)
    ganymede_conn.close()
    return df.to_html()


if __name__ == "__main__":
    app.run()
