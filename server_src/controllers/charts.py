#!/usr/bin/env python

from core import TermiteCore
from charts.ScatterPlot import ScatterPlot as ScatterPlotModel

def index():
	core = TermiteCore( request, response )
	return core.GenerateResponse()

def ScatterPlot():
	chart = ScatterPlotModel( request, response )
	chart.PrepareChart()
	return chart.GenerateResponse()
