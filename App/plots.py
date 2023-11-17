from __future__ import annotations
from cProfile import label
import trace
from matplotlib.pyplot import colorbar, colormaps, scatter, title, yticks
from numpy import sign, zeros
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from App.avg import Average
from App.getData import GetData
import numpy as np
import pandas as pd

infoGetter = GetData()

class Plots:

    def __init__(self, df, chosenRows, dropdownval):
        self.df = df
        self.chosenRows = chosenRows
        self.dropdownval = dropdownval
#-------------------------------------------------------------------------------------------------------------
    def scatterGivenFile(self):
        a = Average()
        avg = a.average(self.df, self.dropdownval)

        scatterGiven = go.Figure()

        scatterGiven.add_scatter(x=self.df['no'],
            y=self.df[self.dropdownval],
            mode='markers+lines',
            line={"color": "#DFFF00"},
            #colormaps = {'tA': '#3AA0FA', 'tO': '#CE4BFF', 'tR': '#FFC300'},
            name=self.dropdownval,
            hovertemplate="%{y}<extra></extra>"
        )
        scatterGiven.add_scatter(
            x=self.df['no'],
            y=avg,
            mode='lines+markers',
            line={"color": "#FF7F50"},
            name='Moving Average',
            hovertemplate="%{y}<extra></extra>"
        )

        scatterGiven.update_xaxes(showgrid=False)

        scatterGiven.update_layout(
            uirevision="foo",
            showlegend=True,
            title_text="{} values over time".format(self.dropdownval),
            title_x=0.5,
            hovermode="x",
            plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)',
            font_color='white'
        )
        scatterGiven.update_xaxes(title="Detection Point",tickmode="linear",dtick=1)
        scatterGiven.update_yaxes(title="Time in \u03BCs")
        return scatterGiven
#------------------------------------------------------------------------------------------------------------

    def scatterChosen(self):
        scatterChosen = go.Figure()
        scatterChosen.add_scatter(
            x=self.df["no"],
            y=self.df[self.dropdownval],
            mode='lines+markers',
            name='chosenValues',
            hovertemplate="%{y}<extra></extra>"
        )
        scatterChosen.update_xaxes(showgrid=False)
        scatterChosen.update_layout(
            uirevision="foo",
            showlegend=True,
            title_text="Comparison of chosen {} values".format(self.dropdownval),
            title_x=0.5,
            hovermode="x",
            plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)',
            font_color='white'
        )
        scatterChosen.update_xaxes(title="Detection Point",tickmode="linear",dtick=1)
        scatterChosen.update_yaxes(title="Time in \u03BCs")
        return scatterChosen
#-----------------------------------------------------------------------------------------------------------

    def signal(self):
        signal = make_subplots(
                rows=5,
                cols=1,
                shared_xaxes=True,
                specs=[
                    [{"type": "scatter"}],
                    [{"type": "scatter"}],
                    [{"type": "scatter"}],
                    [{"type": "scatter"}],
                    [{"type": "scatter"}],
                ],
                x_title="Timestamp(\u03BCs)",
                y_title="Signal value"
            )

        signal.add_traces(
            [
                go.Scatter(
                    x=self.df["time"],
                    y=self.df["DO"],
                    mode="markers+lines",
                    name="DO signal",
                    hovertemplate="Signal: %{y}<br>" + "Time: %{x}<br>",
                    line=dict(shape="hv"),
                ),
                go.Scatter(
                    x=self.df["time"],
                    y=self.df["L1"],
                    mode="markers+lines",
                    name="L1 signal",
                    hovertemplate="Signal: %{y}<br>" + "Time: %{x}<br>",
                    line=dict(shape="hv"),
                ),
                go.Scatter(
                    x=self.df["time"],
                    y=self.df["L2"],
                    mode="markers+lines",
                    name="L2 signal",
                    hovertemplate="Signal: %{y}<br>" + "Time: %{x}<br>",
                    line=dict(shape="hv"),
                ),
                go.Scatter(
                    x=self.df["time"],
                    y=self.df["S1"],
                    mode="markers+lines",
                    name="S1 signal",
                    hovertemplate="Signal: %{y}<br>" + "Time: %{x}<br>",
                    line=dict(shape="hv"),
                ),
                go.Scatter(
                    x=self.df["time"],
                    y=self.df["S2"],
                    mode="markers+lines",
                    name="S2 signal",
                    hovertemplate="Signal: %{y}<br>" + "Time: %{x}<br>",
                    line=dict(shape="vh"),
                ),
            ],
            rows=[1, 2, 3, 4, 5],
            cols=[1, 1, 1, 1, 1],
        )
        # trekk fra 1000000 på starttidspunkt, legg til 1000000 til sluttidspunkt, for de reelle målingene
        signal.update_xaxes(range=[self.df['time'][0], self.df['time'][len(self.df['time'])-1]], color='white', showgrid=False)
        signal.update_yaxes(visible=True, showgrid=False)

        signal.update_layout(
            showlegend=True,
            title_text="Signal plot of DO, L1, L2, S1 and S2",
            font_color='white',
            title_x=0.5,
            hovermode="x",
            height = 600,
            plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)'
        )
        signal.update_yaxes(tickmode="linear")
        return signal
