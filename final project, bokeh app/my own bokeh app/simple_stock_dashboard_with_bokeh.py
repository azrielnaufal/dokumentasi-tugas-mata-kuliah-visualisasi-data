from bokeh.models.ranges import Range
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import RangeTool
import pandas as pd
import yfinance as yf
from datetime import date
import numpy as np

from bokeh.io import curdoc
from bokeh.models import ColumnarDataSource, Select, DataTable, TableColumn
from bokeh.layouts import column, row 
from bokeh.plotting import figure, show
from yfinance import ticker

# buat konstanta
DEFAULT_TICKERS = ['AAPL', 'GOOG', 'MSFT', 'NFLX', 'TSLA','AMZN','AAPL','FB','BABA']
START, END = "2015-01-01", date.today().strftime("%Y-%m-%d")

# ambil data --HARGA-- dari yfinance
def load_data(ticker):
    data = yf.download(ticker, start=START, end=END)
    return data

# ambil data --ANALISIS SAHAM-- dari yfinance
def load_recom(ticker):
    stock = yf.Ticker(ticker)
    temp = stock.recommendations
    return temp.tail(10)

# mengambil dan mengambungkan 2 data saham yang dipilih
def get_data_close(t1, t2):
    d = load_data(DEFAULT_TICKERS)
    cols = [t1,t2]
    df = d['Close'][cols]
    returns = df.pct_change().add_suffix("_returns")
    df = pd.concat([df, returns], axis=1)
    df.rename(columns={t1:"t1", t2:"t2", t1+"_returns":"t1_returns", t2+"_returns":"t2_returns"}, inplace=True)
    return df.dropna()

# membuat pilihan-pilihan saham yang ada di drop down menu
def nix(val, lst):
    return [x for x in lst if x != val]

# drop down menu
ticker1 = Select(title="pick first stock :", value="AAPL", options = nix("GOOG", DEFAULT_TICKERS))
ticker2 = Select(title="pick second stock :", value="GOOG", options = nix("AAPL", DEFAULT_TICKERS))

analysis_t1 = load_recom(ticker1.value)
analysis_t2 = load_recom(ticker2.value)
source_recom_t1 = ColumnDataSource(analysis_t1)
source_recom_t2 = ColumnDataSource(analysis_t2)

t1_columns = [TableColumn(field=col, title=col) for col in analysis_t1.columns]
t2_columns = [TableColumn(field=col, title=col) for col in analysis_t2.columns]

table_recom_t1 = DataTable(source = source_recom_t1, columns = t1_columns, width=500, height=250, index_position=None)
table_recom_t2 = DataTable(source = source_recom_t2, columns = t2_columns, width=500, height=250, index_position=None)

# membuat source data
data = get_data_close(ticker1.value, ticker2.value)
dates = np.array(data.index, dtype=np.datetime64)
source_plot = ColumnDataSource(data=data)

# membuat plot
tools = "pan, wheel_zoom, xbox_select, reset"

ts1 = figure(width=700, height=250, tools=tools, x_axis_type="datetime", active_drag="xbox_select", x_range=(dates[0], dates[800]))
ts1.line("Date", "t1", source = source_plot)
ts1.circle("Date", "t1", size=1, source=source_plot, color=None, selection_color="firebrick")

ts2 = figure(width=700, height=250, tools=tools, x_axis_type="datetime", active_drag="xbox_select", x_range=(dates[0], dates[800]))
ts2.x_range = ts1.x_range
ts2.line("Date", "t2", source = source_plot)
ts2.circle("Date", "t2", size=1, source=source_plot, color=None, selection_color="firebrick")

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
    source_plot.data = df
    source_recom_t1.data = load_recom(t1)
    source_recom_t2.data = load_recom(t2)
    ts1.title.text = t1
    ts2.title.text = t2

ticker1.on_change('value', ticker1_change)
ticker2.on_change('value', ticker2_change)

# membuat range tool untuk menggeser timeframe waktu
select = figure(title="Drag the middle and edges of the selection box to change the timeframe",
                plot_height=130, plot_width=800, y_range= ts1.y_range,
                x_axis_type="datetime", y_axis_type=None,
                tools="", toolbar_location=None, background_fill_color="#efefef")

range_tool = RangeTool(x_range= ts1.x_range)
range_tool.overlay.fill_color = "navy"
range_tool.overlay.fill_alpha = 0.2

select.line('Date', 't1', color='red', source=source_plot)
select.line('Date', 't2', color='blue', source=source_plot)
select.ygrid.grid_line_color = None
select.add_tools(range_tool)
select.toolbar.active_multi = range_tool

# Layouts
stock_1 = row(ts1, table_recom_t1)
stock_2 = row(ts2, table_recom_t2)
layout = column(ticker1, stock_1, ticker2, stock_2, select)

# Bokeh Server
curdoc().add_root(layout)
curdoc().title = "stock dashboard"

