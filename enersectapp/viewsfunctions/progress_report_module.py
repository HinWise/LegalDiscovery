
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

import random

import re
import json,csv

def progress_report(request):

    the_user = request.user
    
    if not request.user.is_authenticated() or (the_user.is_superuser == False and the_user.username != "JamesTL") :
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    try:
        export_mark = request.POST['export_mark']
        
    except (KeyError):
    
        export_mark='none'
    
    super_group = Group.objects.get(name="NathanTeam")
    test_group = Group.objects.get(name="TestGroup")
    invensis_group = Group.objects.get(name="INVENSIS")
    

    # Number of total documents entered
    
    total_pdf_entered_list = PdfRecord.objects.exclude(audit_mark="duplicatemarked_reentered").exclude(audit_mark="auditmarked_confirmed_reassignment").exclude(ocrrecord_link__OcrByCompany=test_group).exclude(ocrrecord_link__OcrByCompany=invensis_group).exclude(ocrrecord_link__OcrAuthor__username="nemot").order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day').distinct()
    
    #total_pdf_entered_list = total_pdf_entered_list[:5000]
    
    total_pdf_entered = len(total_pdf_entered_list)
    
    # Number of total documents rejected
    # Number of entries divided by Country
    
    if export_mark == "export_csv":
    
        date = datetime.datetime.now().strftime("%d_%m_%Y")
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="progress_report_'+date+'".csv"'

        writer = csv.writer(response)
        
        writer.writerow(['Amount', 'IssueDate', 'Day', 'Month', 'Year', 'Currency', 'Company/Beneficiary', 'Piece_Number', 'Document_Number', 'Document_Type',
        'Address', 'Telephone', 'City', 'Country', 'PurchaseOrder_Number', 'Page_Number', 'ContainsArabic', 'Notes','Source_Bank_Account',
        'Cheque_Number','Blank','Unreadable'])
        
        
        for item in total_pdf_entered_list:
        
            try:
                writer.writerow([str(item.ocrrecord_link.Amount), str(item.ocrrecord_link.IssueDate), str(item.ocrrecord_link.Day),str(item.ocrrecord_link.Month),
                str(item.ocrrecord_link.Year),str(item.ocrrecord_link.Currency),str(item.ocrrecord_link.Company),str(item.ocrrecord_link.Piece_Number),
                str(item.ocrrecord_link.Document_Number),str(item.ocrrecord_link.Document_Type),str(item.ocrrecord_link.Address),str(item.ocrrecord_link.Telephone),
                str(item.ocrrecord_link.City),str(item.ocrrecord_link.Country),str(item.ocrrecord_link.PurchaseOrder_Number),str(item.ocrrecord_link.Page_Number),
                str(item.ocrrecord_link.ContainsArabic),str(item.ocrrecord_link.Notes),str(item.ocrrecord_link.Source_Bank_Account),
                str(item.ocrrecord_link.Cheque_Number),str(item.ocrrecord_link.Blank),str(item.ocrrecord_link.Unreadable)])
            except:
                print "FAILED IN --- "+str(item.pk)
            
        return response
        #return HttpResponseRedirect(reverse('enersectapp:progress_report', args=()))  
    
    else:
    
        context = {
        'total_pdf_entered':total_pdf_entered,
        'the_user':the_user}
        
        return render(request,'enersectapp/progress_report.html',context)