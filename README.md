# Dashboard

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

- https://stackoverflow.com/questions/45845872/running-a-dash-app-within-a-flask-app

_"how can I serve two Flask instances next to each other"_, assuming you don't end up using one instance as in the above Dash answer, you would use DispatcherMiddleware to mount both applications.
        
    dash_app = Dash(__name__)
    flask_app = Flask(__name__)
    application = DispatcherMiddleware(flask_app, {'/dash': dash_app.server})
