from IPython.display import display, clear_output
from ipywidgets import AppLayout, TwoByTwoLayout, FloatSlider, \
                       SelectionRangeSlider, jslink, Output

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import datetime as dt

from hoodflex.robb_modd._joog import GradientIterator

class WidgetForecaster(GradientIterator):
    def __init__(self, ticker, start, date_points, **kwargs):
        super().__init__(ticker, start, date_points, **kwargs)
        self.plt_value_1 = 0.0
        self.plt_value_2 = 32.0
        self.plt_label_1 = '11/27/2018'
        self.plt_label_2 = '05/30/2022'
        
    def new_axis_values(self, b, m):
        range_X = 32
        new_X = list(self.x)
        new_X.append(range_X)
        new_Y = list(self.y)
        two_year_future = m*range_X + b
        new_Y.append(two_year_future)
        return [new_X, new_Y]
    
    def add_dollar(self, x, pos):
        return '$%1.2f' % (x)
    
    def initialize_hoodflex(self):
        df = self.full_dataframe()
        formatter = FuncFormatter(self.add_dollar)
        stock_X = df['Scaled Date']
        stock_Y = df['Close']
        b, m = self.optimize()
        new_X, new_Y = self.new_axis_values(b, m)
        high_Y = [m*x + b for x in new_X]
        return [formatter, stock_X, stock_Y, b, m, new_X, new_Y, high_Y]
        
    def full_plot(self):
        formatter, stock_X, stock_Y, b, m, new_X, new_Y, high_Y = self.initialize_hoodflex()
        forecast_1 = '{0:.2f}'.format(m*self.plt_value_1 + b)
        forecast_2 = '{0:.2f}'.format(m*self.plt_value_2 + b)
        self.ax.set_title(f'{self.ticker} Forecast ({self.plt_label_1}: \${forecast_1} - {self.plt_label_2}: \${forecast_2})\n', fontsize=20)
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.plot(new_X, new_Y, 'o')
        self.ax.plot(new_X, high_Y)
        self.ax.plot(stock_X, stock_Y)
        self.ax.plot(self.plt_value_1, m*self.plt_value_1 + b, 's')
        self.ax.plot(self.plt_value_2, m*self.plt_value_2 + b, 's')
        
    def update_plot(self, change):
        clear_output(wait=True)
        self.ax.clear()
        ###
        if type(change.new[0]) == float:
            self.plt_value_1 = change.new[0]
            self.plt_value_2 = change.new[1]
        else:
            self.plt_label_1 = change.new[0]
            self.plt_label_2 = change.new[1]
        ###
        self.full_plot()
        
    def plot_setup(self):
        plt.ioff()
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.tick_params(axis="y", labelsize=15)
        plt.ion()
        fig.canvas.header_visible = False
        fig.canvas.layout.min_height = '400px'
        self.fig = fig
        self.ax = ax
           
    def hoodcast_widget(self):
        dates_4yr = list([self.start + dt.timedelta(days=i) for i in range(1291)])
        tick_options = [(dates_4yr[i].strftime('%m/%d/%Y'), i/40) for i in range(len(dates_4yr)) if i % 20 == 0]
        
        date_slider = SelectionRangeSlider(
            options=tick_options,
            index=(0, 64),
            description='Date:',
            disabled=False
        )
        
        date_slider.layout.margin = '0px 30% 0px 30%'
        date_slider.layout.width = '40%'
        
        self.plot_setup()
        self.full_plot()
        date_slider.observe(self.update_plot, names='value')
        date_slider.observe(self.update_plot, names='label')

        app_layout = AppLayout(
            center=self.fig.canvas,
            footer=date_slider,
            pane_heights=[0, 6, 1]
        )

        return app_layout
