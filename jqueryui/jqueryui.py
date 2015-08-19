
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


class jquery:
	def __init__(self):
		self.scripts = []

	def render(self):
		pass
	
	def autocomplete(self, id):
		ret = jquery_autocomplete(id)
		self.scripts.append(ret)
		return ret

	def button(self, id):
		ret = jquery_button(id)
		self.scripts.append(ret)
		return ret
		
	def selectable(self, id):
		ret = jquery_selectable(id)
		self.scripts.append(ret)
		return ret
	
	def radio(self, id):
		ret = jquery_radio(id)
		self.scripts.append(ret)
		return ret

class jscript:
	def __init__(self, action):
		self.action = action

	def render(self):
		js_template = self.get_js_template()
		return  js_template % (self.action)
		
	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			    $(function() {
				%s;
			    });
			</script>
		'''

		return js_template


class jqueryui:
	def __init__(self, id):
		self.id = id
		self.target = None

	def val(self, v = None):
		if v is None:
			return "$('#%s').val()" % (self.id)
		else:
			return "$('#%s').val(%s)" % (self.id, v)

	def val_str(self, v = None):
		if v is None:
			return "$('#%s').val()" % (self.id)
		else:
			return "$('#%s').val('%s')" % (self.id, v)

	def text(self, v = None):
		if v is None:
			return "$('#%s').text()" % (self.id)
		else:
			return "$('#%s').text(%s)" % (self.id, v)

	def text_str(self, v = None):
		if v is None:
			return "$('#%s').text()" % (self.id)
		else:
			return "$('#%s').text('%s')" % (self.id, v)
	

class jquery_autocomplete(jqueryui):
	def set(self, source, action):
		self.source = source
		self.action = action

	def render(self):
		raw_data = self.source.__repr__()

		js_template = self.get_js_template()
		return  js_template % (self.id, raw_data, self.action, self.id)

	def source(self, url):
		return "$('#%s').autocomplete('option', 'source', %s);" % (self.id, url)
		
	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			    $(function() {
				$('#%s').autocomplete({
				    source: %s,
				    minLength: 0,
				    select: function( event, ui ) {
					%s;
					return false;
				    }
				}).focus(function(){
				    $(this).autocomplete('search', $(this).val())});
			    });
			</script>

			<input type="text" id="%s"> 
		'''

		return js_template


# TODO
class jquery_selectable(jqueryui):
	def __init__(self, id):
		self.id = id
		self.select_list = []

	def push_item(self, item):
		self.select_list.append(item)

	def render(self):
		select_list = ''
		for item in self.select_list:
			select_list += "<li class='ui-widget-content'>%s</li>\n" % item

		js_template = self.get_js_template()
		id = self.id
		return  js_template % (id, id, id, id, id, select_list)

	def get_js_template(self):
		js_template = '''
			<style>
			#%s .ui-selecting { background: #FECA40; }
			#%s .ui-selected { background: #F39814; color: white; }
			#%s { list-style-type: none; margin:0; padding:0; }
			.ui-widget-content { display:inline; margin: 0 0 0 0; padding: 0 0 0 0; border: 1; }
			</style>

			<script type="text/javascript">
			    $(function() {
				$('#%s').selectable();
			    });
			</script>

			<ul id='%s'>
				%s
			</ul>
		'''

		return js_template


class jquery_button(jqueryui):
	def __init__(self, id):
		self.id = id
		self.action = ''

	def set_action(self, action):
		self.action = action

	def render(self):
		js_template = self.get_js_template()
		return  js_template % (self.id, self.action, self.id, self.id)

	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			    $(function() {
				$('#%s').button().click(
					function() {
						%s;
					}
				);
			    });
			</script>

			<button id='%s' float>%s</button>
		'''

		return js_template

class jquery_radio(jqueryui):
	def __init__(self, id):
		self.id = id
		self.action = ''
		self.button_list = []

	def push_item(self, item):
		self.button_list.append(item)

	def set_action(self, action):
		self.action = action

	def render(self):
		button_list = ''
		for item in self.button_list:
			button_list += "<input type='radio' id='%s' name='radio'><label for='%s'>%s</label>" % (item, item, item)

		js_template = self.get_js_template()
		id = self.id
		return  js_template % (id, id, self.action, id, button_list)

	def get_js_template(self):
		js_template = '''
			<script type="text/javascript">
			    $(function() {
				$('#%s').buttonset();
				$('#%s :radio').click(function() {
					%s;
				});
			    });
			</script>

			<ul id='%s' style="display:inline">
				%s
			</ul>
		'''

		return js_template


