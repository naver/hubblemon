
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


from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django import forms
import urllib
import json

import os, time, datetime
from syslog import syslog

import common.settings

from chart.forms import chart_expr_form
from chart.forms import query_form
from jqueryui.jqueryui import *

from common.settings import * # for expr
from common.core import * # for expr
from data_loader.loader_factory import * # for expr

def _make_main_link():
	ret = ''
	for link in common.settings.main_link:
		ret += "<a href='%s'>%s</a>&nbsp&nbsp&nbsp" % (link[1], link[0])
		
	return ret


def _make_time_range(param, link):
	js_chart_list = ''

	if 'start_date' in param:
		script =  jscript("$('#start_date').val('%s');" % (param['start_date']))
		js_chart_list += script.render()

	if 'end_date' in param:
		script =  jscript("$('#end_date').val('%s');" % (param['end_date']))
		js_chart_list += script.render()


	realtime = jquery_radio('realtime')
	realtime.push_item('on')
	realtime.push_item('off')
	action = """
		var s = $(this).attr('id');
		var diff = 0;
		if (s == 'on') {
			window.location.href=%s + '&auto_update=5&diff=5';
		}
		else if (s == 'off') {
			window.location.href=%s;
		}

	""" % (link, link)

	realtime.set_action(action)


	# radio button
	range_radio = jquery_radio('range_radio')
	range_radio.push_item('5m')
	range_radio.push_item('30m')
	range_radio.push_item('1h')
	range_radio.push_item('3h')
	range_radio.push_item('6h')
	range_radio.push_item('12h')
	range_radio.push_item('1d')
	range_radio.push_item('2d')
	range_radio.push_item('1w')
	range_radio.push_item('1M')
	range_radio.push_item('3M')
	range_radio.push_item('6M')
	range_radio.push_item('1Y')
	action = """
		var s = $(this).attr('id');
		var diff = 0;
		if (s == '5m') {
			diff = 5*60;
		}
		else if (s == '30m') {
			diff = 30*60;
		}
		else if (s == '1h') {
			diff = 1*3600;
		}
		else if (s == '3h') {
			diff = 3*3600;
		}
		else if (s == '6h') {
			diff = 6*3600;
		}
		else if (s == '12h') {
			diff = 12*3600;
		}
		else if (s == '1d') {
			diff = 1*3600*24;
		}
		else if (s == '2d') {
			diff = 2*3600*24;
		}
		else if (s == '1w') {
			diff = 1*3600*24*7;
		}
		else if (s == '1M') {
			diff = 1*3600*24*30;
		}
		else if (s == '3M') {
			diff = 3*3600*24*30;
		}
		else if (s == '6M') {
			diff = 6*3600*24*30;
		}
		else if (s == '1Y') {
			diff = 1*3600*24*365;
		}

		var ed = new Date($('#end_date').val());
		var offset = ed.getTimezoneOffset() * 60;
		ed.setSeconds(ed.getSeconds() - offset);
		var end_ts = ed.getTime()/1000;

		var start_ts = end_ts - diff;
		var sd = new Date(start_ts*1000);

		var sd_str = sd.toISOString();
		var date = sd_str.substring(0, 10)
		var time = sd_str.substring(11, 16)
		sd_str = date + " " + time

		$('#start_date').val(sd_str);

		window.location.href=%s + '&start_date=' + $('#start_date').val() + '&end_date=' + $('#end_date').val();
	""" % (link)

	range_radio.set_action(action)


	

	# input & rendering
	date_template = """
		<div class="date_range">
			time range <div id="date_start" style="display:inline">
			<input type="text" id="start_date" value="%s">

			<script type="text/javascript">
			$('#start_date').datetimepicker({
				showSecond: true,
				dateFormat: 'yy-mm-dd',
				timeFormat: 'HH:mm',
				onClose: function(dateTeText, inst) {
						window.location.href=%s + '&start_date=' + $('#start_date').val() + '&end_date=' + $('#end_date').val();
					}
			})
			</script>
			</div>


			&nbsp~&nbsp
			<div id="date_end" style="display:inline">
			<input type="text" id="end_date" value="%s">

			<script type="text/javascript">
			$('#end_date').datetimepicker({
				dateFormat: 'yy-mm-dd',
				timeFormat: 'HH:mm',
				onClose: function(dateTeText, inst) {
						window.location.href=%s + '&start_date=' + $('#start_date').val() + '&end_date=' + $('#end_date').val();
					}
			})
			</script>
			</div>


			&nbsp &nbsp &nbsp
			set start before
			<div id="start_radio" style="display:inline">
			%s
			</div>

			&nbsp &nbsp &nbsp
			realtime
			<div id="start_radio" style="display:inline">
			%s
			</div>
			%s
		</div>

		
	"""

	end_date = datetime.datetime.now()
	start_date = end_date - datetime.timedelta(0, 60*30)
	if 'auto_update' in param:
		try:
			auto_update_time = int(param['auto_update']) * 1000
		except:
			auto_update_time = 5000

		end_date += datetime.timedelta(0, 60)

		auto_update = """
		    <script type="text/javascript">
		    setInterval(function() {
			console.log("update chart");
			var nd = new Date();
			var ed = new Date(nd.getTime() + 60 * 1000);
			var offset = ed.getTimezoneOffset() * 60;
			ed.setSeconds(ed.getSeconds() - offset);
			var end_ts = ed.getTime()/1000;

			var start_ts = end_ts - %s*60;
			var sd = new Date(start_ts*1000);

			var sd_str = sd.toISOString();
			var sd_date = sd_str.substring(0, 10);
			var sd_time = sd_str.substring(11, 16);
			sd_str = sd_date + " " + sd_time;

			$('#start_date').val(sd_str);

			var ed_str = ed.toISOString();
			var ed_date = ed_str.substring(0, 10);
			var ed_time = ed_str.substring(11, 16);
			ed_str = ed_date + " " + ed_time;

			$('#end_date').val(ed_str);

			$.ajax(
			{
			    url : %s + '&start_date=' + $('#start_date').val() + '&end_date=' + $('#end_date').val() + '&auto_update=%d&diff=%s&ajax=true',
			    type : "GET",
			    dataType : 'json',
			    success : function(data) {
				console.log(data.reponse);
				if(data.reponse == 'success') {
				    $('.chart_area').html(data.chart_data);
				}
			    }
			});
		    }, %d);
		    </script>
		"""
		if 'diff' in param:
			auto_update = auto_update %(param['diff'], link, auto_update_time // 1000, param['diff'], auto_update_time)
		else:
			auto_update = auto_update %('30', link, auto_update_time // 1000, '30', auto_update_time)
		js_chart_list += date_template % (start_date.strftime("%Y-%m-%d %H:%M"), link, end_date.strftime("%Y-%m-%d %H:%M"), link, range_radio.render(), realtime.render(), auto_update) # set initial time
	else:
		js_chart_list += date_template % (start_date.strftime("%Y-%m-%d %H:%M"), link, end_date.strftime("%Y-%m-%d %H:%M"), link, range_radio.render(), realtime.render(), '') # set initial time

	return js_chart_list


def _make_static_chart_list(param, url, levels, level_items):
	## list rendering
	js_chart_list = ''
	#print(level_items)

	type = None # chart type
	if 'type' in param:
		type = param['type']

	ac_levels = []
	for i in range(0, len(levels)):
		ac_tmp = jquery_autocomplete(levels[i])
		ac_levels.append(ac_tmp)

	# make link
	if type is not None:
		link = "'/%s?type=%s'" % (url, type)
	else:
		link = "'/%s?'" % (url)

	for i in range(0, len(levels)):
		link = "%s + '&%s=' + %s" % (link, levels[i], ac_levels[i].val())
		

	for i in range(0, len(levels)):
		key_list = level_items[i]

		actions = ac_levels[i].val('ui.item.label') + ';'
		actions += "window.location.href=%s;" % (link)
		ac_levels[i].set(key_list, actions)


	# set script
	for i in range(0, len(levels)):
		js_chart_list += '%s %s &nbsp&nbsp' % (levels[i], ac_levels[i].render())
		

	for i in range(0, len(levels)):
		if levels[i] in param:
			script = jscript(ac_levels[i].val_str(param[levels[i]]) + ';')
			js_chart_list += script.render()


	js_chart_list = '<div class="chart_select">%s</div>' % js_chart_list
	js_chart_list += _make_time_range(param, link)

	return js_chart_list




def _make_dynamic_chart_list(param, url, levels, chart_map):
	## list rendering
	js_chart_list = ''
	#print(chart_map)

	type = None # chart type
	if 'type' in param:
		type = param['type']

	ac_levels = []
	for i in range(0, len(levels)):
		ac_tmp = jquery_autocomplete(levels[i])
		ac_levels.append(ac_tmp)

	link = ''


	if (len(levels) == 1): # only 1 level
		ac_curr = ac_levels[0]
		if type is not None:
			actions = "window.location.href='/%s?type=%s&%s=' + ui.item.label;" % (url, type, levels[0])
		else:
			actions = "window.location.href='/%s?%s=' + ui.item.label" % (url, levels[0])

		key_list = list(chart_map.keys())
		key_list.sort()
		ac_curr.set(key_list, actions)

	else: 			# multi level
		for i in range(0, len(levels)):
			ac_curr = ac_levels[i]
			
			actions = ac_curr.val('ui.item.label') + ';'



			if i < len(levels)-1:			# non-leaf level
				ac_child = ac_levels[i+1]

				if i == 0:
					if type is not None:
						link = "'/%s?type=%s&%s=' + %s" % (url, type, levels[i], ac_curr.val())
					else:
						link = "'/%s?%s=' + %s" % (url, levels[i], ac_curr.val())

					key_list = list(chart_map.keys())
					key_list.sort()
				else:
					link = "%s + '&%s=' + %s" % (link, levels[i], ac_curr.val())
					key_list = []

				actions += ac_child.source(link) + ';'
				actions += ac_child.val_str('') + ';'

				ac_curr.set(key_list, actions)
			else:					# leaf level
				actions = "window.location.href=%s + '&%s=' + ui.item.label;" % (link, levels[i])
				link = "%s + '&%s=' + %s" % (link, levels[i], ac_curr.val()) # used later
				ac_curr.set([], actions)

	# set script
	for i in range(0, len(levels)):
		js_chart_list += '%s %s &nbsp&nbsp' % (levels[i], ac_levels[i].render())
		

	for i in range(0, len(levels)):
		if levels[i] in param:
			script = jscript(ac_levels[i].val_str(param[levels[i]]) + ';')
			js_chart_list += script.render()

	js_chart_list =  '<div class="chart_select">%s</div>' % js_chart_list
	if url != 'graph' and url != 'query':
		js_chart_list += _make_time_range(param, link)

	return js_chart_list


def _get_ts(param):
	end_ts = int(time.time())
	start_ts = end_ts - 60*30

	if 'start_date' in param and param['start_date'] != '':
		start_date = datetime.datetime.strptime(param['start_date'], '%Y-%m-%d %H:%M')
		start_ts = int(start_date.timestamp())

	if 'end_date' in param and param['end_date'] != '':
		end_date = datetime.datetime.strptime(param['end_date'], '%Y-%m-%d %H:%M')
		end_ts = int(end_date.timestamp())

	return start_ts, end_ts


def system_page(request):
	## list rendering
	print('####### system page request ########')
	print(request.GET)

	levels = [ 'server', 'item' ]
	entity_list = []
	item_list = [ 'brief', 'cpu', 'memory', 'swap', 'disk', 'net', 'resource' ]

	entity_list = common.core.get_entity_list()
	#print(entity_list)
	
	entity_list.sort()
	js_chart_list = _make_static_chart_list(request.GET, 'system', levels, [ entity_list, item_list ])

	# chart data
	js_chart_data = ''
	start_ts, end_ts = _get_ts(request.GET)

	if 'server' in request.GET and request.GET['server'] != '' and 'item' in request.GET and request.GET['item'] != '':
		loader = common.core.system_view(request.GET['server'], request.GET['item'])
		chart_data_list = loader.load(start_ts, end_ts)

		js_chart_data = ''
		for chart_data in chart_data_list:
			js_chart_data += chart_data.render()
		
	if 'ajax' in request.GET:
		return HttpResponse(json.dumps({'reponse': 'success', 'chart_data': js_chart_data}), content_type='application/json')

	## make view
	variables = RequestContext(request, { 'main_link':_make_main_link(), 'chart_list':js_chart_list, 'chart_data':js_chart_data } )
	return render_to_response('system_page.html', variables)



def expr_page(request):
	levels, chart_map = common.core.get_chart_list(request.GET) # for init (preload cloud map)

	print('####### expr page request ########')

	if request.method == 'POST':
		param = request.POST
	else:
		param = request.GET
	print(param)

	
	expr = ''
	expr_form = chart_expr_form(data=param)
	if expr_form.is_valid():
		expr = expr_form.cleaned_data['expr']

	print('## expr: %s' % expr)
	## make view

	## eval expression
	js_chart_data = ''
	if request.method == 'POST' and expr != '':
		try:
			x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
			if x_forwarded_for:
				ip = x_forwarded_for.split(',')[0]
			else:
				ip = request.META.get('REMOTE_ADDR')

			syslog('[hubblemon-expr_page:%s] %s' % (ip, query))
			loader = eval(expr)
			#print(loader)

			# allow list or tuple in expr_text
			if isinstance(loader, list) or isinstance(loader, tuple):
				loaders = loader
			else:
				loaders = [loader]
		
			## chart rendering
			start_ts, end_ts = _get_ts(param)

			print(loaders)
			for loader in loaders:
				print(loader)
				if hasattr(loader, 'load'):
					chart_data_list = loader.load(start_ts, end_ts)
					for chart_data in chart_data_list:
						js_chart_data += chart_data.render()
				else:
					js_chart_data += str(loader)
				
		except Exception as e:
			js_chart_data = '''
				<p>evaluation error</p>
				<p>source: %s</p>
				<p>exception: %s</p>
			''' % (expr, str(e))

	## set time range
	start_date = ''
	end_date = ''
	if 'start_date' in param:
		start_date = param['start_date']
	if 'end_date' in param:
		end_date = param['end_date']
	date_range = '''<input type="hidden" name="start_date" value="%s">
			<input type="hidden" name="end_date" value="%s">''' % (start_date, end_date)
	js_chart_list = _make_time_range(param, "'/expr?expr=%s'" % urllib.parse.quote(expr))

	if 'ajax' in param:
		return HttpResponse(json.dumps({'reponse': 'success', 'chart_data': js_chart_data}), content_type='application/json')
	## make view
	variables = RequestContext(request, { 'main_link':_make_main_link(), 'expr_form':expr_form, 'date_range':date_range, 'chart_list':js_chart_list, 'chart_data':js_chart_data} )
	return render_to_response('expr_page.html', variables)


def chart_page(request):
	print('####### chart page request ########')

	param = request.GET
	print(param)

	## list rendering
	levels, chart_map = common.core.get_chart_list(param)
	if (len(levels) == 0):
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'chart_list':'', 'chart_data':'' } )
		return render_to_response('chart_page.html', variables)
	
	js_chart_list = _make_dynamic_chart_list(param, 'chart', levels, chart_map)
	print(levels)
	#print(chart_map)

	# case 1. not selected anyone
	if levels[0] not in param:
		#print('## return chart map')
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'chart_list':js_chart_list } )
		return render_to_response('chart_page.html', variables)

	# case 2. partialy selected
	if levels[-1] not in param:
		ret = chart_map
		for level in levels:
			if level in param:
				if isinstance(ret, dict) and param[level] in ret:
					ret = ret[param[level]]
				else:
					ret = []
					break
			else:
				break

		#print('## return json: ' + json.dumps(ret))
		return HttpResponse(json.dumps(ret))


	# case 3. select all (make data)
	loader = common.core.get_chart_data(param)
	#print(loader)

	if loader == None:
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'chart_data':'Unknown chart id'} )
		return render_to_response('chart_page.html', variables)

	## chart rendering
	start_ts, end_ts = _get_ts(request.GET)
	chart_data_list = loader.load(start_ts, end_ts)

	js_chart_data = ''
	for chart_data in chart_data_list:
		js_chart_data += chart_data.render()

	## make view
	if 'ajax' in param:
		return HttpResponse(json.dumps({'reponse': 'success', 'chart_data': js_chart_data}), content_type='application/json')
	variables = RequestContext(request, { 'main_link':_make_main_link(), 'chart_list':js_chart_list, 'chart_data':js_chart_data } )
	return render_to_response('chart_page.html', variables)


