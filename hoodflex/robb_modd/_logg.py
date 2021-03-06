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
    def __init__(self, ticker, **kwargs):
        super().__init__(ticker, **kwargs)
        self.plt_1 = 0.0
        self.plt_2 = 30.0
        self.plt_3 = 60.0
        
    def new_axis_values(self, b, m):
        range_X = 30
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
        forecast_1 = '{0:.2f}'.format(m*self.plt_2 + b)
        forecast_2 = '{0:.2f}'.format(m*self.plt_3 + b)
        self.ax.set_title(f'{self.ticker} Forecast ({self.ftoday}: \${forecast_1} - {self.ffuture}: \${forecast_2})\n', fontsize=20)
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.plot(new_X, new_Y, 'o')
        self.ax.plot(new_X, high_Y)
        self.ax.plot(stock_X, stock_Y)
        self.ax.plot(self.plt_2, m*self.plt_2 + b, 's')
        self.ax.plot(self.plt_3, m*self.plt_3 + b, 's')
        
    def update_plot(self, change):
        clear_output(wait=True)
        self.ax.clear()

        if type(change.new[0]) == float:
            self.plt_2 = change.new[0]
            self.plt_3 = change.new[1]
        else:
            self.ftoday = change.new[0]
            self.ffuture = change.new[1]

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
           
    def hoodflex_widget(self):
        one_year = list([self.start + dt.timedelta(days=i) for i in range(364)])
        tick_options = [(one_year[i].strftime('%m/%d/%Y'), i/12) for i in range(len(one_year)) if i % 6 == 0]
        
        date_slider = SelectionRangeSlider(
            options=tick_options,
            index=(30, 60),
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
