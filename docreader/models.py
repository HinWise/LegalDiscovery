from django.db import models

# Create your models here.

class Doctoread(models.Model):
    job_directory = models.CharField(max_length=300, default="No Job Directory")
    filename = models.CharField(max_length=300, default="No Filename")
    label = models.CharField(max_length=300, default="No Label")
    checked = models.CharField(max_length=300, default="unchecked")
    correct = models.CharField(max_length=300, default="none")
    notes = models.CharField(max_length=300, default="none")
    
    def __unicode__(self):
        return self.filename
        
    class Meta:
        ordering = ['checked']