# translation_app/models.py
from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    translated_file = models.FileField(upload_to='translated_files/', blank=True, null=True)
