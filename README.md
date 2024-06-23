# Dashboard

- https://dash.plotly.com/dash-ag-grid/column-filters
- https://www.ag-grid.com/javascript-data-grid/grid-options/
- https://dash.plotly.com/dash-ag-grid/grid-size
- https://community.plotly.com/t/drop-down-with-checkboxes/21549
- https://dash.plotly.com/pattern-matching-callbacks
- https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
- https://pandas.pydata.org/docs/user_guide/timeseries.html#timeseries-offset-aliases
- https://github.com/plotly/dash-sample-apps/tree/main
- https://dash-example-index.herokuapp.com/cheatsheet
- https://dash-example-index.herokuapp.com/
- https://docs.linnworks.com/articles/#!documentation/dashboards-order
- https://www.inetsoft.com/solutions/order_analysis_dashboard_example
- https://github.com/asyaparfenova/dashboard_NorthWind_Database
- https://dash.plotly.com/tutorial
- https://dash.gallery/Portal/
- https://flask.palletsprojects.com/en/3.0.x/
- https://github.com/plotly/dash-deploy
- https://www.educative.io/courses/data-storytelling-through-visualizations-in-python
- https://www.educative.io/courses/interactive-dashboards-and-data-apps-with-plotly-and-dash
- https://github.com/LinkedInLearning/data-vis-python-dash-3009706/tree/05_01

## JQuery | Slide Left | Slide Right

    $(this).hide("slide", { direction: "left" }, 1000);
    $(this).show("slide", { direction: "left" }, 1000);

- https://github.com/flot/flot/blob/master/API.md
- https://omnipotent.net/jquery.sparkline/#s-about

## Running Dash and Flask side-by-side

- https://medium.com/@adityaarya1/deploy-a-flask-application-to-azure-vm-with-a-ssl-certificate-d2960c50783d
- https://github.com/tzelleke/flask-dash-app
- https://stackoverflow.com/questions/45845872/running-a-dash-app-within-a-flask-app

_"how can I serve two Flask instances next to each other"_, assuming you don't end up using one instance as in the above Dash answer, you would use DispatcherMiddleware to mount both applications.

```python
import dash
app = dash.Dash(__name__)
server = app.server

dash_app = Dash(__name__)
flask_app = Flask(__name__)
application = DispatcherMiddleware(flask_app, {'/dash': dash_app.server})
```

```python
from dash import Dash
from werkzeug.wsgi import DispatcherMiddleware
import flask
from werkzeug.serving import run_simple
import dash_html_components as html

server = flask.Flask(__name__)
dash_app1 = Dash(__name__, server = server, url_base_pathname='/dashboard' )
dash_app2 = Dash(__name__, server = server, url_base_pathname='/reports')
dash_app1.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])
dash_app2.layout = html.Div([html.H1('Hi there, I am app2 for reports')])
@server.route('/')
@server.route('/hello')
def hello():
    return 'hello world!'

@server.route('/dashboard')
def render_dashboard():
    return flask.redire+ct('/dash1')


@server.route('/reports')
def render_reports():
    return flask.redirect('/dash2')

app = DispatcherMiddleware(server, {
    '/dash1': dash_app1.server,
    '/dash2': dash_app2.server
})

run_simple('0.0.0.0', 8080, app, use_reloader=True, use_debugger=True)
```

- https://pandas.pydata.org/pandas-docs/version/1.3.1/user_guide/style.html

```python
from pandas.io.formats.style import Styler
from IPython.display import HTML
import re

html = Styler(df, uuid_len=0, cell_ids=False)\
      .set_table_styles([{'selector': 'td', 'props': props},
                         {'selector': '.col1', 'props': 'color:green;'},
                         {'selector': '.level0', 'props': 'color:blue;'}])\
      .render()\
      .replace('blank', '')\
      .replace('data', '')\
      .replace('level0', 'l0')\
      .replace('col_heading', '')\
      .replace('row_heading', '')

html = re.sub(r'col[0-9]+', lambda x: x.group().replace('col', 'c'), html)
html = re.sub(r'row[0-9]+', lambda x: x.group().replace('row', 'r'), html)
print(html)
HTML(html)
```
