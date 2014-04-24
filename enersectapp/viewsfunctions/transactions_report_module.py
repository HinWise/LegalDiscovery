
from enersectapp.models import *
from django.db import transaction


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

import time
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime

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
            searchtags.append(searchtags_dict)
    

    #print "THIS IS--->" + str(searchtags)
    
    number_of_searchtags = len(searchtags)
   
    if number_of_searchtags>8:
        number_of_searchtags = 8

        
    coincident_transactions = TransactionTable.objects.none()
    
    #Next Segment: Go throught the searchtags list-dictionary and search candidates in the corpus of entries following the chosen tags
    
    coincident_transactions_list = []
    
    with transaction.commit_on_success():
        for item in searchtags:

            if item["tag_name"] == "Unique Transaction Index":
            
                coincident_transactions = TransactionTable.objects.filter(TransactionIndex = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Amount":
            
                coincident_transactions = TransactionTable.objects.filter(Amount__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            
            if item["tag_name"] == "Piece Number":
            
                print "NOPIECE" + item["tag_content"]
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoPiece__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
    
            if item["tag_name"] == "Libdesc":
            
                coincident_transactions = TransactionTable.objects.filter(Libdesc__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))

            if item["tag_name"] == "Company":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Company__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Day":
            
                coincident_transactions = TransactionTable.objects.filter(PostDay = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
            
            if item["tag_name"] == "Month":
            
                coincident_transactions = TransactionTable.objects.filter(PostMonth = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueMonth = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
            if item["tag_name"] == "Year":
            
                coincident_transactions = TransactionTable.objects.filter(PostYear = item["tag_content"]).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueYear = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
            if item["tag_name"] == "Complete Date":
            
                divided_date = item["tag_content"].split("/")
            
                coincident_transactions = TransactionTable.objects.filter(PostDay = divided_date[0],PostMonth = divided_date[1],PostYear = divided_date[2] ).order_by()
                coincident_transactions = coincident_transactions | TransactionTable.objects.filter(ValueDay = divided_date[0],ValueMonth = divided_date[1],ValueYear = divided_date[2] ).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
   
   
            if item["tag_name"] == "Reftran":
            
                coincident_transactions = TransactionTable.objects.filter(Reftran = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Description":
            
                coincident_transactions = TransactionTable.objects.filter(bank_records_list__Description__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Name":
            
                coincident_transactions = TransactionTable.objects.filter(BankName__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Account":
            
                coincident_transactions = TransactionTable.objects.filter(BankAccount__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Bank Currency":
            
                coincident_transactions = TransactionTable.objects.filter(BankCurrency__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))

                
            if item["tag_name"] == "INT Account Number":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__AccountNum__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
                
            if item["tag_name"] == "Exchange Rate":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__ExchangeRate__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))
                
            if item["tag_name"] == "Memo":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__Memo__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
   
            if item["tag_name"] == "Movement Number":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True))  
            
            if item["tag_name"] == "Lett":
            
                coincident_transactions = TransactionTable.objects.filter(internal_records_list__NoMvt__contains = item["tag_content"]).order_by()
                coincident_transactions_list.extend(coincident_transactions.values_list('TransactionIndex',flat=True)) 
   
    coincident_transactions_dict = {}
   
    for item in coincident_transactions_list:
    
        coincident_transactions_dict[str(item)] = coincident_transactions_list.count(item)

    final_coincident_transactions_list = []
    
    for dict_key in coincident_transactions_dict.keys():
    
        temp_dict = {"TransactionIndex":dict_key,"score":coincident_transactions_dict[dict_key]}
        final_coincident_transactions_list.append(temp_dict)

        
    final_list_ordered_score = []
    
    for score in range(number_of_searchtags,0,-1):
    
        temp_dict = {}
        temp_dict["transactions_list"] = [d for d in final_coincident_transactions_list if d['score'] == score]
        temp_dict["score_index"]= str(score);
        final_list_ordered_score.append(temp_dict)
    
    

    tag_types = ["Amount","Piece Number","Company","Day","Month","Year","Complete Date","Libdesc","Description","Reftran",
    "Bank Name","Bank Account","Bank Currency","Unique Transaction Index","Movement Number","INT Account Number","Exchange Rate","Memo","Lett"]
    
    user_templates_list = user_profile.created_transactionsreport_templates.all().values_list('name',flat=True)
    
    context = {"the_user":the_user,'number_of_searchtags': number_of_searchtags,
                'searchtags_string':searchtags_string,'final_list_ordered_score':final_list_ordered_score,"tag_types":tag_types,"searchtags":searchtags,
                'user_templates_list':user_templates_list,"selected_template":selected_template,'selected_candidates_list':selected_candidates_list}
    return render(request,'enersectapp/transactions_report.html',context)
    
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