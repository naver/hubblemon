
#
# Hubblemon - Yet another general purpose system monitor
#
# Copyright 2015 NAVER Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#



import os, socket, sys, time, copy, datetime, threading
import data_loader

hubblemon_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(hubblemon_path)

import test_mon
import common.settings
import common.core
from graph.node import graph_pool


def init_plugin():
	print('# test module init')



def get_chart_data(param):
	print(param)
	# TODO
	return None


def get_chart_list(param):
	print(param)
	return (['cloud', 'instance'], {'cloud_a':['inst_a0', 'inst_a1', 'inst_a2'], 'cloud_b':['inst_b0', 'inst_b1']})


def get_graph_list(param):
	print(param)
	ret = {}
	return (['graph_name'], {'graph1':True, 'graph2':True})

	
def get_graph_data(param):
	print(param)
	name = param['graph_name']

	position = 20 # yaxis
	pool = graph_pool(position)

	root = pool.get_node('root')

	for i in range(0, 10):
		nleaf = pool.get_node('nleaf %d' % i)
		nleaf.link(root)

		for j in range(0, 5):
			leaf = pool.get_node('leaf %d/%d' % (j, i))
			leaf.link(nleaf)

	graph_data  = pool.render()
	return graph_data




