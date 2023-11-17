import pytest
import json
import pandas as pd
import unittest
from App.getData import GetData
from App.plots import Plots

@pytest.fixture(scope="class")
def tatemdf():
    with open("datasets/2022-09-06_09-08-23.json", "r") as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    yield df

class TestGetTatemData:
    def test_column_present(self, tatemdf):
        # check if all columns are present
        assert "eventStart" in tatemdf.columns
        assert "eventEnd" in tatemdf.columns
        assert "doOff" in tatemdf.columns
        assert "tA" in tatemdf.columns
        assert "tO" in tatemdf.columns
        assert "tR" in tatemdf.columns
        assert "eventResult" in tatemdf.columns
        assert "details" in tatemdf.columns
    def test_non_empty(self, tatemdf):
        # check that dataframe is not empty
        assert len(tatemdf.index) != 0
    
    def test_eventInfo_values(self, tatemdf):
        for i in range(len(tatemdf)):
            print(tatemdf['eventResult'][i])
            assert tatemdf['eventResult'][i] == 'NotDefined' or 'Success' or 'TaError' or 'ToError' or 'TrError'
    
    def test_eventStart_eventEnd_values(self, tatemdf):
        for i in range(len(tatemdf)):
            assert tatemdf['eventStart'][i] < tatemdf['eventEnd'][i]

    def test_doOff_value(self, tatemdf):
        for i in range(len(tatemdf)):
            assert tatemdf['doOff'][i] >= 0

    def test_tA_value(self, tatemdf):
        for i in range(len(tatemdf)):
            assert tatemdf['tA'][i] >= 0
    
    def test_tO_value(self, tatemdf):
        for i in range(len(tatemdf)):
            assert tatemdf['tO'][i] >= 0
    
    def test_tR_value(self, tatemdf):
        for i in range(len(tatemdf)):
            assert tatemdf['tR'][i] >= 0

class TestDetailsData:
    def test_column_present(self, tatemdf):
        # check if all columns of details are present
        detailsdf = tatemdf['details']
        for k in range(len(detailsdf)):
            for i in range(len(detailsdf[k])):
                print(detailsdf[k][i])
                #print(detailsdf[k])
                assert "time" in detailsdf[k][i]
                assert "DO" in detailsdf[k][i]
                assert "ERROR" in detailsdf[k][i]
                assert "L1" in detailsdf[k][i]
                assert "L2" in detailsdf[k][i]
                assert "S1" in detailsdf[k][i]
                assert "S2" in detailsdf[k][i]

    def test_data_present(self, tatemdf):
        detailsdf = tatemdf['details']
        for k in range(len(detailsdf)):
            for i in range(len(detailsdf[k])):
                assert len(detailsdf[k][i]) != 0
    
    def test_data_values(self, tatemdf):
        detailsdf = tatemdf['details']
        for k in range(len(detailsdf)):
            for i in range(len(detailsdf[k])):
                print(detailsdf[k][i]['time'])
                assert detailsdf[k][i]['DO'] == 1 or detailsdf[k][i]['DO'] == 0
                assert detailsdf[k][i]['L1'] == 1 or detailsdf[k][i]['L1'] == 0
                assert detailsdf[k][i]['L2'] == 1 or detailsdf[k][i]['L2'] == 0
                assert detailsdf[k][i]['S1'] == 1 or detailsdf[k][i]['S1'] == 0
                assert detailsdf[k][i]['S2'] == 1 or detailsdf[k][i]['S2'] == 0

    def test_state_values(self, tatemdf):
        detailsdf = tatemdf['details']
        for k in range(len(detailsdf)):
            for i in range(len(detailsdf[k])):
                assert detailsdf[k][i]['STATE'] == 'ResetState' or 'InitState' or 'ToolActivationState' or 'ToolOperationState' or 'ExtendedOperationState' or 'ToolRetractionState' or 'ExtendedRetractionState' or 'ErrorState'


class TestEventInfoCases:
    pass


class TestDetailsInfoCase:
    pass


class TestHTMLSetupt:
    pass

class TestDataTable:
    pass

class TestAppCallback:
    pass

class TestGetData:
    pass

class TestPlots:
    pass




