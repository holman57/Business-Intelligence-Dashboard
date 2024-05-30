import numpy as np
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash import dcc, html, Input, Output, State
from dash import dash_table
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import warnings
import base64
import io
from flask import Flask

warnings.filterwarnings('ignore')

# initialize server for your app deployment
# server = Flask(__name__)

# making a dash to run in the server __name__; stylesheet = html styling
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# if deploy onto a server
server = app.server

# create a background template for plots
templates = ['plotly', 'seaborn', 'simple_white', 'ggplot2',
             'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
             'ygridoff', 'gridon', 'none']


# create a blank figure to prevent plotly dash error when runnng the app, even though it still works without this.
def blankfigure():
    figure = go.Figure(go.Scatter(x=[], y=[]))
    figure.update_layout(template=None)
    figure.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    figure.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return figure


app.layout = html.Div([

    # components for label and input content by user
    dbc.Row([dbc.Col(html.H1('Plotter App', style={'textAlign': 'center', "font-size": "60px"}))]),  # title

    # components for upload file
    dbc.Row([dbc.Col(html.Label('Upload file'), style={'textAlign': 'left', "font-size": "30px"})]),
    dbc.Row([dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
                        style={
                            'width': '30%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=False)
             ]),
    html.Div(id='output-data-upload', children=''),

    # component for radio button for show/hide table
    dbc.Row([dcc.RadioItems(id='show_hide_table_button', options=['show_table', 'hide_table', 'show_plot'],
                            value='hide_table')]),
])


def parse_contents(contents, file_name):  # 'contents/filename' property is needed for callbacks

    content_type, content_string = contents.split(',')
    # print(content_type)

    decoded = base64.b64decode(content_string)
    # print(decoded)

    if 'csv' in file_name:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in file_name:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    elif 'txt' in file_name:
        # Assume that the user uploaded an text file
        # 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte -> USE utf-16
        df = pd.read_csv(io.StringIO(decoded.decode('utf-16')),
                         delimiter='\t')  # \t separates columns separated by tabs

    return df


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),  # refer to first arg in upload_data_file()
     Input('upload-data', 'filename'),  # refer to 2nd arg in upload_data_file()
     Input(component_id='show_hide_table_button', component_property='value')]  # refer to 3rd arg in upload_data_file()

    # State('upload-data', 'last_modified'),
    # prevent_initial_call=True
)
def upload_data_file(contents, file_name, display):
    show_table = html.Div()
    app.show_plot = html.Div()

    global uploaded_df
    if contents is not None:
        uploaded_df = parse_contents(contents, file_name)  # dataframe object
        dropdown = uploaded_df.columns
        show_table = html.Div([
            dbc.Row([dbc.Col([html.H5(file_name)])]),

            # show data table
            dbc.Row([dbc.Col([dash_table.DataTable(data=uploaded_df.to_dict('rows'),
                                                   columns=[{"name": i, "id": i} for i in uploaded_df.columns])])]),
        ])

        app.show_plot = html.Div([

            # component for show dropdown options
            dbc.Row([dbc.Col(html.Label('Select x-axis from dropdown'), width=2),  # width = between Cols
                     dbc.Col(dcc.Dropdown(id='xaxis_column1', options=dropdown, value=None)),
                     dbc.Col(html.Label('Select x-axis from dropdown'), width=2),  # width = between Cols
                     dbc.Col(dcc.Dropdown(id='xaxis_column2', options=dropdown, value=None)),
                     ]),

            dbc.Row([dbc.Col(html.Label('Select y-axis from dropdown'), width=2),
                     dbc.Col(dcc.Dropdown(id='yaxis_column1', options=dropdown, value=None, multi=True)),
                     dbc.Col(html.Label('Select y-axis from dropdown'), width=2),
                     dbc.Col(dcc.Dropdown(id='yaxis_column2', options=dropdown, value=None, multi=True)),
                     ]),

            dbc.Row([dbc.Col(html.Label('Select group column from dropdown'), width=2),
                     dbc.Col(dcc.Dropdown(id='groupby1', options=dropdown, value=None, multi=False)),
                     dbc.Col(html.Label('Select group column from dropdown'), width=2),
                     dbc.Col(dcc.Dropdown(id='groupby2', options=dropdown, value=None, multi=False)),
                     ]),

            html.Div(id='filter_list1', children=''),
            html.Div(id='filter_list2', children=''),

            # component for output graph(s) when data is uploaded
            dbc.Row([dbc.Col(
                dcc.RadioItems(id='template1', options=[{'label': k, 'value': k} for k in templates], value=None,
                               inline=True)),
                     dbc.Col(dcc.RadioItems(id='template2', options=[{'label': k, 'value': k} for k in templates],
                                            value=None, inline=True)),  # grid style
                     ]),  # grid style

            html.Br(),

            # components for graph, graph options, and download data from plot (for two plots)
            dbc.Row([dbc.Col(dcc.Graph(id="graph1", figure=blankfigure())),
                     dbc.Col(dcc.Graph(id="graph2", figure=blankfigure()))
                     ]),
            dbc.Row([dbc.Col(dcc.Dropdown(id='plot_type1', options=['scatter', 'line', 'bar', 'box'], value='line',
                                          style={'font-size': 20})),
                     dbc.Col(dcc.Dropdown(id='plot_type2', options=['scatter', 'line', 'bar', 'box'], value='line',
                                          style={'font-size': 20})),
                     ]),
        ])

    # connecting radio button options with output of upload button
    if display == 'show_table':
        return show_table
    if display == 'hide_table':
        return None
    if display == 'show_plot':
        return app.show_plot


