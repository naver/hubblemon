
import os

import common.core
from data_loader.rrd_loader import rrd_loader
from data_loader.loader_util import merge_loader
from data_loader.loader_util import sum_loader
from data_loader.loader_util import filter_loader
from data_loader.loader_util import draw_loader


# rrd

def rrd(path, filter = None, title = ''):
	results = []

	if not path.endswith('.rrd'):
		path += '.rrd'

	try:
		fd = common.core.get_data_handle(path)
		return rrd_loader(fd.path, filter, title)
	except:
		return rrd_loader(None, [])
		
		
# utility
def merge(loaders):
	ret = merge_loader(loaders)
	return ret
	
def sum(loaders):
	ret = sum_loader(loaders)
	return ret

def filter(loaders, *filters):
	ret = filter_loader(loaders, filters)
	return ret
	
def draw(range, *datas):
	ret = draw_loader(range, datas)
	return ret

# add functions to use at chart_page





