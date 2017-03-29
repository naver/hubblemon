
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

import os
from chart.chart_data import chart_data
import common.settings
import re
              
class basic_loader:
	def __init__(self, handle, filter, title=''):
		self.filter = filter

		self.handle = handle

		self.title = title
		self.data = {}

		self.ts_start = None
		self.ts_end = None

		self.renderer = {}
		flot_line = flot_line_renderer()
		flot_pie = flot_pie_renderer()
		flot_bar = flot_bar_renderer()
		flot_stack = flot_line_renderer()
		self.renderer['default'] = flot_line
		self.renderer['line'] = flot_line
		self.renderer['title'] = title_renderer()
		self.renderer['pie'] = flot_pie
		self.renderer['bar'] = flot_bar
		self.renderer['stack'] = flot_stack

	def count(self, name):
		if self.handle is None:
			return 0

		sum = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				sum += ts_value[1]
		return sum

	def avg(self, name):
		if self.handle is None:
			return 0

		sum = 0
		avg = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				sum += ts_value[1]

			avg = sum / len(item.data)

		return avg

	def max(self, name):
		if self.handle is None:
			return 0

		max = 0

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				if ts_value[1] > max:
					max = ts_value[1]
		return max

	def min(self, name):
		if self.handle is None:
			return 0

		min = sys.maxsize

		if name in self.data:
			chart = self.data[name]
			item = chart.items[0] # should be 1 metric 

			for ts_value in item.data:
				if ts_value == None:
					continue

				if ts_value[1] < min:
					min = ts_value[1]
		return min

	def parse(self, ts_start, ts_end):
		self.ts_start = ts_start
		self.ts_end = ts_end

		if self.handle is None:
			return

		chart_data_list = self.load(ts_start, ts_end)

		self.data = {}
		for chart_data in chart_data_list:
			self.data[chart_data.title] = chart_data

	def make_chart(self, titles, tmap, items, ts_start, ts_step):
		if isinstance(titles, str):
			idx = tmap[titles]
			data = []

			ts_count = 0
			for item in items:
				if ts_start is None:
					ts = item[0] * 1000
				else:
					ts = ts_start + ts_count * ts_step
					ts_count += 1

				if item[idx] == None:
					data.append(None)
					continue

				data.append([ts, item[idx]])

			return [(titles, data)]

		elif isinstance(titles, tuple):
			title = ''

			for func in titles:
				if not hasattr(func, '__call__'):
					title = func

			data = []
			ts_count = 0
			input = { 'prev':{} }

			for item in items:
				if ts_start is None:
					ts = item[0] * 1000
				else:
					ts = ts_start + ts_count * ts_step
					ts_count += 1

				for name, idx in tmap.items():
					input[name] = item[idx]

				for func in titles: # only last function result is saved
					if hasattr(func, '__call__'):
						try:
							output = [ts, func(input)]
						except:
							output = None

				prev = input['prev']
				for k, v in input.items():
					if k == 'prev':
						continue

					if k not in prev:
						prev[k] = []
					
					prev[k].append(v)

				data.append(output)

			return [(title, data)]

		elif isinstance(titles, list):
			ret = []
			for title in titles:
				if isinstance(title, str) and title.startswith('#'):
					continue

				ret += self.make_chart(title, tmap, items, ts_start, ts_step)
		
			return ret

		return []


	def load(self, ts_start, ts_end):
		self.ts_start = ts_start
		self.ts_end = ts_end

		if self.handle is None:
			print ('invalid handle')
			return []

		ret = self.handle.read(ts_start, ts_end)
		#print ('result: ', ret)
		# default(rrd) type ((ts_start, ts_end, step), (metric1, metric2, metric3), [(0, 0, 0), (1, 1, 1)....])
		# rrd type ('#rrd', (ts_start, ts_end, step), (metric1, metric2, metric3), [(0, 0, 0), (1, 1, 1)....])
		# tsdb type ('#timestamp', (metric1, metric2, metric3), [(ts, 0, 0, 0), (ts, 1, 1, 1)....])

		tmap = {}

		if isinstance(ret[0], str):
			if ret[0] == '#timestamp':
				ts_start = None
				ts_step = None

				names = ret[1]
				items = ret[2]
			else:
				ts_start = ret[1][0] * 1000
				ts_step = ret[1][2] * 1000
				
				names = ret[2]
				items = ret[3]

			for i in range(0, len(names)):
				tmap[names[i]] = i+1 # skip 1 for tag

		else:	# implicit rrd style
			ts_start = ret[0][0] * 1000
			ts_step = ret[0][2] * 1000
			
			names = ret[1]
			items = ret[2]

			for i in range(0, len(names)):
				tmap[names[i]] = i

		# for debug
		#print(tmap)
		#print(names)
		#print(items)
			
		# loader title
		chart_data_list = []
		if self.title != '':
			title_chart = chart_data()
			title_chart.title = self.title
			title_chart.renderer = self.renderer['title']
			chart_data_list.append(title_chart)

		if self.filter == None: 	# select all
			self.filter = names

		#print(self.filter)
		for titles in self.filter: # for each chart
			new_chart = chart_data()

			tmp_list = self.make_chart(titles, tmap, items, ts_start, ts_step)
		
			if titles[0]=="#stack":
				for t in range(len(tmp_list))[1:]:
					tmp_data = tmp_list[t][1]
					stack_data=[]
					for i in range(len(tmp_data)):  
						if tmp_data[i] == None:
							stack_data.append(tmp_data[i])
						else:
							prev_data = tmp_list[t-1][1]
							stack_data.append([tmp_data[i][0], (tmp_data[i][1] + prev_data[i][1])])
					
				new_chart.push_data('stack', stack_data)	
			for tmp in tmp_list:
				new_chart.push_data(tmp[0], tmp[1])
			


	

			renderer_name = 'default'
			if isinstance(titles, list) and isinstance(titles[0], str) and titles[0].startswith('#'): # renderer
				renderer_name = titles[0][1:]

			if renderer_name in self.renderer:
				new_chart.renderer = self.renderer[renderer_name]

			chart_data_list.append(new_chart) 

		return chart_data_list


