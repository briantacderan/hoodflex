import numpy as np
import pandas as pd
import pandas_datareader as web
import matplotlib.dates as mdates

from hoodflex.robb_modd._logg import WidgetForecaster

class Robbin(WidgetForecaster):
    def __init__(self, ticker, start, date_points, **kwargs):
        super().__init__(ticker, start, date_points, **kwargs)
        
        """
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        -----                                                      -----
        -                    $$$$$$ hoodcast $$$$$$                    -
        -                              X                               -
        -                    $$$$$$$ robbin $$$$$$$                    -
        -----                                                      -----
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        
        
                                  ----------
                                  Parameters
                                  ----------
        
        
        ticker : string
        
            --company ticker i.e. 'IDEX'
            
        start : datetime
        
            --preferably as matplotlib.dates
            --corresponding dates in time
            --scaled (only if values start to exceed 500)
            
        date_points : [datetimes]
        
            --preferably as datetime import
            --correlating data points i.e. dates during record highs
        
                    **** optional keyword arguments ****

        learning_rate : float

            --default: 0.01
            --linear regression value for setting gradient iteration

        num_iterations : integer

            --default: 1000
            --linear regression value for setting gradient iteration
          
          
        --------------------------------
            
            
                                --------------
                                Usable Methods
                                --------------
        
        
        .optimize()
        
            --finds values: b, m
            --initializes gradient iterator
            --obtains best fit y-intercept(m) and slope of line(b)
            --uses data from variables: data_points, start
            
        .__repr__()
        
            --print() your instantiation to view resulting linear
              regression model
            --(in development)
            
        .full_dataframe()
        
            --returns a DataFrame from Yahoo! stock data
            --columns: ['Scaled Date', 'High', 'Close', '20d', '250d']
            --index: ['Date']
            --`start` will be the earliest date and will display
              each day's market results until today
            --`20d`: 20 day moving average
            --`250`: 250 day moving average
            
        .record_highs()
        
            --any correlating datapoints will suffice, but the method is 
              linked to Yahoo! stock highs. Edit to your liking.
            --use to your liking
            --recommmendation: find lines suspected on a company's 
              stock chart that may indicate rising or falling trends, 
              floor or ceilings, etc.
              
        .hoodcast_widget()
            
            
                         ----------------------------
                         Dependent Modules & Packages
                         ----------------------------
        
        
        import numpy as np
        import pandas as pd
        import pandas_datareader as web

        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        %matplotlib inline
        %matplotlib widget

        from ipywidgets import AppLayout, TwoByTwoLayout, 
                               FloatSlider, SelectionRangeSlider, 
                               jslink

        import requests
        import urllib
        import datetime as dt
        
        
        
        ----------------------------------------------------------------
        
        ----------------------------------------------------------------
        ----------------------------------------------------------------
        """
    
    def __repr__(self):
        b, m = self.optimize()
        line1 = f'Best fit y-intercept: {b}'
        line2 = f'Best fit slope: {m}'
        return f'\n\n{line1}\n{line2}\n\n\n\n'
