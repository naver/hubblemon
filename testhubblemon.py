

from django.test import TestCase
from django.test.client import Client


class LinkTest(TestCase):
	def setUp(self):
		print('setup')

	def test_main(self):
		c = Client()
		resp = c.get('/').content
		print('#resp: ', resp)
	
		self.assertTrue(resp.find(b'system') > 0)
		self.assertTrue(resp.find(b'expr') > 0)
		self.assertTrue(resp.find(b'arcus_graph') > 0)


	def test_list(self):
		c = Client()
		resp = c.get('/system').content
		print('#resp: ', resp)
	
		self.assertTrue(resp.find(b'test.com') > 0)