class title_renderer:
	def render(self, chart_data):
		title_template = self.get_title_template()
		return title_template % chart_data.title

	def get_title_template(self):
		title_template = '''
			<div class="chart-seperator" style="clear:both">
				<p>%s</p>
			</div>
		'''

		return title_template


class flot_pie_renderer:
	idx = 1

	def render(self, chart_data):
		chart_data.sampling(common.settings.chart_resolution)

		# adjust timezone if needed
		mode = 'series: {pie: {show: true, radius:1, label: {show:true, radius:2/3, formatter:labelFormatter, threshold:0.1}}}, legend: {show:false}'
		if chart_data.mode == 'time':
			chart_data.adjust_timezone()

		# convert python array to js array
		raw_data = ''
		if len(chart_data.items) == 1: # one item
			item = chart_data.items[-1]
			last_data = list(filter(None.__ne__, item.data))[-1][1]
			raw_data = '{ label: "%s", data: %s }'% (item.title , last_data)
		else: # multi item (display label)
			for item in chart_data.items:
				tmp = list(filter(None.__ne__, item.data))
				if len(chart_data.items) > 7:
					if (item.title != "total"):
						raw_data += '{ label: "%s", data: %s },' % (item.title, tmp[-1][1])
				else:
					if (item.title != "total"):
						raw_data += '{ label: "%s", data: %s },' % (item.title, tmp[-1][1])

		idx = flot_line_renderer.idx + id(chart_data) # to get unique idx
		flot_line_renderer.idx += 1

		js_template = self.get_js_template()
		return  js_template % ('[ %s ]' % raw_data, idx, mode, chart_data.title, idx)

		
	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			// A custom label formatter used by several of the plots

			function labelFormatter(label, series) {
				return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%%</div>";
			}

			$(function(){
				tickFunc = function(val, axis) {
					if (val > 1000000000 && (val %% 1000000000) == 0) {
						return val/1000000000 + "G";
					}
					else if (val > 1000000 && (val %% 1000000) == 0) {
						return val/1000000 + "M";
					}
					else if (val < 1) {
						return Math.round(val*1000)/1000
					}

					return val;
				};

				var data_list = %s;

				$.plot($("#placeholder_%s"), data_list, {
					%s		
				});
			});
			</script>

			<div>
			<div class="chart-container">
				<div class="chart-title">%s</div>
				<div id="placeholder_%s" class="chart-placeholder" style="float:left" align="center">
				</div>
			</div>
			</div>
		'''
		return js_template


class flot_line_renderer:
	idx = 1

	def render(self, chart_data):
		chart_data.sampling(common.settings.chart_resolution)

		# adjust timezone if needed
		mode = ''
		if chart_data.mode == 'time':
			mode = 'xaxis: { mode: "time" }, yaxis: { tickFormatter: tickFunc, min: 0 }, lines: { fillOpacity:1.0, show: true, lineWidth:1 },'
			chart_data.adjust_timezone()

		mode = mode + "cursors: [ { mode: 'x', showIntersections: true, showLabel: false,snapToPlot: 0, symbol: 'diamond', position: { relativeX: 0, relativeY:0} }], grid: {hoverable: true, autoHighlight: false },"
		# convert python array to js array
		raw_data = ''
		if len(chart_data.items) == 1: # one item
			item = chart_data.items[0];
			tmp = list(filter(None.__ne__, item.data))
			tmp = tmp.__repr__()
			raw_data = '{ label: "%s", data: %s}' %(item.title, tmp)
		else: # multi item (display label)
			for item in chart_data.items:
				tmp = list(filter(None.__ne__, item.data))
				tmp = tmp.__repr__()
				if len(chart_data.items) > 7:
					raw_data += '%s,' % tmp
				else:
					raw_data += '{ label: "%s", data: %s },' % (item.title, tmp)

		idx = flot_line_renderer.idx + id(chart_data) # to get unique idx
		flot_line_renderer.idx += 1

		plot_idx = idx
		#plot_idx = 1

		#print (raw_data)
		js_template = self.get_js_template()
		return  js_template % (plot_idx, raw_data, plot_idx, idx, mode, idx, idx, plot_idx, plot_idx, plot_idx, plot_idx, idx, chart_data.title, idx, idx, idx, chart_data.title, idx)

		
	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			var plot_%s;	
			$(function() {
				tickFunc = function(val, axis) {
					if (val > 1000000000 && (val %% 1000000000) == 0) {
						return val/1000000000 + "G";
					}
					else if (val > 1000000 && (val %% 1000000) == 0) {
						return val/1000000 + "M";
					}
					else if (val < 1) {
						return Math.round(val*1000)/1000
					}

					return val;
				};

				var data_list = [%s];
				plot_%s = $.plot("#placeholder_%s", data_list, {
					%s
				});
			});
			</script>

			<script>
			$(function(){
			var legends = $("#placeholder_%s .legendLabel");
			    legends.each(function () {
				// fix the widths so they don't jump around
				$(this).css('width', $(this).width());
			    });

			    var updateLegendTimeout = null;
			    var latestPosition = null;
			    
			    function updateLegend_%s() {
				updateLegendTimeout = null;
				
				var pos = latestPosition;
				var axes = plot_%s.getAxes();
				if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
				    pos.y < axes.yaxis.min || pos.y > axes.yaxis.max)
			    		return;

				var i, j, dataset = plot_%s.getData();
				for (i = 0; i < dataset.length; ++i) {
				    var series = dataset[i];
				    // find the nearest points, x-wise
				    for (j = 0; j < series.data.length; ++j)
					if (series.data[j][0] > pos.x)
					    break;
				    plot_%s.setCursor(plot_%s.getCursors()[0], {position:{x:series.data[j-1][0]}}); 
				    var t = parseFloat(series.data[j-1][0]);
				    var date = new Date(t);// Milliseconds to date
				    date.setTime(t + date.getTimezoneOffset()*60*1000); // timezone offset 	
				    var formatted = date.toTimeString().replace(/.*(\d{2}:\d{2}:\d{2}).*/, "$1"); // change time format as HH:MM:SS
				    $("#chart-title-%s").text("%s x = "+formatted);
				}
			    }	
			var placeholder = $("#placeholder_%s");
			placeholder.bind("plothover",  function (event, pos, item) {
				latestPosition = pos;
				if (!updateLegendTimeout)
				    updateLegendTimeout = setTimeout(updateLegend_%s, 50);
			    });
			});

</script>

			<div>
			<div class="chart-container">
				<div id="chart-title-%s" class="chart-title">%s x = 0.00 </div>
				<div id="placeholder_%s" class="chart-placeholder" style="float:left"></div>
			</div>
			</div>
		'''

		return js_template


