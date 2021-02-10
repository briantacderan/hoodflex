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
    def __init__(self, ticker, date_points, **kwargs):
        super().__init__(ticker, date_points, **kwargs)
        self.plt_value_1 = 0.0
        self.plt_value_2 = 5.0
        self.plt_value_3 = 9.5
        
    def new_axis_values(self):
        range_X = 9.5
        new_X = list(self.x*2)
        new_X.append(range_X)
        new_Y = list(self.y)
        forecast_line = self.opt_slope*range_X + self.opt_y_int
        new_Y.append(forecast_line)
        return [new_X, new_Y]
    
    def add_dollar(self, x, pos):
        return '$%1.2f' % (x)
    
    def initialize_hoodflex(self):
        df = self.full_dataframe()
        formatter = FuncFormatter(self.add_dollar)
        stock_X = df['Scaled Date'] * 2
        stock_Y = df['Close']
        b, m = self.optimize()
        new_X, new_Y = self.new_axis_values(self.opt_y_int, self.opt_slope)
        high_Y = [self.opt_slope*x + self.opt_y_int for x in new_X]
        return [formatter, stock_X, stock_Y, new_X, new_Y, high_Y]
        
    def full_plot(self):
        formatter, stock_X, stock_Y, new_X, new_Y, high_Y = self.initialize_hoodflex()
        forecast_1 = '{0:.2f}'.format(self.opt_slope*self.plt_value_2 + self.opt_y_int)
        forecast_2 = '{0:.2f}'.format(self.opt_slope*self.plt_value_3 + self.opt_y_int)
        self.ax.set_title(f'{self.ticker} Forecast ({self.today_fixed}: \${forecast_1} - {self.end_fixed}: \${forecast_2})\n', fontsize=20)
        self.ax.yaxis.set_major_formatter(formatter)
        self.ax.plot(new_X, new_Y, 'o')
        self.ax.plot(new_X, high_Y)
        self.ax.plot(stock_X, stock_Y)
        self.ax.plot(self.plt_value_2, self.opt_slope*(self.plt_value_2) + self.opt_y_int, 's')
        self.ax.plot(self.plt_value_3, self.opt_slope*(self.plt_value_3) + self.opt_y_int, 's')
        
    def update_plot(self, change):
        clear_output(wait=True)
        self.ax.clear()
        ###
        if type(change.new[0]) == float:
            self.plt_value_2 = change.new[0]
            self.plt_value_3 = change.new[1]
        else:
            self.today_fixed = change.new[0]
            self.end_fixed = change.new[1]
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
           
    def hoodflex_widget(self):
        dates_1yr = list([self.start + dt.timedelta(days=i) for i in range(366)])
        tick_options = [(dates_1yr[i].strftime('%m/%d/%Y'), i/38) \
                        for i in range(len(dates_1yr)) if i % 19 == 0]
        
        date_slider = SelectionRangeSlider(
            options=tick_options,
            index=(9, 18),
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
