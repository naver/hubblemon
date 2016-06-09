
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
	def __init__(self, id, name=''):
		self.id = id 
		if name == '':
			self.name = id
		else:
			self.name = name

		self.links = []
		self.color = 'EEEEEE'

	def link(self, node, edge_name='', color='000000'):
		self.links.append( (node.name, edge_name, color) )


class cytoscape_renderer:
	def render(self, pool):
		map = pool.map
		lists = pool.lists
		pos = pool.position

		nodes = ''
		edges = ''
		datas = [20, 30, 50]
		for node in lists:
			nodes += "{ data: { id:'%s', name:'%s', color: '#%s', datas: '%s' } },\n" % (node.id, node.name, node.color, datas)

			link_no = 0
			for link in node.links:
				link_no += 1
				dest = map[link[0]]
				edges += "{ data: { id:'%s', name:'%s', source:'%s', target:'%s', color: '#%s' } },\n" % ('%s_%d' % (node.id, link_no), link[1], node.id, dest.id, link[2])

		#layout = "name: 'concentric'"
		layout = "name: 'breadthfirst'"

		result = ''

		result = self.get_template() % (pos, pos, pos, pos, pos, pos, pool.description,  pos, nodes, edges,layout, pos)
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
					
					
					'pie-size': '90%%',
        				'pie-1-background-color': '#696969',
        				'pie-1-background-size': function(ele) { return ele.data('datas')[1]+ele.data('datas')[2] },
        				'pie-2-background-color': '#A9A9A9',
        				'pie-2-background-size': function(ele) { return ele.data('datas')[2] },
       					'pie-3-background-color': '#D3D3D3',
       					'pie-3-background-size': function(ele) { return ele.data('datas')[2] }
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
					'target-arrow-color': 'black',
					'source-arrow-color': 'black',
					'pie-size': '95%%',
					'pie-1-background-color': '#E8747C',
        				'pie-2-background-color': '#74CBE8',
        				'pie-3-background-color': '#74E883',
        				'opacity': 1
					
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
	
			