def query_page(request):
	print('####### query page request ########')

	if request.method == 'POST':
		param = request.POST
	else:
		param = request.GET
	print(param)

	auth_fields = ''
	query_data = ''
	query = ''

	if 'query_type' not in param: # initial default value
		param = param.copy()
		param['query_type'] = 'query'

	form = query_form(data=param)
	if form.is_valid():
		query = form.cleaned_data['query']
	print('## query: %s' % query)

	fields = common.core.auth_fields(param)
	for field in fields:
		form.fields[field.label] = field

		auth_fields += field.label
		auth_fields += field.widget.render(field.label, '')
		auth_fields += '&nbsp&nbsp'
		

	## list rendering
	levels, query_map = common.core.get_chart_list(param)
	if (len(levels) == 0):
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'auth_fields':auth_fields, 'query_form':form, 'query_list':'', 'query_data':'' } )
		return render_to_response('query_page.html', variables)
	
	js_query_list = _make_dynamic_chart_list(param, 'query', levels, query_map)
	#print(levels)

	# add hidden fields for form rendering
	if 'type' in param:
		form.fields['type'] = forms.CharField(initial=param['type'], widget=forms.widgets.HiddenInput())
	for level in levels:
		if level in param:
			form.fields[level] = forms.CharField(initial=param[level], widget=forms.widgets.HiddenInput())

	# partialy selected
	if levels[0] in param and levels[-1] not in param:
		ret = query_map
		for level in levels:
			if level in param:
				if isinstance(ret, dict) and param[level] in ret:
					ret = ret[param[level]]
				else:
					ret = []
					break
			else:
				break

		#print('## return json: ' + json.dumps(ret))
		return HttpResponse(json.dumps(ret))

	# execute query
	if request.method == 'POST':	
		x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
		if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
		else:
			ip = request.META.get('REMOTE_ADDR')

		query_data = common.core.query(param, ip)

	variables = RequestContext(request, { 'main_link':_make_main_link(), 'auth_fields':auth_fields, 'query_form':form, 'query_list':js_query_list, 'query_data':query_data} )
	return render_to_response('query_page.html', variables)



