from cgitb import html
#from distutils.log import debug
from setuptools._distutils import log
from statistics import mode
from turtle import fillcolor
from xmlrpc.server import DocCGIXMLRPCRequestHandler
from matplotlib.pyplot import title
import pandas as pd
import dash
from dash import Input, Output
from App.plots import Plots
from App.getData import GetData
from App.layout import layout
import os
import plotly.graph_objects as go

app = dash.Dash(__name__, title="TATEM Visualizer")


# --------------------------------------------------
# html layout of the application, specified in layout.py
app.layout = layout
#end of application layout
#---------------------------------------------------------------------------

#---------------------------------------------------------------------------
#application functionality and passing of information to tables and plots

@app.callback(
    Output('chart', 'figure'),
    [Input('datatable_id', 'selected_rows'),
    Input('dropdown', 'value'), 
    Input('filedropdown', 'value')]
)

#callback for updating plots that are whown below the table, also handles what happens when one or more rows are selected
def update_plots(chosenRows, dropdownval, filedropdown):
    # class that is used to get information from dataframe, also converts file content to dataframe
    infoGetter = GetData()
    #master dataframe that is the file content converted to a dataframe
    masterdf = infoGetter.fromFileToDF(os.path.join('../../datasets/', filedropdown))
    if len(chosenRows)==0:
        dfFiltered = infoGetter.getEventInfo(masterdf)
        if dropdownval == 'eventResults':
            p = Plots(dfFiltered, chosenRows, dropdownval)
            scatterAll = p.eventResultPlot()
        else:
            # scatter plot of all tA, tO and tR values
            p = Plots(dfFiltered, chosenRows, dropdownval)
        
            scatterAll = p.scatterAll()
        return scatterAll
    elif len(chosenRows) == 1:
        rowIndex = chosenRows[0]
        eventInfo = infoGetter.getEventInfo(masterdf)
        details = infoGetter.getDetails(masterdf)
        row = details.at[rowIndex, "details"]
        #check if there is any data in details to plot
        if len(row) == 0:
            p = Plots(infoGetter.getEventInfo(masterdf), chosenRows, dropdownval)
            signal = p.plotText("successError")
        else: 
            rowdf = pd.DataFrame.from_records(row)
            # make signal plots for DO, L1, L2, S1 and S2 in one figure
            p = Plots(rowdf, chosenRows, dropdownval)
            event = infoGetter.getEventInfoByIndex(chosenRows[0], eventInfo)
            signal = p.signal()
            # signal.add_vrect(x0=event['eventStart'], x1=(event['eventStart']+event['tA']), annotation_text='tA period', annotation_position='top left', fillcolor='#DAF7A6', opacity=0.25, line_width=2)
            # signal.add_vrect(x0=(event['operationStart']), x1=(event['operationStart']+event['tO']), annotation_text='tO period', annotation_position='top left', fillcolor='#66C7F4', opacity=0.25, line_width=2)
            # signal.add_vrect(x0=(event['operationStart']+event['tO']), x1=(event['operationStart']+event['tO']+event['tR']), annotation_text='tR period', annotation_position='top left', fillcolor='#F59031', opacity=0.25, line_width=2)
        return signal
    else:
        eventInfo = infoGetter.getEventInfo(masterdf)
        dfFiltered = eventInfo[eventInfo.index.isin(chosenRows)]
        # make a scatterplot for only the values of tA, tO and tR in chosenRows
        p = Plots(dfFiltered, chosenRows, dropdownval)
        try: 
            #p = Plots(dfFiltered, chosenRows, dropdownval)
            scatterChosen = p.scatterChosen()
            return scatterChosen
        except KeyError as keyerror:
            return p.plotText("keyError")

#callback for updating the table with data from the selected file(filedropdown)
@app.callback(
    Output('datatable_id', 'data'),
    Input('filedropdown', 'value')
)

def updateDatatable(filedropdown):
    infoGetter = GetData()
    masterdf = infoGetter.fromFileToDF(os.path.join('../../datasets/', filedropdown))
    eventInfo = infoGetter.getEventInfo(masterdf)
    return eventInfo.to_dict('records')

#----------------------------------------------------------------------------

# callback for highlighting the racing track points
@app.callback(
    Output('raceTrack', 'figure'),
    Input('datatable_id', 'selected_rows')
)

def updateRacetrack(chosenRows):
    df = GetData()
    p = Plots(df, chosenRows, "")
    raceTrack = p.raceTrack()
    return raceTrack

#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#callback for updating the file dropdown

@app.callback(
    Output('filedropdown', 'options'),
    Input('filedropdown', 'value')
)

def updateFileDropdownList(value):
    newFileList = GetData().getReportList()
    filedropdown = [{'label': newFileList[i], 'value': newFileList[i]} for i in range(len(newFileList))]
    return filedropdown

#-----------------------------------------------------------------------------
# run application

if __name__ =='__main__':
    app.run_server(debug=True)

