# myapp/forms.py
from django import forms

class MyForm(forms.Form):
    name = forms.CharField(max_length=100)
    file_url = forms.URLField(label="Google Sheet Url", required=True)
    email = forms.EmailField()