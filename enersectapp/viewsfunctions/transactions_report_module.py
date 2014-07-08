
from enersectapp.models import *
from django.db import transaction

from django.db.models import Count

from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import tempfile

import json
from django.core import serializers

import time
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime

import io
import django.utils.simplejson as json

def transactions_report(request):
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    the_user = request.user
   
       
    #searchtags = ['amount','doctype','date','account','memo','reftran','libelle','account']
    
    searchtags = []
    
    #Example searchtags_string: "Amount:1000,Piece_Number:120"
    

    try:
        action_button_pressed = request.POST['action_button_pressed']
    except:
        action_button_pressed = ""
    
    try:
        selected_template = request.POST['selected_template']
    except:
        selected_template = ""
        
    try:
        searchtags_string = request.POST['searchtags_string']
    except:
        searchtags_string = ""
        
    try:
        selected_transactions_list_string = request.POST['selected_transactions_list_string']
    except:
        selected_transactions_list_string = ""
    
    user_profile = UserProfile.objects.get(user = the_user);
    
    try:
        chosen_template = user_profile.created_transactionsreport_templates.get(name = selected_template)
    except:
        chosen_template = TransactionsReportTemplate.objects.none()
    
    selected_candidates_list = []
    
    if action_button_pressed == "generate_report":
  
        #Make a list with the searchtags
    
        searchtags_fields = []
    
        if searchtags_string:
    
            searchtags_fields = searchtags_string.split("+")

        #Making the query that includes all selected candidate TransactionTables, then write the Report PDF

        selected_transactions = TransactionTable.objects.none()
        
        if len(selected_transactions_list_string):
        
            selected_transactions_list = selected_transactions_list_string.split(',')
            
            for transaction_index in selected_transactions_list:
            
                selected_transactions = selected_transactions | TransactionTable.objects.filter(TransactionIndex = int(transaction_index))
    
        #Initialize the Pdf to be written
        
        output = PdfFileWriter()
    
        title_string = "Transactions Report ; Contains "+str(len(selected_transactions))+" elements.\n\n"
        
        # Build the string for the searchtags:
       
        searchtags_line = "Search tags used: "
        
        for searchtag in searchtags_fields:
        
            try:
                                                    
                try:
                    
                    if (len(searchtags_line.split("\n")[-1]) + len(" "+str(searchtag)+" ")) > 80:
                        test_string = "\n"
                        test_string2 = ".              -"
                    else:
                        test_string = ""
                        test_string2 = ""
                      
                    searchtags_line += " "+test_string+test_string2+str(searchtag)+" "
                      
                except:
                    test_string = ""
                
            except:
                searchtags_line += " "
        
        title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))
    
        response = HttpResponse(mimetype="application/pdf")
        response['Content-Disposition'] = 'attachment; filename=transactions_report_%s.pdf' %(title_date)
    
        
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
                
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
        string_to_pdf(the_canvas,title_string+searchtags_line)
               
        the_canvas.save()
                        
        input1 = PdfFileReader(tmpfile)
                
        output.addPage(input1.getPage(0))
        
    
        #Ready to make the writing to the PDF loop
                                
        #Exhibit Title Pages + Pdfs Loop
        
        pdf_string = ""
        
        for transaction_item in selected_transactions:
                                
            pdf_string += "Transaction "+str(transaction_item.TransactionIndex)+": "
                                                            
            pdf_string = add_to_string_or_split(pdf_string,"Number Linked Bank Records: "+str(transaction_item.NumberBankRecordIndexes));
            pdf_string = add_to_string_or_split(pdf_string,"Number Linked Internal Records: "+str(transaction_item.NumberInternalRecordIndexes));
            pdf_string = add_to_string_or_split(pdf_string,"Amount: "+str(transaction_item.Amount));
            pdf_string = add_to_string_or_split(pdf_string,"Amount Discrepancy: "+str(transaction_item.AmountDiscrepancy));
            pdf_string = add_to_string_or_split(pdf_string,"PostDay: "+str(transaction_item.PostDay));
            pdf_string = add_to_string_or_split(pdf_string,"PostMonth: "+str(transaction_item.PostMonth));
            pdf_string = add_to_string_or_split(pdf_string,"PostYear: "+str(transaction_item.PostYear));
            pdf_string = add_to_string_or_split(pdf_string,"ValueDay: "+str(transaction_item.ValueDay));
            pdf_string = add_to_string_or_split(pdf_string,"ValueMonth: "+str(transaction_item.ValueMonth));
            pdf_string = add_to_string_or_split(pdf_string,"ValueYear: "+str(transaction_item.ValueYear));
            pdf_string = add_to_string_or_split(pdf_string,"Date Discrepancy: "+str(transaction_item.DateDiscrepancy));
            pdf_string = add_to_string_or_split(pdf_string,"Libdesc: "+str(transaction_item.Libdesc));
            pdf_string = add_to_string_or_split(pdf_string,"Reftran: "+str(transaction_item.Reftran));
            pdf_string = add_to_string_or_split(pdf_string,"BankAccount: "+str(transaction_item.BankAccount));
            pdf_string = add_to_string_or_split(pdf_string,"BankName: "+str(transaction_item.BankName));
            pdf_string = add_to_string_or_split(pdf_string,"BankCurrency: "+str(transaction_item.BankCurrency));

                   
            pdf_string += '\n'
            pdf_string += '\n'
            
            if pdf_string.count('\n') > 37:
            
                tmpfile = tempfile.SpooledTemporaryFile(1048576)
                # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                tmpfile.rollover()
                
                the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                string_to_pdf(the_canvas,pdf_string)
                       
                the_canvas.save()
                        
                input1 = PdfFileReader(tmpfile)
                
                output.addPage(input1.getPage(0))
                
                pdf_string = ""
            
            
        tmpfile = tempfile.SpooledTemporaryFile(1048576)
        # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
        tmpfile.rollover()
        
        the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
        string_to_pdf(the_canvas,pdf_string)
               
        the_canvas.save()
                
        input1 = PdfFileReader(tmpfile)
        
        output.addPage(input1.getPage(0))
        
        
        #Finalize the report document
            
        outputStream = StringIO()
        output.write(outputStream)
        

        response.write(outputStream.getvalue())
        return response 
            

    
    elif action_button_pressed == "add_template":
    
        #If template already exists
        if chosen_template:
            
            saved_searchtag_string = chosen_template.searchtag_string
            
            #If there are searchtags to save
            if len(searchtags_string):
            
                #If there were already search tags saved before
                if len(saved_searchtag_string):
                
                    new_searchtag_string = saved_searchtag_string + "+" + searchtags_string
                
                else:
                
                    new_searchtag_string = searchtags_string
                
                #Getting rid of duplicates by converting it into a set, then back to a list
                
                splitted_searchtags_fields = new_searchtag_string.split("+")
                print splitted_searchtags_fields
                splitted_searchtags_fields = set(splitted_searchtags_fields)
                print splitted_searchtags_fields
                splitted_searchtags_fields = list(splitted_searchtags_fields)      
                print splitted_searchtags_fields               
                
                index = 0
                new_searchtag_string = ""
                
                for searchtag_field in splitted_searchtags_fields:
                
                    if index != 0:
                        new_searchtag_string += "+"
                    
                    new_searchtag_string += str(searchtag_field)
                    
                    index +=1
                
                print new_searchtag_string 
                
                Transactions_Report_Template = chosen_template
                Transactions_Report_Template.modification_date = datetime.datetime.now().replace(tzinfo=timezone.utc)
                Transactions_Report_Template.searchtag_string = new_searchtag_string
                Transactions_Report_Template.save()
                
                
        #Template doesn't exist, create a new template with the chosen name
        else:
            #If the name is the default "New Template" name, generate a not used one
            if selected_template == "New Template":
            
                template_names_list = user_profile.created_transactionsreport_templates.all().values_list("name",flat = True)
                print template_names_list
            
                template_exists = True
                count = 1
                
                while template_exists == True:
                
                    name = "Unnamed Template "+str(count)
                    template_exists = name in template_names_list
                    count += 1
                
                selected_template = name
            #Independently of the name being default or not, create a new Transactions Report Template
            
            template_name = selected_template
      
            Transactions_Report_Template = TransactionsReportTemplate(name=template_name)
            Transactions_Report_Template.creation_date = datetime.datetime.now().replace(tzinfo=timezone.utc)
            Transactions_Report_Template.creation_user = the_user
            Transactions_Report_Template.searchtag_string = searchtags_string
            Transactions_Report_Template.save()
            
            user_profile.created_transactionsreport_templates.add(Transactions_Report_Template)
            

        #This block attempts to add all selected Transactions to the Template, independently of it existing before or not
        #ManyToMany takes care of duplicates by default :)
        if len(selected_transactions_list_string):
            
            selected_transactions_list = selected_transactions_list_string.split(',')
            
            for transaction_index in selected_transactions_list:
            
                transaction_item = TransactionTable.objects.get(TransactionIndex = int(transaction_index))
                
                Transactions_Report_Template.selected_transactions.add(transaction_item)
                
        
        print action_button_pressed
    
    elif action_button_pressed == "load_template":
    
        if chosen_template:
    
            selected_candidates_list = chosen_template.selected_transactions.all().values_list('TransactionIndex',flat=True)
            searchtags_string = chosen_template.searchtag_string
    
        print action_button_pressed
        
        
        
    elif action_button_pressed == "remove_template":
    
        if chosen_template:
        
            chosen_template.delete()

            selected_template = ""
    
        print action_button_pressed
        
        
    
    if searchtags_string:
    
        searchtags_fields = searchtags_string.split("+")
        
        #Getting rid of duplicates by converting it into a set, then back to a list
                
        searchtags_fields = set(searchtags_fields)
        searchtags_fields = list(searchtags_fields)        
        
        for searchtag_fields in searchtags_fields:
        
            searchtag = searchtag_fields.split(":")
        
            searchtags_dict = {}
            searchtags_dict["tag_name"] = searchtag[0]
            searchtags_dict["tag_content"] = searchtag[1]
            searchtags_dict["tag_operator"] = searchtag[2]
            searchtags.append(searchtags_dict)
    

    #print "THIS IS--->" + str(searchtags)
    
    number_of_searchtags = len(searchtags)
   
    if number_of_searchtags>8:
        number_of_searchtags = 8

        
    coincident_transactions = TransactionTable.objects.none()
    
    #Next Segment: Go throught the searchtags list-dictionary and search candidates in the corpus of entries following the chosen tags
    
    coincident_transactions_list = []
    
    base_fields_searched = ["TransactionIndex","Amount","CompleteValueDate"]
    internal_fields_searched = []
    bank_fields_searched = []
    
    all_coincident_transactions = TransactionTable.objects.none()
    
    with transaction.commit_on_success():
        for item in searchtags:
            
            if item["tag_name"] == "Unique Transaction Index":
            
                coincident_transactions = TransactionTable.objects.filter(TransactionIndex = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
            
            if item["tag_name"] == "Amount":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(Amount__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(Amount__contains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(Amount__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(Amount__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(Amount__contains = item["tag_content"]).order_by()
                
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex', flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Amount" not in base_fields_searched:
                    base_fields_searched.append("Amount")
            
            
            if item["tag_name"] == "Piece Number":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__contains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__NoPiece__contains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "NoPiece" not in internal_fields_searched:
                    internal_fields_searched.append("NoPiece")
    
            if item["tag_name"] == "Libdesc":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(Libdesc__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(Libdesc__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(Libdesc__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(Libdesc__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(Libdesc__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Libdesc" not in base_fields_searched:
                    base_fields_searched.append("Libdesc")

            if item["tag_name"] == "Company":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__Company__icontains = item["tag_content"]).order_by()

                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Company" not in internal_fields_searched:
                    internal_fields_searched.append("Company")
            
            if item["tag_name"] == "Day":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__exact = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__contains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__gt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__lt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(PostDay__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.exclude(ValueDay__contains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "ValueDay" not in base_fields_searched:
                    base_fields_searched.append("ValueDay")
                if "PostDay" not in base_fields_searched:    
                    base_fields_searched.append("PostDay")
        
                
            
            if item["tag_name"] == "Month":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(PostMonth__exact = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(PostMonth__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth__contains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(PostMonth__gt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(PostMonth__lt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(PostMonth__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.exclude(ValueMonth__contains = item["tag_content"]).order_by()
            

                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "ValueMonth" not in base_fields_searched:
                    base_fields_searched.append("ValueMonth")
                if "PostMonth" not in base_fields_searched:
                    base_fields_searched.append("PostMonth")
 
   
            if item["tag_name"] == "Year":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(PostYear__exact = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(PostYear__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear__contains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(PostYear__gt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(PostYear__lt = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(PostYear__contains = item["tag_content"]).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.exclude(ValueYear__contains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "ValueYear" not in base_fields_searched:
                    base_fields_searched.append("ValueYear")
                if "PostYear" not in base_fields_searched:
                    base_fields_searched.append("PostYear")

   
            if item["tag_name"] == "Complete Date":
            
                divided_date = item["tag_content"].split("/")
            

                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__exact = divided_date[0],PostMonth__exact = divided_date[1],PostYear__exact = divided_date[2] ).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__exact = divided_date[0],ValueMonth__exact = divided_date[1],ValueYear__exact = divided_date[2] ).order_by()
                    
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(PostDay__contains = divided_date[0])
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(PostMonth__contains = divided_date[1])
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(PostYear__contains = divided_date[2])
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay__contains = divided_date[0])
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth__contains = divided_date[1])
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear__contains = divided_date[2])
                   
                if item["tag_operator"] == "greater_than":
                    
                    date = divided_date[0]+"/"+divided_date[1]+"/"+divided_date[2]
                
                    coincident_transactions = TransactionTable.objects.filter(CompletePostDate__gt = date).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(CompleteValueDate__gt = date).order_by()
                if item["tag_operator"] == "less_than":
                
                    date = divided_date[0]+"/"+divided_date[1]+"/"+divided_date[2]
                
                    coincident_transactions = TransactionTable.objects.filter(CompletePostDate__lt = date).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.filter(CompleteValueDate__lt = date).order_by()
                if item["tag_operator"] == "exclude":
                
                    date = divided_date[0]+"/"+divided_date[1]+"/"+divided_date[2]
                
                    coincident_transactions = TransactionTable.objects.exclude(CompletePostDate__exact = date).order_by()
                    coincident_transactions = coincident_transactions | TransactionTable.objects.exclude(CompleteValueDate__exact = date).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "ValueDay" not in base_fields_searched:
                    base_fields_searched.append("ValueDay")
                if "PostDay" not in base_fields_searched:
                    base_fields_searched.append("PostDay")
                if "ValueMonth" not in base_fields_searched:
                    base_fields_searched.append("ValueMonth")
                if "PostMonth" not in base_fields_searched:
                    base_fields_searched.append("PostMonth")
                if "ValueYear" not in base_fields_searched:
                    base_fields_searched.append("ValueYear")
                if "PostYear" not in base_fields_searched:
                    base_fields_searched.append("PostYear")
   
            if item["tag_name"] == "Reftran":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(Reftran__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(Reftran__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(Reftran__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(Reftran__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(Reftran__icontains = item["tag_content"]).order_by()
            
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Reftran" not in base_fields_searched:
                    base_fields_searched.append("Reftran")
                
            if item["tag_name"] == "Description":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(bank_records_list__Description__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Description" not in bank_fields_searched:
                    bank_fields_searched.append("Description")
                
            if item["tag_name"] == "Bank Name":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(BankName__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(BankName__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(BankName__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(BankName__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(BankName__icontains = item["tag_content"]).order_by()
            
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Bank Name" not in base_fields_searched:
                    base_fields_searched.append("BankName")
                
            if item["tag_name"] == "Bank Account":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(BankAccount__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(BankAccount__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(BankAccount__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(BankAccount__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(BankAccount__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "BankAccount" not in base_fields_searched:
                    base_fields_searched.append("BankAccount")
                
            if item["tag_name"] == "Bank Currency":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(BankCurrency__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(BankCurrency__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(BankCurrency__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(BankCurrency__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(BankCurrency__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "BankCurrency" not in base_fields_searched:
                    base_fields_searched.append("BankCurrency")
                
            if item["tag_name"] == "INT Account Number":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__AccountNum__icontains = item["tag_content"]).order_by()
    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "AccountNum" not in internal_fields_searched:
                    internal_fields_searched.append("AccountNum")
                
            if item["tag_name"] == "Exchange Rate":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__ExchangeRate__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "ExchangeRate" not in internal_fields_searched:
                    internal_fields_searched.append("ExchangeRate")
                
            if item["tag_name"] == "Memo":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__Memo__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Memo" not in internal_fields_searched:
                    internal_fields_searched.append("Memo")
                
            if item["tag_name"] == "Movement Number":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__NoMvt__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "NoMvt" not in internal_fields_searched:
                    internal_fields_searched.append("NoMvt")
                
            if item["tag_name"] == "Lett":
            
                if item["tag_operator"] == "exact":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Lett__exact = item["tag_content"]).order_by()
                if item["tag_operator"] == "contains":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Lett__icontains = item["tag_content"]).order_by()
                if item["tag_operator"] == "greater_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Lett__gt = item["tag_content"]).order_by()
                if item["tag_operator"] == "less_than":
                    coincident_transactions = TransactionTable.objects.filter(internal_records_list__Lett__lt = item["tag_content"]).order_by()
                if item["tag_operator"] == "exclude":
                    coincident_transactions = TransactionTable.objects.exclude(internal_records_list__Lett__icontains = item["tag_content"]).order_by()
                    
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True)) 
                all_coincident_transactions = all_coincident_transactions | coincident_transactions
                if "Lett" not in internal_fields_searched:
                    internal_fields_searched.append("Lett")
    

    ## Prepares a dictionary that counts the number of duplicates in the list "coincident_transactions_list" made before
    #It is important to have this dictionary as it keeps duplicates, that we will use later to add the Relevance Score to the dicts
    
    coincident_transactions_dict = {}
   
    for item in coincident_transactions_list:
    
        coincident_transactions_dict[str(item)] = coincident_transactions_list.count(item)

       
    ## Prepares the results of the Queryset in objects that contain all the information
    
    coincident_transactions_complete_dict = {}
    
    
    #Create a copy of the selected Queryset, as well as a ValuesQueryset
    #Original queryset keeps the base info (TransactionTable table) as well as the manytomany relationships (InternalRecord and BankRecord)
    #ValuesQuerySet only keep the base info (TransactionTable table)
    
    coincident_transactions_complete = all_coincident_transactions
    coincident_transactions_complete_values = coincident_transactions_complete.values(*base_fields_searched) #Values limited to chosen search tags
        
    #Converting the unicode strings to strings, so javascript doesn't whine when receiving the object    
        
    coincident_transactions_complete_values = unicode_to_str_list(coincident_transactions_complete_values)
    

    #print coincident_transactions_complete_values
    
    
    #Create a dictionary to convert the ValuesQuerySet into a dict, accesible by keys
    
    coincident_transactions_dict_complete_values = {}
    
    #Transforming the "coincident_transactions_complete_values" dictionary into json
    
    with io.open('jsondata.txt', 'w', encoding='utf-8') as f:
        f.write(unicode(coincident_transactions_complete_values))
        #f.write(unicode(json.dumps(coincident_transactions_complete_values, ensure_ascii=False)))
    
    #Loop that takes the id of every item in the queryset and makes it's own searchable dict item that contains that info to be accesed later
    
    for transaction_dict_queryset in coincident_transactions_complete_values:
    
        element_dict = {}
        
        element_dict["complete_info"] = transaction_dict_queryset
        
        #print element_dict
        
        coincident_transactions_dict_complete_values[str(transaction_dict_queryset["TransactionIndex"])] = element_dict
        
    
    #Loop that takes the base info from the previous dictionary, and builds a new dictionary adding the internal records and bank records to it
    #Basically, it's like a QuerySet, but in a dictionary with keys, to allow for instant access by ID later, instead of using a shit ton of "get" Queries
    ## This is THE BIG TIME SAVER
    
    
    for transaction_temp_item in coincident_transactions_complete:
    
        element_dict = {}

        element_dict["complete_item"] = coincident_transactions_dict_complete_values[str(transaction_temp_item.TransactionIndex)]["complete_info"]
        if len(internal_fields_searched):
            element_dict["internal_records"] = unicode_to_str_list(transaction_temp_item.internal_records_list.all().values(*internal_fields_searched))
        else:
            element_dict["internal_records"] = []
        if len(bank_fields_searched):
            element_dict["bank_records"] = unicode_to_str_list(transaction_temp_item.bank_records_list.all().values(*bank_fields_searched))
        else:
            element_dict["bank_records"] = []
        coincident_transactions_complete_dict[str(transaction_temp_item.TransactionIndex)] = element_dict


    final_coincident_transactions_list = []
    
    final_fields_values_list = []
    
    # Last loop; Takes the previously built complete dictionary, and adds the Relevance Score, obtained thanks to the separate list/dictionary in which
    # duplicates are conserved.
    
    for dict_key in coincident_transactions_dict.keys():

        transaction_item = coincident_transactions_complete_dict[dict_key]
    
        temp_dict = {}
        temp_dict["TransactionIndex"] = dict_key
        temp_dict["score"] = coincident_transactions_dict[dict_key]
        temp_dict["complete_item"] = transaction_item["complete_item"]
        temp_dict["internal_records"] = transaction_item["internal_records"]
        temp_dict["bank_records"] = transaction_item["bank_records"]
                
        final_coincident_transactions_list.append(temp_dict)

        
    final_list_ordered_score = []
    
    #Change this variable to modify the final number of elements of the table
    max_range_per_relevance_set = 1000000
    
    for score in range(number_of_searchtags,0,-1):
    
        temp_dict = {}
        
        temp_dict["transactions_list"] = [d for d in final_coincident_transactions_list if d['score'] == score][:max_range_per_relevance_set]
        temp_dict["score_index"]= str(score)
        final_list_ordered_score.append(temp_dict)
    

    tag_types = ["Amount","Piece Number","Company","Day","Month","Year","Complete Date","Libdesc","Description","Reftran",
    "Bank Name","Bank Account","Bank Currency","Unique Transaction Index","Movement Number","INT Account Number","Exchange Rate","Memo","Lett"]
    
    user_templates_list = user_profile.created_transactionsreport_templates.all().values_list('name',flat=True)
    
    #Making a copy of the tag names used without duplicates, for the html table column titles
    
    non_repeated_searchtags = []
    
    for tag in searchtags:
        
        non_repeated_searchtags.append(tag["tag_name"])
    
    temp_repeated_searchtags = list(set(non_repeated_searchtags))

    #Converting the search tags in strings so javascript won't whine when passing the object
    
    non_repeated_searchtags = []
    
    for tag in temp_repeated_searchtags:
    
        non_repeated_searchtags.append(str(tag))
    
    print non_repeated_searchtags

    context = {"the_user":the_user,'number_of_searchtags': number_of_searchtags,
                'searchtags_string':searchtags_string,'final_list_ordered_score':final_list_ordered_score,"tag_types":tag_types,"searchtags":searchtags,
                'non_repeated_searchtags':non_repeated_searchtags,'user_templates_list':user_templates_list,"selected_template":selected_template,'selected_candidates_list':selected_candidates_list,
                }
    return render(request,'enersectapp/transactions_report.html',context)

def unicode_to_str_list(final_list):

    from django.db import transaction

    with transaction.commit_on_success():
        for item in final_list:
            for key,value in item.iteritems():
                
                if type(value) is not int:
                   
                    item[key] = str(value)
                
    return final_list
    
def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.drawString(2,800-(14*times),item)
    
        times +=1
                            

    '''textobject = canvas.beginText()
    textobject.setTextOrigin(2, 800)
    textobject.setFont("Helvetica-Oblique", 14)
    
    # for line in lyrics:
    # textobject.textOut(line)
    # textobject.moveCursor(14,14) # POSITIVE Y moves down!!!
    # textobject.setFillColorRGB(0.4,0,1)
    textobject.textLines(string)
    
    canvas.drawText(textobject)'''
    
def add_to_string_or_split(pdf_string_origin,string_to_add):

    try:
                
        try:
            
            if (len(pdf_string_origin.split("\n")[-1]) + len(" "+str(string_to_add)+" ")) > 80:
                test_string = "\n"
                test_string2 = ".              -"
            else:
                test_string = ""
                test_string2 = ""
              
            pdf_string_origin += " "+test_string+test_string2+str(string_to_add)+" "
              
        except:
            test_string = ""
        
    except:
        pdf_string_origin += " "
        
    return pdf_string_origin