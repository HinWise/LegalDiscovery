
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from docreader.models import Doctoread
import re

def doctoreadtool(request):
    
    '''try:
        document_type = request.POST['doctype']
        
    except (KeyError):
    
        document_type='Document Type'''
    
    file = Doctoread.objects.all()
    file = file.filter(checked="unchecked").order_by('filename')[:1]
    print file
    
    context = {'file':file}
    return render(request,'docreader/docreader.html',context)

def doctoreadtool_savedata(request):
   
    '''try:
        sourcedoc = request.POST['sourcedoc']
    except:
        sourcedoc = "NoSourceDocField"'''
    

    '''control_rec = Record.objects.get(name="ControlRecord")
    
    if(doctype == "Blank"):
        new_ocr.Blank = "Blank"
        new_ocr = OcrRecord(Amount="Blank",Currency="Blank",Company="Blank",Address="Blank",City="Blank",Telephone="Blank",Source_Bank_Account="Blank",Document_Type="Blank",IssueDate="Blank",ContainsArabic="Blank",Blank="Blank",Doc_Name="Blank",Notes="Blank",Unreadable="Blank")
    
    else:
        new_ocr = OcrRecord(Amount=amount,Currency=currency,Company=company_name,Address=company_address,City=company_city,Telephone=company_telephone,Source_Bank_Account=sourcedoc,Document_Type=doctype,IssueDate=issuedate,ContainsArabic=arabic,Blank="none",Doc_Number=docnumber,Notes=memo,Unreadable="no")
    

    new_ocr.save()
    
    new_pdf = PdfRecord(record_link=control_rec,ocrrecord_link=new_ocr)
    
    new_pdf.save()'''
    
    return HttpResponseRedirect(reverse('docreader:doctoreadtool', args=()))