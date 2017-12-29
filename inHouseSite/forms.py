from django import forms
from inHouseSite.models import Document

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('document', )