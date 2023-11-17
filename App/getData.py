import imp
import json
import pandas as pd
import os

data_path = 'C:/TFS/TATEM/datasets/'
# data_path = './datasets/'   # ?

class GetData:

    # def __init__(self, file):
    #     self.filenme = file

    def fromFileToDF(self, file):
        with open(file, 'r') as f:
            data = json.load(f)
        df = pd.json_normalize(data)
        return df
#-----------------------------------------------------------------------------------------------------    
    def getEventInfo(self, df):
        eventInfo = df.loc[:, df.columns!='details']
        eventduration = []
        opduration = []
        for idx, row in enumerate(eventInfo['no']):
            eventduration.append(abs(eventInfo['eventEnd'][idx] - eventInfo['eventStart'][idx]))
            opduration.append(abs(eventInfo['doOff'][idx] - eventInfo['operationStart'][idx]))
        eventInfo.insert(3, 'eventDuration', eventduration)
        eventInfo.insert(6, 'operationDuration', opduration)
        return eventInfo
#------------------------------------------------------------------------------------------------------
    def getEventInfoByIndex(self, index, df):
        # eventInfo = self.getEventInfo()
        specifiedEvent = df.loc[index]
        return specifiedEvent
#------------------------------------------------------------------------------------------------------
    def getDetails(self, df):
        details = df.loc[:, df.columns=='details']
        return details
#------------------------------------------------------------------------------------------------------
    def getEventResultCount(self, df):
        notDefined = len(df[df['eventResult'] == 'NotDefined'])
        tAerr = len(df[df['eventResult'] == 'TaError'])
        tOerr = len(df[df['eventResult'] == 'ToError'])
        tRerr = len(df[df['eventResult'] == 'TrError'])
        success = len(df[df['eventResult'] == 'Success'])
        eventResult = {
        'eventResultType': ['notDefined', 'tA', 'tO', 'tR', 'success'], 
        'eventResultCount': [notDefined, tAerr, tOerr, tRerr, success],
        'colors': ['#FF4B4B', '#3AA0FA', '#CE4BFF', '#FFC300', '#179A00']}
        errdf = pd.DataFrame.from_dict(eventResult).set_index('eventResultType')
        return errdf
#-------------------------------------------------------------------------------------------------------
    def getReportList(self):
        reportList = []
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.endswith('.json'):
                    #reportList.append(os.path.join(root, file))
                    reportList.append(file)
        return reportList
#--------------------------------------------------------------------------------------------------------
    def combineFilesToOneDf(self):
        frames = []
        for root, dirs, files in os.walk(data_path):
            for file in files:
                with open(os.path.join(data_path + file), 'r') as f:
                    data = json.load(f)
                    df = pd.json_normalize(data)
                    frames.append(df)
        greatDF = pd.concat(frames, ignore_index=True)
        # print(greatDF)
        return greatDF