class flot_bar_renderer:
	idx = 1

	def render(self, chart_data):
		chart_data.sampling(common.settings.chart_resolution)

		# adjust timezone if needed
		mode = ''
		if chart_data.mode == 'time':
			# add click event listener to label
			labelFormatter = '''
                               function(label, series){
					var idx = %s;
					var labelList = %s;
                                        return "<a name=" + "'" + idx + " " + label + " " + labelList + "'" + " onclick='(function(elem){\
									var data = elem.name.split(/ /);\
									var id = data[0];\
									var label = data[1];\
									var labelList = data[2].split(/,/);\
                                                                        var bars = dic_plot[id].getData()[labelList.indexOf(label)].bars;\
									bars.show ? bars.show=false : bars.show=true;\
                                                                        dic_plot[id].draw();\
                                                                })(this)'>" + label + "</a>";
                                }
                        '''

			#set bar width

			#push num1(time in millisecond) which matches '[num1, num2]'
			tmp_data = re.findall('\d+(?=, \d+)', chart_data.items[0].data.__repr__())
			if len(tmp_data) >= 2:
				start_time = int(tmp_data[0])
				end_time = int(tmp_data[-1])
				time_gap = end_time - start_time
				#unit of barWidth = unit of x axis(1 millisecond)
				barWidth = time_gap / len(chart_data.items[0].data) * 0.8
			else:
				barWidth = 1

			mode = 'xaxis: { mode: "time" }, yaxis: { tickFormatter: tickFunc, min: 0 }, bars: { fill: 0.8, show: true, lineWidth: 0, barWidth: %d, fillColors: false}, legend: { labelFormatter: %s }, ' %(barWidth, labelFormatter)


			chart_data.adjust_timezone()

		# convert python array to js array
		raw_data = ''
		labelList = [] # list of all label
		if len(chart_data.items) == 1: # one item
			raw_data = chart_data.items[0].data.__repr__().replace('None', 'null')
		else: # multi item (display label)
			for item in chart_data.items:
				tmp = item.data.__repr__().replace('None', 'null')
				if len(chart_data.items) > 7:
					raw_data += '%s,' % tmp
				else:
					labelList.append(item.title)
					raw_data += '{ label: "%s", data: %s, },' % (item.title, tmp)

		idx = flot_bar_renderer.idx + id(chart_data) # to get unique idx
		flot_bar_renderer.idx += 1

		#print (raw_data)
		js_template = self.get_js_template()
		return  js_template % ('[ %s ]' % raw_data, idx, mode %(idx, labelList), idx, chart_data.title, idx)

		
	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">

			$(function() {
				tickFunc = function(val, axis) {
					if (val > 1000000000 && (val %% 1000000000) == 0) {
						return val/1000000000 + "G";
					}
					else if (val > 1000000 && (val %% 1000000) == 0) {
						return val/1000000 + "M";
					}
					else if (val < 1) {
						return Math.round(val*1000)/1000
					}

					return val;
				};

				var data_list = %s;

				var plot = $.plot("#placeholder_%s", data_list, {
					%s
				});

				if (typeof(dic_plot) == "undefined")	
					dic_plot = Object();
				dic_plot["%s"] = plot;
			});
			</script>

			<div>
			<div class="chart-container">
				<div class="chart-title">%s</div>
				<div id="placeholder_%s" class="chart-placeholder" style="float:left"></div>
			</div>
			</div>
		'''

		return js_template
