from django.db import models

# Create your models here.
from django.db import models

class Transcription(models.Model):
    youtube_url = models.URLField()
    transcription_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
