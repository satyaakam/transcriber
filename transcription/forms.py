from django import forms

class YouTubeLinkForm(forms.Form):
    youtube_url = forms.URLField(label='YouTube URL')
