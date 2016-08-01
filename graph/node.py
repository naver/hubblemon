
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

import random

class graph_pool:
	def __init__(self, position):
		self.map = {}
		self.lists = []
		self.renderer = cytoscape_renderer()
		self.position = position;
		self.description = '__None__'
	
	def get_node(self, name):
		if name in self.map:
			return self.map[name]

		node = graph_node(name)
		self.map[name] = node
		self.lists.append(node)
		return node

	def render(self):
		result = self.renderer.render(self)
		return result


class graph_node:
	def __init__(self, id, name='', data_list=None):
		self.id = id 
		if name == '':
			self.name = id
		else:
			self.name = name

		self.links = []
		self.color = 'EEEEEE'

		# for Test
		#data_list = []
		#for i in range(16):
		#	data_list.append(random.randrange(0,10))

		if data_list is not None:
			result_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			
			total = 0
			i=0
			for val in data_list:
				total += val
				result_list[i] = val
				i += 1;
			result_list = list(map(lambda x: x/total*100, result_list))
			self.pie_datas = result_list
		else:
			self.pie_datas = None

	def link(self, node, edge_name='', color='000000'):
		self.links.append( (node.name, edge_name, color) )


class cytoscape_renderer:
	def render(self, pool):
		map = pool.map
		lists = pool.lists
		pos = pool.position

		nodes = ''
		edges = ''
		flag_pie_color = False

		for node in lists:
			if node.pie_datas is not None:
				flag_pie_color = True

				nodes += "{ data: { id:'%s', name:'%s', color: '#%s'" % (node.id, node.name, node.color)
				for i in range(16):
					nodes += ", data"+str(i)+": '%s'" % (node.pie_datas[i])
				nodes += " } },\n"
			else:
				nodes += "{ data: { id:'%s', name:'%s', color: '#%s'} },\n" % (node.id, node.name, node.color)

			link_no = 0
			for link in node.links:
				link_no += 1
				dest = map[link[0]]
				edges += "{ data: { id:'%s', name:'%s', source:'%s', target:'%s', color: '#%s' } },\n" % ('%s_%d' % (node.id, link_no), link[1], node.id, dest.id, link[2])

		#layout = "name: 'concentric'"
		layout = "name: 'breadthfirst'"

		result = ''
		pie_color = ''
		if flag_pie_color:
			pie_color = """
				'pie-size': '90%',
				'pie-1-background-color': '#8956e2',
				'pie-1-background-size': 'data(data0)',
				'pie-2-background-color': '#b556e2',
				'pie-2-background-size': 'data(data1)',
				'pie-3-background-color': '#e056e2',
				'pie-3-background-size': 'data(data2)',
				'pie-4-background-color': '#e256b7',
				'pie-4-background-size': 'data(data3)',
				'pie-5-background-color': '#e2568b',
				'pie-5-background-size': 'data(data4)',
				'pie-6-background-color': '#e25660',
				'pie-6-background-size': 'data(data5)',
				'pie-7-background-color': '#e27756',
				'pie-7-background-size': 'data(data6)',
				'pie-8-background-color': '#e2a356',
				'pie-8-background-size': 'data(data7)',
				'pie-9-background-color': '#e2cf56',
				'pie-9-background-size': 'data(data8)',
				'pie-10-background-color': '#c8e256',
				'pie-10-background-size': 'data(data9)',
				'pie-11-background-color': '#9de256',
				'pie-11-background-size': 'data(data10)',
				'pie-12-background-color': '#71e256',
				'pie-12-background-size': 'data(data11)',
				'pie-13-background-color': '#56e266',
				'pie-13-background-size': 'data(data12)',
				'pie-14-background-color': '#56e292',
				'pie-14-background-size': 'data(data13)',
				'pie-15-background-color': '#56e2bd',
				'pie-15-background-size': 'data(data14)',
				'pie-16-background-color': '#56dae2',
				'pie-16-background-size': 'data(data15)'
			"""
		result = self.get_template() % (pos, pos, pos, pos, pos, pos, pool.description, pos, pie_color, nodes, edges,layout, pos)
		return result
		
					
		

	def get_template(self):
		graph_template = '''
		<style>
		#cy_%d {
		  height: 100%%;
		  width: 80%%;
		  position: absolute;
		  left: 0;
		  top: %d%%;
		  border-top: 3px solid #ccc;
		  border-right: 1px solid #ccc;
		}
		#desc_%d {
		  height: 100%%;
		  width: 20%%;
		  position: absolute;
		  left: 80%%;
		  top: %d%%;
		  border-top: 3px solid #ccc;
		}
		</style>

		<div id="cy_%d"></div>
		<div id="desc_%d">%s</div>
		

	       <script type="text/javascript">
			$(function(){ // on dom ready
				$('#cy_%d').cytoscape({
				  style: [
				    {
				      selector: 'node',
				      css: {
					'content': 'data(name)',
					'text-valign': 'center',
					'text-halign': 'center',
					'background-color': 'data(color)',
					
					 %s
					}
				    },
				    {
				      selector: '$node > node',
				      css: {
					'padding-top': '10px',
					'padding-left': '10px',
					'padding-bottom': '10px',
					'padding-right': '10px',
					'text-valign': 'top',
					'text-halign': 'center'
				      }
				    },
				    {
				      selector: 'edge',
				      css: {
					'target-arrow-shape': 'triangle',
					'content': 'data(name)',
					'line-color': 'data(color)',
					'target-arrow-color': 'data(color)',
					'source-arrow-color': 'data(color)'
				      }
				    },
				    {
				      selector: ':selected',
				      css: {
					'background-color': 'black',
					'line-color': 'black',
					'target-arrow-color': 'black',
					'source-arrow-color': 'black',
					
					}
				    }
				  ],

				  elements: {
				    nodes: [ %s ],
				    edges: [ %s ]
				  },

				  layout: { %s, spacingFactor: 0.4 },
				  
  				  minZoom: 0.5,
  				  maxZoom: 3,
  				  
				  ready : function() {
				  	
					$('#cy_%d').cytoscapeNavigator({
					});
			
				   /* cy.on('mouseup', function(event){
				      if (event.cyTarget === cy) {
					  console.log('background');
				      }
				      else {
					console.log(event.cyTarget.position());
					console.log(event.cyTarget.id());
				      }
				    }); */ 
				  },
	
				});
				  			
				/*console.log(cy.$('#b').position());*/
				
			}); // on dom ready
		</script>
		'''

		return graph_template
	
			