# call back for getting filter_list1
@app.callback(
    Output("filter_list1", "children"),
    Input(component_id='groupby1', component_property='value')
)
def update_filter_list(group):
    global group1_name
    global filter_list1
    data_filtered = uploaded_df
    filter_list = data_filtered[group].unique()
    print('filter_list', filter_list)
    group1_name = group
    filter_list1 = filter_list

    app.filter_option1 = html.Div([
        dbc.Row([dbc.Col(html.Label('Select filter for plot1'), width=2),
                 dbc.Col(dcc.Dropdown(id='filter1', options=filter_list, value=None, multi=True)),
                 ]),
    ])
    if group:
        return app.filter_option1


# call back for getting filter list2
@app.callback(
    Output("filter_list2", "children"),
    Input(component_id='groupby2', component_property='value')
)
def update_filter_list(group):
    global group2_name
    global filter_list2
    data_filtered = uploaded_df
    filter_list = data_filtered[group].unique()
    print('filter_list', filter_list)
    group2_name = group
    filter_list2 = filter_list

    app.filter_option2 = html.Div([
        dbc.Row([dbc.Col(html.Label('Select filter for plot 2'), width=2),
                 dbc.Col(dcc.Dropdown(id='filter2', options=filter_list, value=None, multi=True)),
                 ]),
    ])
    if group:
        return app.filter_option2


# call back for first graph
@app.callback(
    Output(component_id='graph1', component_property='figure'),
    Input(component_id='template1', component_property='value'),
    Input(component_id='xaxis_column1', component_property='value'),
    Input(component_id='yaxis_column1', component_property='value'),
    Input(component_id='plot_type1', component_property='value')
)
def update_figure_from_upload(template, xaxis_column, yaxis_columns, plot_type):
    print(group1_name)

    df1 = uploaded_df.where(pd.notnull(uploaded_df), 0)
    df = df1.copy()

    # create figure object
    if xaxis_column and yaxis_columns:
        if group1_name:
            if filter_list1:
                df = df[df[group1_name].isin(filter_list1)]
            grouped = df.groupby([xaxis_column, group1_name]).mean().unstack()
            grouped_std = df.groupby([xaxis_column, group1_name]).std().unstack()
        else:
            grouped = df.groupby([xaxis_column]).mean().unstack()
            grouped_std = df.groupby([xaxis_column]).std().unstack()

        # create figure object
        fig = go.Figure()

        # create list of yaxis string for go.Scatter()
        yaxis_num = []
        for count in range(len(yaxis_columns)):
            count += 1
            string = 'y' + str(count)
            yaxis_num.append(string)

        if plot_type == 'bar':
            # create plots
            if len(filter_list1) >= 2:
                # if go.Scatter is used, here is always a straight line when more than yaxis is selected
                fig = px.histogram(grouped, x=xaxis_column, y=yaxis_columns, color=xaxis_column, barmode='group',
                                   histfunc='avg', text_auto=True, title='{} vs {}'.format(xaxis_column, yaxis_columns))

            else:
                for i, yaxis_column in enumerate(yaxis_columns):
                    # print(xaxis_column, yaxis_column)
                    fig.add_trace(go.Histogram(x=grouped[xaxis_column], y=grouped[yaxis_column], textposition='auto',
                                               bingroup='group',
                                               histfunc='avg'))  # marker_color='#d99b16',hoverinfo='none'))

        # if plot_type == 'line':
        #     # create plots
        #     if len(filter_list) >= 2:
        #         # if go.Scatter is used, here is always a straight line when more than yaxis is selected
        #         fig = px.line(data_filtered, x=xaxis_column, y=yaxis_columns, color='experiment_id', title = '{} vs {}'.format(xaxis_column, yaxis_columns), markers = True)

        #     else:
        #         for i,yaxis_column in enumerate(yaxis_columns):
        #             #print(xaxis_column, yaxis_column)
        #             fig.add_trace(go.Scatter(x=data_filtered[xaxis_column],y=data_filtered[yaxis_column],name=yaxis_column,yaxis= yaxis_num[i])) #marker_color='#d99b16',hoverinfo='none'))

        # create a dictionary containing multiple dictionares of yaxis
        args_for_update_layout = dict()
        for i, yaxis_name in enumerate(yaxis_columns):
            key_name = 'yaxis' if i == 0 else f'yaxis{i + 1}'
            if i == 0:
                yaxis_args = dict(title=yaxis_columns[0])
            else:
                yaxis_args = dict(title=yaxis_name, anchor='free', overlaying='y', side='left', autoshift=True)

            # populate the dictionary
            args_for_update_layout[key_name] = yaxis_args
            # print(args_for_update_layout)

        # update layout using yaxis dictionary.
        fig.update_layout(**args_for_update_layout)
        fig.update_layout(template=template)

        # combine selected data together for download in callback
        x = pd.DataFrame(data_filtered[xaxis_column])  # turn series into panda datafrae
        x.reset_index(drop=True,
                      inplace=True)  # must drop index (the 0, 1, 2..) or else will get NaN values and columns dont line up when concat
        y = pd.DataFrame(data_filtered[yaxis_columns])
        y.reset_index(drop=True, inplace=True)

        global selected_figure_data  # create global variable for selected data column for download
        selected_figure_data = pd.concat([x, y], axis=1)

    else:
        return blankfigure()

    return fig


if __name__ == "__main__":
    app.run_server(debug=True)