#--------------------------------------------------------------------------------------------------------------------

    def plotText(self, errormsg):
        text = go.Figure()

        if errormsg == "successError":
            text = go.Figure()
            text.update_layout(
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [{"text": "No data to plot for a successfull run", "showarrow": False, "font": {"size": 28}}],
                plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)', font_color='white'
            )
        elif errormsg == "keyError":
            text.update_layout(
                xaxis = {"visible": False},
                yaxis = {"visible": False},
                annotations = [{"text": "Please select tA, tO or tR from the dropdown above to compare values", "showarrow": False, "font": {"size": 28}}],
                plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)', font_color='white'
            )
        return text
#--------------------------------------------------------------------------------------------------------------------

    def eventResultPlot(self):
        a = Average()
        avg = a.average(self.df, "tR")

        eventResult = infoGetter.getEventResultCount(self.df)
        colors = eventResult.colors.to_list()
        labels = eventResult.index.to_list()
        eventResultplot = make_subplots(
            rows=1, 
            cols=2, 
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        eventResultplot.add_bar(
            x=eventResult.index, 
            y=eventResult.eventResultCount, 
            marker=dict(autocolorscale=False, color=colors), 
            hovertemplate="Result: %{label}<br>"+"Count: %{y}<br><extra></extra>",
            text=eventResult.eventResultCount,
            textposition='outside',
            textfont={'color': colors, 'size': 12},
            showlegend=False,
            row=1, col=1, yperiod=1
        )
        
        temp = {
            "tA":round(float(a.average(self.df, "tA").iloc[-1])/10**6,6),
            "tO":round(float(a.average(self.df, "tO").iloc[-1])/10**6,6),
            "tR":round(float(a.average(self.df, "tR").iloc[-1])/10**6,6)
        }

        temp_var = [
            round((a.variance(self.df, "tA").iloc[-1]**0.5)/10**6,4),
            round((a.variance(self.df, "tO").iloc[-1]**0.5)/10**6,4),
            round((a.variance(self.df, "tR").iloc[-1]**0.5)/10**6,4)
        ]

        pdTemp = pd.Series(data=temp,name="eventResultCount")

        eventResultplot.add_bar(
            x=["tA","tO","tR"],
            y= pdTemp, 
            marker=dict(autocolorscale=False, color=colors), 
            text= pdTemp,
            textposition='outside',
            textfont={'color': colors, 'size': 12},
            showlegend=False,
            row=1, col=2, yperiod=1,
            error_y=dict(type="data", array=temp_var),
            hovertemplate="Average: %{y:.2}<br>"+"Variance : %{y}<br><extra></extra>"
        )
        eventResultplot.update_yaxes(
            #dtick=20
            row=1,
            col=2,
            ticksuffix="s"
        )
        eventResultplot.update_layout(
            height=600, 
            title_text="Quantitative and Percentile event result count",
            font_color='white',
            #yaxis={"dtick": 2},
            title_x=0.5,
            showlegend=False, 
            font_size=15, plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)'
        )
        '''
        eventResultplot.add_pie(
            values=eventResult.eventResultCount, 
            labels=labels , 
            texttemplate= "Result: %{label}<br>"+"Count: %{value}<br>" + "%{percent}<br>", 
            textposition='inside', marker={'colors': colors}, 
            hovertemplate="Result: %{label}<br>"+"Count: %{value}<br>" + "%{percent}<br><extra></extra>",
            showlegend=True,
            row=1, col=1
        )
        '''
        return eventResultplot
