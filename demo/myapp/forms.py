from django import forms
from .models import Record

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['text', 'vector']

    def clean_vector(self):
        vector_str = self.cleaned_data['vector']
        vector = [float(x) for x in vector_str.split(',')]
        return vector

class QueryVectorForm(forms.Form):
    vector = forms.CharField(label='Query Vector', help_text='Enter a comma-separated list of three floats')
    k = forms.IntegerField(label='k', initial=5, help_text='Number of similar records to retrieve')
    
class TextSearchForm(forms.Form):
    query = forms.CharField(label='Search', help_text='Enter a search term for trigram similarity search')