def graph_page(request):
	print('####### graph page request ########')

	if request.method == 'POST':
		param = request.POST
	else:
		param = request.GET
	print(param)

	common.core.get_chart_list(param) # for init (dummy)

	## list rendering
	levels, graph_map = common.core.get_graph_list(param)
	if (len(levels) == 0):
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'graph_list':'', 'graph_data':'' } )
		return render_to_response('graph_page.html', variables)

	js_graph_list = _make_dynamic_chart_list(param, 'graph', levels, graph_map)
	#print(levels)

	# return cloud & server list (not selected anyone)
	if levels[0] not in param:
		#print('## return graph map')
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'graph_list':js_graph_list } )
		return render_to_response('graph_page.html', variables)

	# return server list by json (select cloud only)
	if levels[-1] not in param:
		ret = graph_map
		for level in levels:
			if level in param:
				if isinstance(ret, dict) and param[level] in ret:
					ret = ret[param[level]]
				else:
					ret = []
					break
			else:
				break

		#print('## return json: ' + json.dumps(ret))
		return HttpResponse(json.dumps(ret))

	# select could & server
	ret = common.core.get_graph_data(param)
	#print(ret)

	if ret == None or len(ret) == 0:
		variables = RequestContext(request, { 'main_link':_make_main_link(), 'graph_data':'Unknown graph id'} )
		return render_to_response('graph_page.html', variables)

	## make view
	variables = RequestContext(request, { 'main_link':_make_main_link(), 'graph_list':js_graph_list, 'graph_data':ret } )
	return render_to_response('graph_page.html', variables)

def addon_page(request):
	print('####### addon_page request ########')

	if request.method == 'POST':
		param = request.POST
	else:
		param = request.GET

	print(param)
	addon_page_data = common.core.get_addon_page(param)

	variables = RequestContext(request, { 'main_link':_make_main_link(), 'addon_page_data':addon_page_data} )
	return render_to_response('addon_page.html', variables)





