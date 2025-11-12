from django.db import models

class Dataset(models.Model):
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    summary = models.JSONField()
    csv_file = models.FileField(upload_to='datasets/', null=True, blank=True)
    pdf_report = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return self.filename