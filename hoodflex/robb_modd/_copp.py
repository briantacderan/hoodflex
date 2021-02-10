import numpy as np
import pandas as pd
import pandas_datareader as web
import matplotlib.dates as mdates
import datetime as dt

class DataFormatter:
    def __init__(self, ticker, start, date_points):
        self.df = web.get_data_yahoo(ticker, start, dt.datetime.now())
        self.date_points = date_points
        self.start = start
        self.ticker = ticker
        
    def format_dates(self, dates):
        formatted = pd.Series(list(dates)).map(mdates.date2num)
        return formatted
    
    def scaler_value(self):
        series = self.format_dates(self.date_points)
        origin_date = series[0]
        scale_value = (series[1] - origin_date) / 2
        return [scale_value, origin_date]
                              
    def scale_dates(self, dates):                     
        f_dates = self.format_dates(dates)
        scale_value, origin_date = self.scaler_value()
        scaled_dates = f_dates.map(lambda x: (x - origin_date) / scale_value)
        return scaled_dates
        
class DataFrameGenerator(DataFormatter):
    def __init__(self, ticker, start, date_points, **kwargs):
        super().__init__(ticker, start, date_points, **kwargs)
        
    def full_dataframe(self):
        df = self.df.copy()
        df.reset_index(inplace=True)
        df['Scaled Date'] = self.scale_dates(df['Date'])
        df['20d'] = df['Close'].rolling(20).mean()
        df['250d'] = df['Close'].rolling(250).mean()
        df.index = df['Date']
        df = df[['Scaled Date', 'High', 'Close', '20d', '250d']]
        return df
        
    def record_highs(self):
        df = self.full_dataframe()
        scaled_high_dates = self.scale_dates(self.date_points)
        df = df[df.loc[:, 'Scaled Date'].isin(scaled_high_dates)]
        df.reset_index(inplace=True)
        df = df[['Scaled Date', 'High']]
        return df
    
    def get_X(self):
        df = self.record_highs()
        X = df['Scaled Date']
        return X
    
    def get_Y(self):
        df = self.record_highs()
        Y = df['High']
        return Y
