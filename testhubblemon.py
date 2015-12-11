

from django.test import TestCase


class SampleTest(TestCase):
	def setUp(self):
		print('setup')

	def test_foo(self):
		print('foo')
		self.assertEqual(1, 1)

	def test_bar(self):
		print('bar')
		self.assertEqual(1, 2)