#-----------------------------------------------------------------------------------------------------------------------

    def raceTrack(self):
        #[180, -50 ], was the first point, where robot starts movement
        schmid_curve = [
            [  0,   0 ],[ 70,  70 ],[140,   0 ],[210,   0 ],[210,  70 ],[280,  70 ],[360, -10 ],[280, -90 ],[140, -90 ],[120, -110],[140, -130],[160, -110],
            [140,  -90],[ 70,  -90],[  0, -130],[ 70, -170],[140, -170],[140, -160],[150, -160],[150, -170],[160, -170],[160, -160],[170, -160],[170, -170],[260, -170],
            [360,  -70],[260, -170]    
        ]
        data = np.array(schmid_curve)
        x, y = data.T
        labels = [i+1 for i in range(len(schmid_curve))]
        texttest = ['top right' for i in range(len(schmid_curve))]
        texttest[8] = 'top left'; texttest[24] = 'top left'
        texttest[16] = 'bottom center'; texttest[19] = 'bottom center'; texttest[20] = 'bottom center'; texttest[23] = 'bottom center'
        texttest[17] = 'top center'; texttest[18] = 'top center'; texttest[21] = 'top center'; texttest[22] = 'top center'

        fig = go.Figure(go.Scatter(
            x=x, 
            y=y,
            text=labels,
            marker={'symbol': 'diamond', 'size': 10, 'color': '#35FFA9'},
            mode='lines+markers+text',
            textposition=texttest,
            line=dict(color='#FF8835'),
            selectedpoints=self.chosenRows
            )
        ) 
            
        fig.update_layout(
            plot_bgcolor = 'rgb(60, 60, 60)',
            paper_bgcolor = 'rgb(60, 60, 60)',
            xaxis = {"visible": False, "showgrid": False},
            yaxis = {"visible": False, "showgrid": False},
            title_text='Robot Racing Testtrack',
            font_color='white',
            title_x=0.5,
            font_size=15,
            clickmode='event+select'
            )
        return fig
#-----------------------------------------------------------------------------------------------------------------------

    def scatterAll(self):
        scatterAll = go.Figure()
        #x = self.df.loc[:, self.df[self.dropdownval != 0]]

        scatterAll.add_scatter(
            x=self.df['no'],
            y=self.df[self.dropdownval],
            mode='markers',
            marker={'color': '#179A00'},
            name=self.dropdownval,
            hovertemplate="%{y}<extra></extra>"
        )
        scatterAll.update_xaxes(showgrid=False)

        scatterAll.update_layout(
            uirevision="foo",
            showlegend=True,
            title_text="{} values over time".format(self.dropdownval),
            title_x=0.5,
            hovermode="x",
            plot_bgcolor='rgb(60, 60, 60)', paper_bgcolor='rgb(60, 60, 60)',
            font_color='white'
        )
        scatterAll.update_xaxes(title="Detection Point",tickmode="linear",dtick=1)
        scatterAll.update_yaxes(title="Time in \u03BCs")
        scatterAll.update_layout(hovermode='closest')
        return scatterAll

