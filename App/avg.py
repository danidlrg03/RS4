class Average:

    # def __init__(self, df, value):
    #     self.df = df
    #     self.value = value

    def average(self, df, value):
        temp = df[value].ewm(span=len(df)).mean()
        temp2 = df[value].ewm(span=len(df)).var()
        return temp


    def variance(self, df, value):
        temp = df[value].ewm(span=len(df)).var()
        return temp