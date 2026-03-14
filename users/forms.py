from django import forms

class UploadForm(forms.Form):
    pdf_file = forms.FileField()
    subject = forms.CharField(max_length=100)
    level = forms.ChoiceField(choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')])
    num_mcqs = forms.IntegerField(min_value=1, max_value=20)
