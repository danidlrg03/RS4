import os
from tkinter.tix import DisplayStyle
from turtle import position, width
from click import option, style
from dash import dash_table, html, dcc
from matplotlib.pyplot import eventplot
from App.getData import GetData, data_path


reportList = []
for root, dirs, files in os.walk(data_path):
    for file in files:
        if file.endswith('.json'):
            #reportList.append(os.path.join(root, file))
            reportList.append(file)

# print(reportList)

filedropdown = [{'label': reportList[i], 'value': reportList[i]} for i in range(len(reportList))]


infoGetter = GetData()
masterdf = infoGetter.fromFileToDF( data_path+filedropdown[-1]["value"])
eventInfo = infoGetter.getEventInfo(masterdf)
#print(eventInfo)

layout = html.Div(
    [
        html.Br(),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="filedropdown",
                            options=filedropdown,
                            value=filedropdown[-1]['value'],
                            multi=False,
                            clearable=False
                        ),
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        #html.Br(),
        html.Div(
            [
                dash_table.DataTable(
                    id="datatable_id",
                    data=eventInfo.to_dict("records"),
                    columns=[
                        {"name": i, "id": i, "deletable": False, "selectable": False, "hideable": True}
                        if i == "eventStart" or i == "eventEnd" or i == "operationStart" or i == "doOff"
                        else {"name": i, "id": i, "deletable": False, "selectable": False, }
                        for i in eventInfo.columns
                    ],
                    editable=False,
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="multi",
                    row_deletable=False,
                    selected_rows=[],
                    style_cell={
                        'text_align': 'center',
                        'minWidth': '9.1%'
                    },
                    style_header={
                        'backgroundColor': 'rgb(30,30,30)',
                        'color': 'white',
                        'fontWeight': 'bold'},
                    style_data={
                        'backgroundColor': 'rgb(60,60,60)',
                        'color': 'white'
                    },
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_as_list_view=True,
                    style_data_conditional=(
                        [{"if": {
                            "column_id": "no",
                            "filter_query": "{eventResult} = NotDefined"
                            },
                            "background_color": "#FF4B4B",
                            "color": "black" }] +
                        [{"if": {
                            "column_id": "no",
                            "filter_query": "{eventResult} = Success"
                            },
                            "background_color": "#179A00",
                            "color": "black" }] + 
                        [{"if": {
                            "column_id": "no",
                            "filter_query": "{eventResult} = TaError"
                            },
                            "background_color": "#3AA0FA",
                            "color": "black" }] + 
                        [{"if": {
                            "column_id": "no",
                            "filter_query": "{eventResult} = TrError"
                            },
                            "background_color": "#FFC300",
                            "color": "black" }] + 
                        [{"if": {
                            "column_id": "no",
                            "filter_query": "{eventResult} = ToError"
                            },
                            "background_color": "#CE4BFF",
                            "color": "black" }] +
                        [{"if": {
                            "column_id": "eventDuration",
                            "filter_query": "{eventResult} = Success"
                            },
                            "background_color": "#FFA6FC",
                            "color": "black" }] +
                        [{"if": {
                            "column_id": "operationDuration",
                            "filter_query": "{eventResult} = Success"
                            },
                            "background_color": "#FFA6FC",
                            "color": "black" }]
                    ),
                    # ----------------------------
                    #multiple pages with 8 rows on each page
                    # page_action="native",
                    # page_current=0,
                    # page_size=8,
                    # ----------------------------
                    # ----------------------------
                    # all data on one page
                    page_action="none",
                    fixed_rows={"headers": True, "data": 0},
                    virtualization=False,
                    # ----------------------------
                )
            ],
            className="row",
        ),
        html.Br(),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="dropdown",
                            options=[
                                {"label": "tA value", "value": "tA"},
                                {"label": "tO values", "value": "tO"},
                                {"label": "tR values", "value": "tR"},
                                {"label": "Event Results", "value": "eventResults"}
                            ],
                            value="eventResults",
                            multi=False,
                            clearable=False
                        ),
                    ],
                    className="six columns",
                ),
            ],
            className="row",
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id="chart"),
                    ],
                    className="six columns",
                ),
                html.Div( 
                    [
                        dcc.Graph(id="raceTrack", style={'height': '600px'}),
                    ],
                    className="six columns"
                )
            ],
            className="row",
        ),
        #html.Br(),
        # html.Div(
        #     [
        #         html.Div( 
        #             [
        #                 dcc.Graph(id="raceTrack", style={'height': '600px'}),
        #             ],
        #             className="six columns"
        #         )
        #     ],
        #     className="row",
        # )
    ],
)