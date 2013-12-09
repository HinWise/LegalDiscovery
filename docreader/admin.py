from django.contrib import admin
from docreader.models import Doctoread

class DoctoreadAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Doc Details",               {'fields': ['job_directory','filename','label','checked','correct','notes']}),]
    
    list_display = ('job_directory','filename','label','checked','correct','notes')
    
    
    search_fields = ['job_directory','filename','label','checked','correct','notes']
    

admin.site.register(Doctoread, DoctoreadAdmin)       

