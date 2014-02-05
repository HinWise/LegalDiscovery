
from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


def save_new_data_entry(doctype,currency,amount,company_name,company_address,company_telephone,
    company_city,company_country,company_template,issuedate,issuedate_day,issuedate_month,issuedate_year,docnumber,
    memo,translation_memo,arabic,sourcedoc,file_name,purch_order_num,piece_number,page_number,accountnum,chequenum,
    the_user):
 

    control_rec = Record.objects.get(name="ControlRecord")
    
    if(doctype!="NoDocTypeField"):
    
        doctype = doctype.lower()
        
        if doctype == "invoice/facture":
            doctype = "invoice"
            
        if doctype == "receipt/recu":
            doctype = "receipt"
            
        if doctype == "contract page 1":
            doctype = "contract page 1"
            
        if doctype == "contract page X":
            doctype = "contract page X"
        
        if doctype == "purchase order/bon de commande":
            doctype = "purchase order"
        
        if doctype == "arabic":
            
            translation_type = "arabic translation"
            

    doctype_class = SourceDocType.objects.filter(name=doctype)[:1]
    
    if (len(doctype_class)>0):
        doctype_class=doctype_class[0]
    else:
        doctype_class = SourceDocType()
        doctype_class.name = doctype
        doctype_class.pretty_name = doctype
        doctype_class.save()
    
    
    if(doctype == "blank"):
        
        new_ocr = OcrRecord(Amount="Blank",Currency="Blank",Company="Blank",Address="Blank",City="Blank",Country="Blank",Telephone="Blank",Source_Bank_Account="Blank",Document_Type="Blank",IssueDate="Blank",Day="Blank",Month="Blank",Year="Blank",ContainsArabic="Blank",Blank="Blank",Notes="Blank",Unreadable="Blank",Document_Number="Blank",PurchaseOrder_Number="Blank",Piece_Number="Blank",Page_Number="Blank",Translation_Notes = "Blank",Cheque_Number = "Blank")
        company_link = CompanyTemplate.objects.get(companyname_base="ControlCompanyTemplate")
    
    else:
        new_ocr = OcrRecord(Amount=amount,Currency=currency,Company=company_name,Address=company_address,City=company_city,Country=company_country,Telephone=company_telephone,Source_Bank_Account=accountnum,Document_Type=doctype,IssueDate=issuedate,Day=issuedate_day,Month=issuedate_month,Year=issuedate_year,ContainsArabic=arabic,Blank="none",Document_Number=docnumber,Notes=memo,Unreadable="no",PurchaseOrder_Number=purch_order_num,Piece_Number=piece_number,Page_Number=page_number,Translation_Notes = translation_memo,Cheque_Number = chequenum)
        
    
    try:
        company_link = CompanyTemplate.objects.filter(companyname_base=company_template)[0]

    except:
        company_link = ""
        
        comp_origin = CompanyOriginal.objects.get(companyname_original="ControlCompanyOriginal")
        company_link = CompanyTemplate(companyname_base=company_name,companyaddress_base=company_address,companytelephone_base=company_telephone ,companycity_base=company_city,companycountry_base=company_country,company_original=comp_origin)
        company_link.save()
           
    
    
    user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
    
    new_ocr.OcrAuthor = the_user
    new_ocr.OcrByCompany = user_group
    new_ocr.OcrCreationDate = datetime.datetime.now().strftime("%d/%m/%Y")
    
    
    source = SourcePdf.objects.get(filename=file_name)
   
    
    if user_group.name == "Enersect_Berlin":
        
        source.modified_document_type = doctype_class
        source.save()
    
    try:
    
        handle = ""
        
        if(the_user.is_superuser == True):
            handle = source.assigndata.get(assigneduser=the_user)
            handle.checked = "checked"
            handle.times_checked = int(handle.times_checked) + 1
            
        else:
            handle = source.assigndata.get(assigneduser=the_user)
            handle.checked = "checked"
            handle.times_checked = int(handle.times_checked) + 1
    
        handle.save()
         
    
    except:
    
        handle = ""
    
    source.save()
    

    new_ocr.save()
    
    #If it is duplicated (Was entered before), mark previous Entries as "Revised"
    
    is_duplicated_list = PdfRecord.objects.filter(sourcedoc_link = source,ocrrecord_link__OcrByCompany = user_group)
    
    if is_duplicated_list.count() > 0:
        
        for item in is_duplicated_list:
            if item.audit_mark != "auditmarked_confirmed_reassignment":
                item.audit_mark = "duplicatemarked_reentered"
                item.save()
    
    translation_type = "no"

    
    if not doctype_class:
        print "ATTENTION!DOC TYPE CLASS NOT SELECTED, views.py Line 1181!"
    
    new_pdf = PdfRecord(modified_doctype_from=doctype,original_document_type=doctype_class,modified_document_type=doctype_class,record_link=control_rec,ocrrecord_link=new_ocr,sourcedoc_link=source,companytemplate_link=company_link,commentary="No modifications",skip_counter='0',audit_mark="None",modification_date=datetime.datetime.now().replace(tzinfo=timezone.utc),modification_author=the_user.username,translated=translation_type)
    
    new_pdf.save()
    
    #Arabic special case, saving the translation in the user that made it
    
    if doctype == "arabic":
            
            user_profile = UserProfile.objects.get(user=the_user)
            
            if len(user_profile.modifiedpdfs_translated_arabic.filter(pk=new_pdf.pk))==0:
                user_profile.modifiedpdfs_translated_arabic.add(new_pdf)
                user_profile.save()

    
    return new_pdf