
from enersectapp.models import *
from enersectapp.viewsfunctions import common_functions_module

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response

from django.db import transaction
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime
import time

import random



def pair_randomqa_spider(request):

    '''Audit Notes
    
        Document Type is selected by what the enterers Chose for a Document Type, not the actual, re-categorised Document Type
        
        
    '''
    
    
    the_user = request.user

    if not the_user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
    
    user_type= ""
    
    if len(the_user.groups.filter(name="TeamLeaders")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
    
    elif len(the_user.groups.filter(name="TeamAuditors")) >0:
    
        user_type = "TeamAuditor"
        
    elif len(the_user.groups.filter(name="Auditors")) >0:
    
        user_type = "Auditor"
        
    

    if user_type == "superuser" or user_type == "Auditor":
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
        try:
            selected_modification_author = request.POST['selected_modification_author']
        except (KeyError):
            selected_modification_author =  "all"
            
        try:
            lot_number_check = request.POST['selected_lot']
        except (KeyError):
            lot_number_check =  "all"
        
        try:
            show_progress_mark = request.POST['show_progress_mark']
        except (KeyError):
            show_progress_mark =  "no"
        
        try:
            selected_user = request.POST['selected_user']
        except (KeyError):
            selected_user =  "all"
       
        try:
            selected_doctype = request.POST['selected_doctype']
        except (KeyError):
            selected_doctype =  "all"
        
        try:
            selected_company = request.POST['selected_company']
        except (KeyError):
            selected_company =  "all"
        
        try:
            selected_date = request.POST['selected_date']
        except (KeyError):
            selected_date =  "all"
            
        try:
            selected_auditmark = request.POST['selected_auditmark']
        except (KeyError):
            selected_auditmark =  "all"
        
        '''try:
            filters_panel_width = request.POST['filters_panel_width']
        except (KeyError):
            filters_panel_width =  ""
            
        try:
            filters_panel_height = request.POST['filters_panel_height']
        except (KeyError):
            filters_panel_height =  ""'''
        
        ### Variables necessary to save the new data entry

        try:
            doctype = request.POST['selected_fieldtype_doctype']
        except:
            doctype = "NoDocTypeField"
       
        try:
            currency = request.POST['selected_fieldtype_currency']
        except:
            currency = "NoCurrencyField"
        
        try:
            amount = request.POST['selected_fieldtype_amount']
        except:
            amount = "NoAmountField"
        
        try:
            company_name = request.POST['selected_fieldtype_companyname']
        except:
            company_name = "NoCompanyNameField"
            
        try:
            company_address = request.POST['selected_fieldtype_address']
        except:
            company_address = "NoCompanyAddressField"
            
        try:
            company_telephone = request.POST['selected_fieldtype_telephone']
        except:
            company_telephone = "NoCompanyTelephoneField"
            
        try:
            company_city = request.POST['selected_fieldtype_city']
        except:
            company_city = "NoCompanyCityField"
            
        try:
            company_country = request.POST['selected_fieldtype_country']
        except:
            company_country = "NoCompanyCountryField"
            
        try:
            company_template = request.POST['company_template']
        except:
            company_template = "NoCompanyTemplateField"
        
        try:
            issuedate = request.POST['selected_fieldtype_date']
        except:
            issuedate = "NoIssueDateField"
        
        issuedate_divided = issuedate.split('/')
        
        try:
            issuedate_day = request.POST['issuedate_day']
        except:
        
            if len(issuedate_divided) > 0:
                
                issuedate_day = issuedate_divided[0]
            else:
            
                issuedate_day = "NoIssueDateDayField"
        
        if issuedate_day == "NaN":
            issuedate_day = "MISSING"
        
        try:
            issuedate_month = request.POST['issuedate_month']
        except:
        
            if len(issuedate_divided) > 1:
                
                issuedate_month = issuedate_divided[1]
            else:
            
                issuedate_month = "NoIssueDateMonthField"
                
            
        if issuedate_month == "NaN":
            issuedate_month = "MISSING"
        
        try:
            issuedate_year = request.POST['issuedate_year']
        except:
        
            if len(issuedate_divided) > 2:
                
                issuedate_year = issuedate_divided[2]
            else:
            
                issuedate_year = "NoIssueDateYearField"
            
        
        if issuedate_year == "NaN":
            issuedate_year = "MISSING"
        
        try:
            docnumber = request.POST['selected_fieldtype_docnum']
        except:
            docnumber = "NoDocNumberField"
        
        try:
            memo = request.POST['selected_fieldtype_memo']
        except:
            memo = "NoMemoField"
            
        try:
            translation_memo = request.POST['translation_memo']
        except:
            translation_memo = "NoTranslationField"
            
        try:
            arabic = request.POST['selected_fieldtype_arabic']
        except:
            arabic = "NoArabicField"

        try:
            sourcedoc = request.POST['sourcedoc']
        except:
            sourcedoc = "NoSourceDocField"
            
        try:
            file_name = request.POST['save_filename']
        except:
            file_name = "NoFilenameField"
            
        try:
            purch_order_num = request.POST['selected_fieldtype_purchaseorder']
        except:
            purch_order_num = "NoPurchaseOrderNumberField"
            
        try:
            piece_number = request.POST['selected_fieldtype_piecenum']
        except:
            piece_number = "NoPieceNumberField"
        
        try:
            page_number = request.POST['pagenumber']
        except:
            page_number = "NoPageNumberField"
        
        try:
            accountnum = request.POST['selected_fieldtype_accountnum']
        except:
            accountnum = "NoAccountNumberField"
            
        try:
            chequenum = request.POST['chequenum']
        except:
            chequenum = "NoChequeNumberField"
            
        try:
            receiver = request.POST['receiver']
        except:
            receiver = "NoReceiverField"
            
        try:
            sender = request.POST['sender']
        except:
            sender = "NoSenderField"
        ###
        
        error_rate = 0
        
        pdf_records_list = PdfRecord.objects.none()
        
        user_company = the_user.groups.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
   
        company_names_list = Group.objects.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic").exclude(name="INVENSIS").order_by().values_list('name',flat=True)
   
        if selected_company == "all":
   
            company_list = Group.objects.exclude(name="NathanTeam").exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic").exclude(name="INVENSIS")
        
        else:
        
            company_list = Group.objects.filter(name=selected_company)
        
        
        pdf_lot_number_distinct = SourcePdfToHandle.objects.none()
        
        for company in company_list:
           
            pdf_lot_number_distinct = pdf_lot_number_distinct | SourcePdfToHandle.objects.filter(assignedcompany = company,checked = 'checked').values('lot_number')
           
        
        pdf_lot_number_distinct = pdf_lot_number_distinct.distinct()
        
        
        lot_number_list = []
        pdf_lot_number_distinct_helper = []
        
        for item in pdf_lot_number_distinct:
            if item['lot_number'] not in lot_number_list:
                pdf_lot_number_distinct_helper.append(item)
                lot_number_list.append(item['lot_number'])
        
        pdf_lot_number_distinct = pdf_lot_number_distinct_helper
        
                
        
        #Filling a Lot Numbers in the Company List
        
        lot_number_list = []
        
        if lot_number_check == "all":
            for item in pdf_lot_number_distinct:
                if item['lot_number'] not in lot_number_list:
                    lot_number_list.append(item['lot_number'])
        
        else:
            lot_number_list.append(lot_number_check)
        
        
        pdf_author_distinct = SourcePdfToHandle.objects.none()
        
        for company in company_list:
        
            pdf_author_distinct = pdf_author_distinct | SourcePdfToHandle.objects.filter(assignedcompany = company,checked = 'checked').values('assigneduser__username')
        
        
        pdf_author_distinct = pdf_author_distinct.values_list('assigneduser__username',flat=True).distinct()
        
        user_names_list = []
        
        if selected_user == "all":
            '''for item in pdf_author_distinct:
                user_names_list.append(item['assigneduser__username'])'''
            
            for lot_num in lot_number_list:
                for company in company_list:
                    pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = company ,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
            
        else:
            user_names_list.append(selected_user)
        
            #Selecting All PdfRecords that have the Lots and Users in their fields in SourcePdfsToHandle
        
            for lot_num in lot_number_list:
                for user_name in user_names_list:
                    pdf_records_list = pdf_records_list | PdfRecord.objects.filter(ocrrecord_link__OcrAuthor__username = user_name,sourcedoc_link__assigndata__lot_number = lot_num,sourcedoc_link__assigndata__checked = "checked")
        
        
        #Making a list of Document Types and selecting the PdfRecords that are of that Document Type (From the Doctype entered, not the actual Doctype)
        
        ''' Disabled temporarily, the ability to choose Audit by Document Type, due to speed limitations
        pdf_doctype_distinct = pdf_records_list.order_by().values('modified_document_type__name').distinct()
        
        Changed for the next line instead: (Delete to return to normal, all types list)
        '''
        pdf_doctype_distinct = PdfRecord.objects.none()
        
        #Delete this line to deactivate selection by Entered Document Types
        
        pdf_doctype_distinct = pdf_records_list.order_by().values('ocrrecord_link__Document_Type').distinct()
        
        pdf_doctype_list = []
        
        if selected_doctype != "all":
            #pdf_doctype_list.append(selected_doctype)
           
            '''for doctype in pdf_doctype_list:
                doctype_class = SourceDocType.objects.filter(name=doctype)[0]
                pdf_records_list = pdf_records_list.filter(modified_document_type=doctype_class)'''
            pdf_records_list = pdf_records_list.filter(ocrrecord_link__Document_Type__iexact = selected_doctype)
        
        
        #Getting rid of Duplicates
        
        pdf_records_list.distinct()
        
        pdf_records_list.exclude(audit_mark = "auditmarked_confirmed_reassignment").exclude(audit_mark = "duplicatemarked_reentered")
        
        #Compare the Time to the selected TimeFrame in Filter
        
        enddate = datetime.datetime.now()
        
        #Changing from naive to timezone to solve the Warning
        
        enddate = enddate.replace(tzinfo=timezone.utc)
        
        if selected_date != "all":
            
            if selected_date == "today":
                startdate = enddate - timedelta(days=2)  

            elif selected_date == "lastdays":
                startdate = enddate - timedelta(days=4)  
            
            elif selected_date == "lastweek":
                startdate = enddate - timedelta(days=7)  
            
            elif selected_date == "lastmonth":
                startdate = enddate - timedelta(days=30)  
            
            elif selected_date == "lastmonths":
                startdate = enddate - timedelta(days=90)
            
            elif selected_date == "lastyear":
                startdate = enddate - timedelta(days=365)
            
            else:
                startdate = enddate - timedelta(days=10000)
            
            pdf_records_list = pdf_records_list.filter(modification_date__range=[startdate, enddate])

        
        #Saving the Audit Marks and making the necessary changes in the database
        #No changes if save_mark is None
        
        try:
            save_mark = request.POST['save_mark']
        except (KeyError):
            save_mark =  "None"
            
        if save_mark is not "None":
            
            user_profile = UserProfile.objects.get(user = the_user)
            
            if save_mark == "auditmarked_as_correct" or save_mark == "auditmarked_as_incorrect":
            
                try:
                    pdf_record_id = request.POST['pdf_record_id']
                except (KeyError):
                    pdf_record_id =  "None"
        
                if pdf_record_id is not "None":
                    recover_pdf = PdfRecord.objects.filter(id=pdf_record_id)[0]
                    if selected_auditmark == "all":
                        recover_pdf.audit_mark = save_mark
                        recover_pdf.modification_author = the_user.username
                        recover_pdf.save()
                        memo_report = "Marked PdfRecord PK."+str(recover_pdf.pk)+" as"+save_mark+"."
                    else:
                        recover_pdf.audit_mark_revision = save_mark
                        recover_pdf.modification_author = the_user.username
                        recover_pdf.save()
                        memo_report = "Revised Mark for PdfRecord PK."+str(recover_pdf.pk)+" from "+recover_pdf.audit_mark+" to "+save_mark+"."
                        
                    report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                    report.save()
                    
                    user_profile.modifiedpdfs_audit_marked.add(recover_pdf)
                    user_profile.save()
        
            elif save_mark == "auditmarked_as_incorrect_reentry":
                
                
                incorrect_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect")
                
                with transaction.commit_on_success():
                    for pdf in incorrect_list:

                        pdf.modification_author = the_user.username
                        pdf.audit_mark = "auditmarked_as_incorrect_reentry"
                        pdf.save()
                        memo_report = "Pressed the Send Incorrect Entries for Re-Entry Button for "+str(len(incorrect_list))+" objs. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                        report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                        report.save()
        
                        
                
        
            elif save_mark == "auditmarked_as_selection_reentry":
               
                with transaction.commit_on_success():
                    for pdf in pdf_records_list:

                        pdf.modification_author = the_user.username
                        pdf.audit_mark = "auditmarked_as_selection_reentry"
                        pdf.save()
                        memo_report = "Pressed the Send All Lots/User Selection for Re-Entry Button for "+str(len(pdf_records_list))+" objs. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                        report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                        report.save()
                    
                        
                    
            elif save_mark == "save_audited_entry":
            
                new_pdf = common_functions_module.save_new_data_entry(doctype,currency,amount,company_name,company_address,company_telephone,
                company_city,company_country,company_template,issuedate,issuedate_day,issuedate_month,issuedate_year,docnumber,
                memo,translation_memo,arabic,sourcedoc,file_name,purch_order_num,piece_number,receiver,sender,page_number,accountnum,chequenum,
                the_user)
                
                new_pdf.audit_mark_saved = "save_audited_entry"
                new_pdf.save()
                
                memo_report = "Pressed the Save Audited Entry Button for PK."+str(new_pdf.id)+" PdfRecord."
                report = Report(report_type="Audit",report_subtype="save_audited_entry",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                report.save()
                
                user_profile.modifiedpdfs_audit_saved.add(new_pdf)
                user_profile.save()
                
        
        #Creating an Editor/Modification Authors List:
        
        modification_authors_selection = User.objects.filter(groups__name="NathanTeam")|User.objects.filter(groups__name="TeamLeaders")|User.objects.filter(groups__name="Auditors")
        modification_authors_list = modification_authors_selection.values_list('username',flat=True).order_by().distinct()
        
        #Selection by Modification Author
        
        pdf_authors_list = pdf_records_list
        
        if selected_modification_author!="all":
            pdf_authors_list = pdf_authors_list.filter(modification_author=selected_modification_author)
           
        if show_progress_mark == "show_progress_mark":
        
            show_progress_mark = "show" 
        
            
            
            if selected_auditmark == "all":
                pdf_total_count = len(pdf_records_list)
                pdf_correct_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_correct"))
                pdf_incorrect_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect"))
            
            else:
                
                pdf_correct_count = len(pdf_authors_list.filter(audit_mark_revision="auditmarked_as_correct"))
                pdf_incorrect_count = len(pdf_authors_list.filter(audit_mark_revision="auditmarked_as_incorrect"))
                
            pdf_reentry_count = len(pdf_authors_list.filter(audit_mark="auditmarked_as_incorrect_reentry")) + len(pdf_authors_list.filter(audit_mark="auditmarked_as_selection_reentry"))
            
            if pdf_correct_count!=0 and pdf_incorrect_count!=0:
                correct = float(pdf_correct_count)
                incorrect = float(pdf_incorrect_count)
                error_rate = incorrect/(correct + incorrect)*100
                error_rate = int(error_rate)
                
            
        else:

            pdf_total_count = 0
            pdf_correct_count = 0
            pdf_incorrect_count = 0
            pdf_reentry_count = 0
            error_rate = 0
            show_progress_mark = "no" 
        

        if selected_auditmark == "all":
            pdf_records_list = pdf_records_list.exclude(audit_mark="auditmarked_as_correct").exclude(audit_mark="auditmarked_as_incorrect").exclude(audit_mark="auditmarked_as_incorrect_reentry").exclude(audit_mark="auditmarked_as_selection_reentry").exclude(audit_mark="auditmarked_confirmed_reassignment")
        elif selected_auditmark == "correct":
            pdf_records_list = pdf_records_list.filter(audit_mark="auditmarked_as_correct").exclude(audit_mark_revision="auditmarked_as_correct").exclude(audit_mark_revision="auditmarked_as_incorrect")
            pdf_total_count = len(pdf_records_list)
        elif selected_auditmark == "incorrect":
            pdf_records_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect").exclude(audit_mark_revision="auditmarked_as_incorrect").exclude(audit_mark_revision="auditmarked_as_correct")
            pdf_total_count = len(pdf_records_list)
        
        pdf_id_list_to_randomize = []
        
        if len(pdf_records_list) > 0:
        
            '''for item in pdf_records_list:
                
                pdf_id_list_to_randomize.append(int(item.id))
            
            
                
            random_id = random.choice(pdf_id_list_to_randomize)
              
            pdf_item_list = PdfRecord.objects.filter(id=random_id)[:1]
            pdf_random_item = pdf_item_list[0]'''
            pdf_random_item = random.choice(pdf_records_list)
            pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item.id)[:1]
            pdf_random_source = pdf_random_item.sourcedoc_link
            pdf_random_company = pdf_random_item.ocrrecord_link.OcrByCompany
            
            pdf_item_list = PdfRecord.objects.none()
            
            '''pdf_random_item = random.choice(pdf_records_list)
            pdf_item_list = PdfRecord.objects.filter(id=pdf_random_item.id)[:1]'''
            
            for company in company_list:
            
                pdf_item_list = pdf_item_list | PdfRecord.objects.filter(sourcedoc_link = pdf_random_source, sourcedoc_link__assigndata__assignedcompany=company).distinct()
            
        
        else:
        
            pdf_item_list = PdfRecord.objects.none()
            pdf_random_item = pdf_item_list
      
        if len(pdf_item_list)>1:
            pdf_item_list = pdf_item_list.order_by('-modification_date')
       
       
        companyname_list = CompanyTemplate.objects.all().order_by('companyname_base').values_list('companyname_base',flat=True).distinct()
       
        document_type_list = SourceDocType.objects.all().order_by('name').values_list('name',flat=True).distinct()
       
        context = {'user_type':user_type,'pdf_random_item':pdf_random_item,
        'pdf_item_list':pdf_item_list,"lot_number":lot_number_check,
        'error_rate':error_rate,'show_progress_mark':show_progress_mark,
        'pdf_doctype_distinct':pdf_doctype_distinct,'modification_authors_list':modification_authors_list,
        'pdf_total_count':pdf_total_count,'pdf_correct_count':pdf_correct_count,'company_names_list':company_names_list,
        'pdf_incorrect_count':pdf_incorrect_count,'pdf_reentry_count':pdf_reentry_count,
        'pdf_lot_number_distinct':pdf_lot_number_distinct,'pdf_author_distinct':pdf_author_distinct,
        'selected_user': selected_user,'selected_doctype': selected_doctype,'selected_company': selected_company,
        'selected_date':selected_date,'selected_modification_author':selected_modification_author,'selected_auditmark':selected_auditmark,
        'filters_panel_width':filters_panel_width,
        'filters_panel_width':filters_panel_height,'company_name':user_company.name,'companyname_list':companyname_list,'document_type_list':document_type_list}
        return render(request,'enersectapp/pair_randomqa_spider.html',context)
    
   
    elif user_type == "TeamLeader" or user_type == "TeamAuditor":
        
        
        user_company = the_user.groups.exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]  
     
        
        selected_modification_author =  user_company.name
        
        try:
            lot_number_check = request.POST['selected_lot']
        except (KeyError):
            lot_number_check =  "all"

            
        try:
            show_progress_mark = request.POST['show_progress_mark']
        except (KeyError):
            show_progress_mark =  "no"
        
        
        ###
        
        
        error_rate = 0
        
        pdf_records_list = PdfRecord.objects.none()
        
        group_profile = GroupProfile.objects.get(group = user_company)
        
        pdf_lot_number_distinct = group_profile.unique_lot_number_list.all().values_list('lot_number',flat=True)
        
        #pdf_lot_number_distinct = SourcePdfToHandle.objects.filter(assignedcompany = user_company).order_by().values_list('lot_number',flat=True).distinct()
        
        #pdf_author_distinct = PdfRecord.objects.filter(ocrrecord_link__OcrByCompany = user_company).values('sourcedoc_link__assigndata__assigneduser__username').distinct()

        
        #Filling a Lot Numbers in the Company List
        
        lot_number_list = []
        
        if lot_number_check == "all":
           
            lot_number_list = pdf_lot_number_distinct
            
            pdf_records_list = PdfRecord.objects.filter(EntryByCompany = user_company).values('ocrrecord_link','sourcedoc_link','sourcedoc_link__job_directory','sourcedoc_link__filename','id','audit_mark_saved','audit_mark_revision','EntryByCompany','AssignedLotNumber').order_by()
        
        else:
            
            lot_number_list.append(lot_number_check)
            
            chosen_lot_number = LotNumber.objects.get(lot_number = lot_number_check)
        
            pdf_records_list = PdfRecord.objects.filter(EntryByCompany = user_company,AssignedLotNumber = chosen_lot_number).values('ocrrecord_link','sourcedoc_link','sourcedoc_link__job_directory','sourcedoc_link__filename','id','audit_mark_saved','audit_mark_revision','EntryByCompany','AssignedLotNumber').order_by()
        
        
        
        try:
            selected_doctype = request.POST['selected_doctype']
        except (KeyError):
            selected_doctype =  "all"
        
        
        if selected_doctype != "all":
            
            pdf_records_list = pdf_records_list.filter(ocrrecord_link__Document_Type__iexact = selected_doctype)

        
        
        #Getting rid of Duplicates
        
        
        pdf_records_list.exclude(audit_mark = "auditmarked_confirmed_reassignment").exclude(audit_mark = "duplicatemarked_reentered")
        
        pdf_records_list.distinct()


        #Saving the Audit Marks and making the necessary changes in the database
        #No changes if save_mark is None
        
        try:
            save_mark = request.POST['save_mark']
        except (KeyError):
            save_mark =  "None"
            
        if save_mark is not "None":
            
            user_profile = UserProfile.objects.get(user = the_user)
            
            if save_mark == "auditmarked_as_correct" or save_mark == "auditmarked_as_incorrect":
            
                try:
                    pdf_record_id = request.POST['pdf_record_id']
                except (KeyError):
                    pdf_record_id =  "None"
        
                if pdf_record_id is not "None":
                    recover_pdf = PdfRecord.objects.filter(id=pdf_record_id)[0]
                    recover_pdf.modification_author = the_user.username
                    recover_pdf.audit_mark = save_mark
                    recover_pdf.save()
                    memo_report = "Marked PdfRecord PK."+str(recover_pdf.pk)+" as"+save_mark+"."
                    report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                    report.save()
                    
                    user_profile.modifiedpdfs_audit_marked.add(recover_pdf)
                    user_profile.save()
        
            elif save_mark == "auditmarked_as_incorrect_reentry":
                
                incorrect_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect")
                
                with transaction.commit_on_success():
                
                    for pdf in incorrect_list:

                        pdf.modification_author = the_user.username
                        pdf.audit_mark = "auditmarked_as_incorrect_reentry"
                        pdf.save()
                        memo_report = "Pressed the Send Incorrect Entries for Re-Entry Button for "+str(len(incorrect_list))+" objs. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                        report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                        report.save()
        
            elif save_mark == "auditmarked_as_selection_reentry":
               
                with transaction.commit_on_success():
                    for pdf in pdf_records_list:

                        pdf.modification_author = the_user.username
                        pdf.audit_mark = "auditmarked_as_selection_reentry"
                        pdf.save()
                        memo_report = "Pressed the Send All Lots/User Selection for Re-Entry Button for "+str(len(pdf_records_list))+" objs. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                        report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                        report.save()
                    
        
            elif save_mark == "auditmarked_confirmed_reassignment":
            
                reentry_list = pdf_records_list.filter(audit_mark="auditmarked_as_incorrect_reentry")|pdf_records_list.filter(audit_mark="auditmarked_as_selection_reentry")
                reentry_list = reentry_list.order_by().distinct()
            
                with transaction.commit_on_success():
                
                    for pdf in reentry_list:

                        to_reassign_handles = pdf.sourcedoc_link.assigndata.filter(assignedcompany=user_company)
                        
                        for handle in to_reassign_handles:
                        
                            handle.checked = "unchecked"
                            handle.save()
                        
                        pdf.audit_mark = "auditmarked_confirmed_reassignment"
                        pdf.save()
                        memo_report = "Pressed the Execute Re-Entry Button, "+str(len(reentry_list))+" elements reassigned. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                        report = Report(report_type="Audit",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                        report.save()
                        
            
        
            elif save_mark == "save_audited_entry":
            
                ### Variables necessary to save the new data entry

                try:
                    doctype = request.POST['selected_fieldtype_doctype']
                except:
                    doctype = "NoDocTypeField"
                    
                try:
                    doctype2 = request.POST['selected_fieldtype_doctype2']
                except:
                    doctype2 = "NoDocType2Field"
               
                try:
                    currency = request.POST['selected_fieldtype_currency']
                except:
                    currency = "NoCurrencyField"
                
                try:
                    amount = request.POST['selected_fieldtype_amount']
                except:
                    amount = "NoAmountField"
                
                try:
                    company_name = request.POST['selected_fieldtype_companyname']
                except:
                    company_name = "NoCompanyNameField"
                    
                try:
                    company_address = request.POST['selected_fieldtype_address']
                except:
                    company_address = "NoCompanyAddressField"
                    
                try:
                    company_telephone = request.POST['selected_fieldtype_telephone']
                except:
                    company_telephone = "NoCompanyTelephoneField"
                    
                try:
                    company_city = request.POST['selected_fieldtype_city']
                except:
                    company_city = "NoCompanyCityField"
                    
                try:
                    company_country = request.POST['selected_fieldtype_country']
                except:
                    company_country = "NoCompanyCountryField"
                    
                try:
                    company_template = request.POST['company_template']
                except:
                    company_template = "NoCompanyTemplateField"
                
                try:
                    issuedate = request.POST['selected_fieldtype_date']
                except:
                    issuedate = "NoIssueDateField"
                
                issuedate_divided = issuedate.split('/')
                
                try:
                    issuedate_day = request.POST['issuedate_day']
                except:
                
                    if len(issuedate_divided) > 0:
                        
                        issuedate_day = issuedate_divided[0]
                    else:
                    
                        issuedate_day = "NoIssueDateDayField"
                
                if issuedate_day == "NaN":
                    issuedate_day = "MISSING"
                
                try:
                    issuedate_month = request.POST['issuedate_month']
                except:
                
                    if len(issuedate_divided) > 1:
                        
                        issuedate_month = issuedate_divided[1]
                    else:
                    
                        issuedate_month = "NoIssueDateMonthField"
                        
                    
                if issuedate_month == "NaN":
                    issuedate_month = "MISSING"
                
                try:
                    issuedate_year = request.POST['issuedate_year']
                except:
                
                    if len(issuedate_divided) > 2:
                        
                        issuedate_year = issuedate_divided[2]
                    else:
                    
                        issuedate_year = "NoIssueDateYearField"
                    
                
                if issuedate_year == "NaN":
                    issuedate_year = "MISSING"
                
                try:
                    docnumber = request.POST['selected_fieldtype_docnum']
                except:
                    docnumber = "NoDocNumberField"
                
                try:
                    memo = request.POST['selected_fieldtype_memo']
                except:
                    memo = "NoMemoField"
                    
                try:
                    translation_memo = request.POST['translation_memo']
                except:
                    translation_memo = "NoTranslationField"
                    
                try:
                    arabic = request.POST['selected_fieldtype_arabic']
                except:
                    arabic = "NoArabicField"

                try:
                    sourcedoc = request.POST['sourcedoc']
                except:
                    sourcedoc = "NoSourceDocField"
                    
                try:
                    file_name = request.POST['save_filename']
                except:
                    file_name = "NoFilenameField"
                    
                try:
                    purch_order_num = request.POST['selected_fieldtype_purchaseorder']
                except:
                    purch_order_num = "NoPurchaseOrderNumberField"
                    
                try:
                    piece_number = request.POST['selected_fieldtype_piecenum']
                except:
                    piece_number = "NoPieceNumberField"
                
                try:
                    page_number = request.POST['pagenumber']
                except:
                    page_number = "NoPageNumberField"
                
                try:
                    accountnum = request.POST['selected_fieldtype_accountnum']
                except:
                    accountnum = "NoAccountNumberField"
                    
                try:
                    chequenum = request.POST['chequenum']
                except:
                    chequenum = "NoChequeNumberField"
            
                try:
                    receiver = request.POST['receiver']
                except:
                    receiver = "NoReceiverField"
                    
                try:
                    sender = request.POST['sender']
                except:
                    sender = "NoSenderField"
            
            
                new_pdf = common_functions_module.save_new_data_entry(doctype,doctype2,currency,amount,company_name,company_address,company_telephone,
                company_city,company_country,company_template,issuedate,issuedate_day,issuedate_month,issuedate_year,docnumber,
                memo,translation_memo,arabic,sourcedoc,file_name,purch_order_num,piece_number,receiver,sender,page_number,accountnum,chequenum,
                the_user)
                

                is_duplicated_list = PdfRecord.objects.filter(sourcedoc_link = new_pdf.sourcedoc_link,EntryByCompany = user_company)
                
                if len(is_duplicated_list) > 0:
                    
                    with transaction.commit_on_success():
                        for item in is_duplicated_list:
                            item.audit_mark_saved = "no_need_audit"
                            item.save()
                 
                sourcedoc = new_pdf.sourcedoc_link
                
                sample_common_pdf = PdfRecord.objects.filter(sourcedoc_link = sourcedoc, EntryByCompany = user_company).exclude(AssignedLotNumber = None)
                
                try:
                    lot_num =  sample_common_pdf[0].AssignedLotNumber
                
                    new_pdf.AssignedLotNumber = lot_num
                
                except:
                    
                    new_lot_num = LotNumber.objects.get(lot_number = 69)
                    new_lot_num.save()
                    
                    new_pdf.AssignedLotNumber = new_lot_num
                
                
                
                new_pdf.audit_mark_saved = "save_audited_entry"
                new_pdf.save()
                
    
                memo_report = "Pressed the Save Audited Entry Button for PK."+str(new_pdf.id)+" PdfRecord."
                report = Report(report_type="Audit",report_subtype="save_audited_entry",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                report.save()
                
                user_profile.modifiedpdfs_audit_saved.add(new_pdf)
                user_profile.save()

        
        ##Re-Entry Confirmation button behaviour. Changes records with audit_mark_saved = "needs_reentry_confirmation" to "being_reentered"
        
        #Commented for new FlatWorld requirements. To make it work for new projects,use the commented version
        #pdf_needs_reentry_confirmation = pdf_records_list.filter(audit_mark_saved = "needs_reentry_confirmation").distinct()
        
        
        if save_mark == "button_reentry_confirmation":
        
            pdf_needs_reentry_confirmation = pdf_records_list.filter(audit_mark_saved = "needs_reentry_confirmation").distinct()
        
            maximum_sample = 2500
        
            sample_to_change = pdf_needs_reentry_confirmation[:2500]
            
            sample_size = len(sample_to_change)
        
            with transaction.commit_on_success():
                for pdf in sample_to_change:
                    
                    to_reassign_handles = pdf.sourcedoc_link.assigndata.filter(assignedcompany=user_company)
                        
                    for handle in to_reassign_handles:
                        
                        handle.checked = "unchecked"
                        handle.save()
                    
                    memo_report = "Pressed the Re-Entry Confirmation button in Audit Tool, "+str(sample_size)+" elements changed. This being PK."+str(pdf.pk)+".Previous mark was:"+pdf.audit_mark
                    pdf.audit_mark_saved = "being_reentered"
                    pdf.save()

                    report = Report(report_type="Audit",report_subtype="audit_reentry_confirmation",report_author=the_user,report_company=user_company,report_date=datetime.datetime.now().replace(tzinfo=timezone.utc),report_memo = memo_report)
                    report.save()
                
        
        
        #show_progress_mark = "show_progress_mark"
        
        if show_progress_mark == "show_progress_mark":
        
        
            pdf_audited = len(pdf_records_list.filter(audit_mark_saved = "save_audited_entry").distinct())
        
            #Commented for new FlatWorld requirements. To make it work for new projects,use the commented version
            #pdf_needs_reentry_confirmation = len(pdf_records_list.filter(audit_mark_saved = "needs_reentry_confirmation").distinct())
            
            pdf_needs_reentry_confirmation = 0
            
            #Commented for new FlatWorld requirements. To make it work for new projects,use the commented version
            #pdf_being_reentered = len(pdf_records_list.filter(audit_mark_saved = "being_reentered").distinct())
            
            pdf_being_reentered = 0
            
            #pdf_records_list = pdf_records_list.filter(audit_mark_saved = "awaiting_audit").distinct()
            pdf_records_list = pdf_records_list.filter(audit_mark_saved = "awaiting_audit").distinct()
            
            pdf_left_to_audit = len(pdf_records_list)
            
            pdf_total_count = pdf_left_to_audit + pdf_audited + pdf_needs_reentry_confirmation + pdf_being_reentered
           
            
        else:

            pdf_records_list = pdf_records_list.filter(audit_mark_saved = "awaiting_audit").distinct()
            pdf_total_count = 0
            show_progress_mark = "no" 
            pdf_left_to_audit = 0
            pdf_audited=0
            pdf_needs_reentry_confirmation = 0
            pdf_being_reentered = 0
        
      
        
        pdf_id_list_to_randomize = []
        
        
        if pdf_records_list:
        
            
            number_reps = 5
            
            
            pdf_random_item = random.choice(pdf_records_list)
           
            
            pdf_item_list = PdfRecord.objects.filter(sourcedoc_link=pdf_random_item['sourcedoc_link'],EntryByCompany = user_company)
            
            
        
        else:
        
            pdf_item_list = PdfRecord.objects.none()
            pdf_random_item = pdf_item_list
        
       
        if len(pdf_item_list)>1:
            pdf_item_list = pdf_item_list.order_by('-modification_date')

        
        
        companyname_list = CompanyTemplate.objects.all().order_by('companyname_base').values_list('companyname_base',flat=True).distinct()
        #companyname_list = CompanyTemplate.objects.none()
       
        document_type_list = SourceDocType.objects.all().order_by('name').values_list('name',flat=True).distinct()
        
        document_type_tags_list = ["cheque","invoice","facture","cheque_stub","receipt"]
        
        context = {'user_type':user_type,'pdf_random_item':pdf_random_item,
        'pdf_item_list':pdf_item_list,"lot_number":lot_number_check,'show_progress_mark':show_progress_mark,
        
        'pdf_total_count':pdf_total_count,'pdf_left_to_audit':pdf_left_to_audit,'pdf_audited':pdf_audited,
        'pdf_needs_reentry_confirmation':pdf_needs_reentry_confirmation,
        'pdf_being_reentered':pdf_being_reentered,'pdf_lot_number_distinct':pdf_lot_number_distinct,
        'company_name':user_company.name,'companyname_list':companyname_list,'document_type_list':document_type_list,
        'document_type_tags_list':document_type_tags_list,"selected_doctype":selected_doctype}
        return render(request,'enersectapp/pair_randomqa_spider.html',context)
    
    else:
    
        return HttpResponseRedirect(reverse('enersectapp:main', args=()))  