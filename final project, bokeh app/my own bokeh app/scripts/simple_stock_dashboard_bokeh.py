from bokeh.models.ranges import Range
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import RangeTool
import pandas as pd
import yfinance as yf
from datetime import date
import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnarDataSource, Select, DataTable, TableColumn, DateRangeSlider
from bokeh.layouts import column, row 
from bokeh.plotting import figure, show
from yfinance import ticker

# buat konstanta
DEFAULT_TICKERS = ['VOO','AAPL', 'GOOG', 'MSFT', 'NFLX', 'TSLA','AMZN','AAPL','FB','BABA']
START, END = "2015-01-01", date.today().strftime("%Y-%m-%d")

# ambil data dari yfinance
def load_ticker(tickers):
    df = yf.download(tickers, start=START, end=END)
    return df["Close"].dropna()

# mengambil dan mengambungkan 2 data saham yang dipilih
def get_data_close(t1, t2):
    d = load_ticker(DEFAULT_TICKERS)
    df = d[[t1,t2]]
    returns = df.pct_change().add_suffix("_returns")
    df = pd.concat([df, returns], axis=1)
    df.rename(columns={t1:"t1", t2:"t2", t1+"_returns":"t1_returns", t2+"_returns":"t2_returns"}, inplace=True)
    return df.dropna()

# membuat pilihan-pilihan saham yang ada di drop down menu
def nix(val, lst):
    return [x for x in lst if x != val]

ticker1 = Select(title="pick first stock :", value="AAPL", options = nix("GOOG", DEFAULT_TICKERS))
ticker2 = Select(title="pick second stock :", value="GOOG", options = nix("AAPL", DEFAULT_TICKERS))

# membuat source data
data = get_data_close(ticker1.value, ticker2.value)
dates = np.array(data.index, dtype=np.datetime64)
source = ColumnDataSource(data=data)

# membuat plot
tools = "pan, wheel_zoom, xbox_select, reset"

ts1 = figure(width=700, height=250, tools=tools, x_axis_type="datetime", active_drag="xbox_select", x_range=(dates[0], dates[800]))
ts1.line("Date", "t1", source = source)
ts1.circle("Date", "t1", size=1, source=source, color=None, selection_color="firebrick")

ts2 = figure(width=700, height=250, tools=tools, x_axis_type="datetime", active_drag="xbox_select", x_range=(dates[0], dates[800]))
ts2.x_range = ts1.x_range
ts2.line("Date", "t2", source = source)
ts2.circle("Date", "t2", size=1, source=source, color=None, selection_color="firebrick")

# fungsi callbacks untuk drop down menu
def ticker1_change(attrname, old, new):
    ticker2.options = nix(new, DEFAULT_TICKERS)
    update()

def ticker2_change(attrname, old, new):
    ticker1.options = nix(new, DEFAULT_TICKERS)
    update()

def update():
    t1 = ticker1.value
    t2 = ticker2.value
    df = get_data_close(t1,t2)
    source.data = df
    ts1.title.text = t1
    ts2.title.text = t2

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

# embuat range tool untuk menggeser timeframe waktu
select = figure(title="Drag the middle and edges of the selection box to change the timeframe",
                plot_height=130, plot_width=800, y_range= ts1.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range= ts1.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('Date', 't1', color='red', source=source)
select.line('Date', 't2', color='blue', source=source)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

# Layouts
layout = column(ticker1,ts1,ticker2,ts2,select)
# show(layout)

# Bokeh Server
curdoc().add_root(layout)
curdoc().title = "stock dashboard"

