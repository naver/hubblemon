
from django import forms

class chart_expr_form(forms.Form):
	expr = forms.CharField(label = 'expr', required=False)

CHOICES = (('query', 'query'), ('eval', 'eval'))

class query_form(forms.Form):
	query = forms.CharField(label = 'query', required=False, widget=forms.Textarea)
	query_type = forms.ChoiceField(label = 'query_type', required=True, choices = CHOICES, widget=forms.RadioSelect())

