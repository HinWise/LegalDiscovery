
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db import connection
from django import db

from enersectapp.models import *

from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render, redirect,render_to_response


from PyPDF2 import PdfFileWriter, PdfFileMerger, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import time
import tempfile

from django.db.models import Count

import json 

import time
import gc
from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


import random

def affidavit_create(request):
    
    the_user = request.user
    
    if not request.user.is_authenticated():
        
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
    if len(the_user.groups.filter(name="TeamLeaders")) >0:
    
        user_type = "TeamLeader"
        
    elif the_user.is_superuser == True :
    
        user_type = "superuser"
        
    else:
    
        user_type = "user"

        
    if user_type != "superuser" and user_type != "TeamLeader" and user_type != "Client":
    
        return HttpResponseRedirect(reverse('enersectapp:app_login', args=()))
        
        
    user_profile = UserProfile.objects.get(user = the_user)

    legaldiscovery_templates_names_list = user_profile.created_legaldiscovery_templates.all().values_list('name',flat=True).distinct()

    
    try:
        action_mark = request.POST['action_mark']
    except (KeyError):
        
        action_mark = ""
    
    try:
        selected_template = request.POST['legal_template']
        
    except (KeyError):
        
        selected_template = ""
    
    try:
        stringified_legal_discovery_template = request.POST['final_legal_discovery']
        
    except (KeyError):
        
        stringified_legal_discovery_template = ""
        
        
    final_entries = PdfRecord.objects.filter(audit_mark = "None").distinct()
    
    #Future note: In this implementation, we don't take into account the apparition of new types, which aren't save in the LegalDiscovey_Templates made in the past
    

    document_types_list_dictionaries = []
    
    default_method = True
    
    if len(action_mark) != 0 and len(selected_template) != 0:
    
        default_method = False
        
        
        
        if action_mark == "choose_template":
        
            
        
            template_exists = selected_template in legaldiscovery_templates_names_list
        
            if selected_template == "New Template":
                
                
                
                default_method = True
        
            elif template_exists == False:
            
                
            
                default_method = True
            
            else:
            
                
                
                ###After choosing the EXISTING TEMPLATE, produce data so it can be shown in the app THIS CODE IS ALMOST THE SAME AS AFTER NEW CREATION
                
                new_Legal_Discovery_Template = LegalDiscoveryTemplate.objects.get(name=selected_template,creation_user=the_user)
                
                used_document_types_dictionary_list = final_entries.values('modified_document_type__clean_name').order_by().annotate(count=Count('id')).order_by()
        
                used_document_types_templates_list = new_Legal_Discovery_Template.sourcedoctypes_list.all().order_by('sequential_order')
                    
                for doctype in used_document_types_templates_list:

                        
                    count = used_document_types_dictionary_list.get(modified_document_type__clean_name = doctype.clean_name)["count"]
                        
                    new_element = {}
                    new_element.update({"clean_name":str(doctype.clean_name)})
                    new_element.update({"name":str(doctype.pretty_name)})
                    new_element.update({"count":count})
                    new_element.update({"min_show":doctype.min_show})
                    new_element.update({"max_show":count})
                    new_element.update({"min_selected":doctype.min_selected})
                    new_element.update({"max_selected":doctype.max_selected})
                    new_element.update({"checked":str(doctype.checked)})
                    new_element.update({"sequential_order":str(doctype.sequential_order)})
                    new_element.update({"extraction_fields_sorting":str(doctype.extraction_fields_sorting)})
                         
                    new_element.update({"id":doctype.pk})
                        
                        

                    extraction_fields_list = doctype.extraction_fields.all().order_by('sequential_order').values('sequential_order','real_field_name','pretty_name','field_sorting','checked')
                    clean_extraction_fields_list = []
                                                
                    for field in extraction_fields_list:
                            
                        new_extraction_marker = {}
                        
                        new_extraction_marker.update({"real_field_name":str(field["real_field_name"])})
                        new_extraction_marker.update({"name":str(field["pretty_name"])})
                        new_extraction_marker.update({"checked":str(field["checked"])})
                        new_extraction_marker.update({"field_sorting":str(field["field_sorting"])})
                        new_extraction_marker.update({"sequential_order":str(field["sequential_order"])})
                                                        
                        clean_extraction_fields_list.append(new_extraction_marker)
                        
                    new_element.update({"extraction_fields":clean_extraction_fields_list})
                    new_element.update({"number_extraction_fields":doctype.number_extraction_fields})
                        
                    document_types_list_dictionaries.append(new_element)
                
                
        
        elif (action_mark == "save_template" or action_mark == "export_template") and len(stringified_legal_discovery_template) > 0:
        
            
        
            template_exists = selected_template in legaldiscovery_templates_names_list
            
            converting_json = False
            
            try:
                decoded_json = json.loads(stringified_legal_discovery_template)
                converting_json = True
                
            except:
                decoded_json = []
                print "ERROR TRIED TO SAVE JSON AND IT DIDN'T DECODE CORRECTLY!"
            
            
            clean_names_list = []
            
            for clean_name in decoded_json:
                
                clean_names_list.append(clean_name)
                
            
            '''if template_exists and selected_template != "New Template" and converting_json == True:
            
                print "GOT HERE!--------------------------------------------------------->6 OVERWRITING PREVIOUS TEMPLATE"'''
                
        
            if converting_json ==True:
                
                
                with transaction.commit_on_success():
                
                    
                
                    try:
                        new_Legal_Discovery_Template = LegalDiscoveryTemplate.objects.get(name=selected_template,creation_user=the_user)
                        
                        new_Legal_Discovery_Template.modification_date = datetime.datetime.now().replace(tzinfo=timezone.utc)
                        
                        all_sourcedocs = new_Legal_Discovery_Template.sourcedoctypes_list.all()
                        
                        for sourcedoc in all_sourcedocs:
                        
                            all_extraction = sourcedoc.extraction_fields.all()
                            
                            for extraction in all_extraction:
                                extraction.delete()
                            
                            sourcedoc.delete()
                        
                        
                    except:
                        
                        new_Legal_Discovery_Template = LegalDiscoveryTemplate()
                        new_Legal_Discovery_Template.name = "Saved Template "+str(len(legaldiscovery_templates_names_list)+1)
                        new_Legal_Discovery_Template.creation_user = the_user
                        new_Legal_Discovery_Template.modification_date = datetime.datetime.now().replace(tzinfo=timezone.utc)

                    new_Legal_Discovery_Template.save()
                    
                                        
                    for sourcedoc in clean_names_list:
                        
                        reference_sourcedoc = SourceDocType.objects.get(clean_name=sourcedoc)
                        
                        new_Source_Doc_Template = SourceDocTypeTemplate()
                        
                        new_Source_Doc_Template.name = reference_sourcedoc.name
                        new_Source_Doc_Template.pretty_name = reference_sourcedoc.pretty_name
                        new_Source_Doc_Template.clean_name = reference_sourcedoc.clean_name
                        new_Source_Doc_Template.number_extraction_fields = reference_sourcedoc.number_extraction_fields
                        new_Source_Doc_Template.sequential_order = decoded_json[sourcedoc]["sequential_order"]
                        new_Source_Doc_Template.extraction_fields_sorting = reference_sourcedoc.extraction_fields_sorting
                        
                        
                        new_Source_Doc_Template.min_show = decoded_json[sourcedoc]["min_show"]
                        new_Source_Doc_Template.max_show = decoded_json[sourcedoc]["max_show"]
                        new_Source_Doc_Template.min_selected = decoded_json[sourcedoc]["min_selected"]
                        new_Source_Doc_Template.max_selected = decoded_json[sourcedoc]["max_selected"]
                        new_Source_Doc_Template.checked = decoded_json[sourcedoc]["checked"]
                        new_Source_Doc_Template.creation_user = the_user
                        
                        new_Source_Doc_Template.save()
                        
                        
                        extraction_fields_names_list = []
            
                        for extraction_name in decoded_json[sourcedoc]["extraction_fields"]:
                            
                            extraction_fields_names_list.append(extraction_name)
                        
                        
                        
                        
                        for extraction_field in extraction_fields_names_list:
                        
                            reference_extraction_field = ExtractionField.objects.get(real_field_name=extraction_field)
                            
                            new_Extraction_Field_Template = ExtractionFieldTemplate()
                            
                            
                            new_Extraction_Field_Template.name = reference_extraction_field.name
                            new_Extraction_Field_Template.pretty_name = reference_extraction_field.pretty_name
                            new_Extraction_Field_Template.real_field_name = reference_extraction_field.real_field_name
                            new_Extraction_Field_Template.importance = reference_extraction_field.importance
                            new_Extraction_Field_Template.sequential_order = decoded_json[sourcedoc]["extraction_fields"][extraction_field]["sequential_order"]
                            
                            new_Extraction_Field_Template.checked = decoded_json[sourcedoc]["extraction_fields"][extraction_field]["checked"]
                            new_Extraction_Field_Template.field_sorting = decoded_json[sourcedoc]["extraction_fields"][extraction_field]["field_sorting"]
                            
                            new_Extraction_Field_Template.creation_user = the_user
                            
                            #Saving Extraction Field Template and adding it to the list in SDT Template
                            
                            new_Extraction_Field_Template.save()
                            
                            new_Source_Doc_Template.extraction_fields.add(new_Extraction_Field_Template)
                            
                            
                            
                        
                        
                        #Saving SourceDocType Template and adding it to the list in LD Template
                        
                        new_Source_Doc_Template.save()
                            
                        new_Legal_Discovery_Template.sourcedoctypes_list.add(new_Source_Doc_Template)
                        
                    
                    #Saving Legal Discovery Template and adding it to the list in User Profile
                    
                    new_Legal_Discovery_Template.save()
                            
                    user_profile.created_legaldiscovery_templates.add(new_Legal_Discovery_Template)
                    
                    
                    
                    if action_mark != "export_template":

                    
                        ###After saving the NEW TEMPLATE, produce data so it can be shown in the app
                        
                        
                        used_document_types_dictionary_list = final_entries.values('modified_document_type__clean_name').order_by().annotate(count=Count('id')).order_by()
            
                        used_document_types_templates_list = new_Legal_Discovery_Template.sourcedoctypes_list.all().order_by('sequential_order')
                        
                        for doctype in used_document_types_templates_list:

                            
                            count = used_document_types_dictionary_list.get(modified_document_type__clean_name = doctype.clean_name)["count"]
                            
                            new_element = {}
                            new_element.update({"clean_name":str(doctype.clean_name)})
                            new_element.update({"name":str(doctype.pretty_name)})
                            new_element.update({"count":count})
                            new_element.update({"min_show":doctype.min_show})
                            new_element.update({"max_show":count})
                            new_element.update({"min_selected":doctype.min_selected})
                            new_element.update({"max_selected":doctype.max_selected})
                            new_element.update({"checked":str(doctype.checked)})
                            new_element.update({"sequential_order":str(doctype.sequential_order)})
                            new_element.update({"extraction_fields_sorting":str(doctype.extraction_fields_sorting)})
                             
                            new_element.update({"id":doctype.pk})
                            
                            

                            extraction_fields_list = doctype.extraction_fields.all().order_by('sequential_order').values('sequential_order','real_field_name','pretty_name','field_sorting','checked')
                            clean_extraction_fields_list = []
                                                    
                            for field in extraction_fields_list:
                                
                                new_extraction_marker = {}
                                
                                new_extraction_marker.update({"real_field_name":str(field["real_field_name"])})
                                new_extraction_marker.update({"name":str(field["pretty_name"])})
                                new_extraction_marker.update({"checked":str(field["checked"])})
                                new_extraction_marker.update({"field_sorting":str(field["field_sorting"])})
                                new_extraction_marker.update({"sequential_order":str(field["sequential_order"])})
                                                            
                                clean_extraction_fields_list.append(new_extraction_marker)
                            
                            new_element.update({"extraction_fields":clean_extraction_fields_list})
                            new_element.update({"number_extraction_fields":doctype.number_extraction_fields})
                            
                            document_types_list_dictionaries.append(new_element)
                    
                    
                    
                    #If the action is Export/Producing the Legal Discovery Report, we don't need to return the new table as output for LD Tool
                    
                    else:
 
                        try:
                            override_sorting = request.POST['override_sorting']
                            
                        except:
                            override_sorting = "no_override"
                            
                        #Temporally set to override_by_date for developing purposes    
                        override_sorting = "override_by_date"
                        print "SORTING TIIIME"
                        print override_sorting
                        print "SORTING TIIIME"
                        
                        Legal_Discovery_object = new_Legal_Discovery_Template
                        
                        corpus_pdfs_to_export = final_entries
                        
                        max_limit_to_print_of_each = 2
                        
                        if max_limit_to_print_of_each > 0 and len(corpus_pdfs_to_export) > 0:
        
                            
                            
                            #Initialize the Pdf to be written
                            
                            output = PdfFileMerger()
                            
                            #Creating a list to divide the output in various files before merging them in one, for memory purposes
                            
                            output_temp_documents_created = []
                            

                            title_string = "Legal Discovery Report\n"
                            title_date = str(Legal_Discovery_object.modification_date)
                        
                            response = HttpResponse(mimetype="application/pdf")
                            response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/legal_discovery_report_%s.pdf' %(title_date)
                        
                            
                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                            tmpfile.rollover()
                                    
                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                            string_to_pdf(the_canvas,title_string+title_date)
                                   
                            the_canvas.save()
                                            
                            input1 = PdfFileReader(tmpfile)
                             
                            output.append(input1)
                            #output.append(input1)
                            
                            temp_filename = "legaldiscoverytemp/initial_cover"+str(len(output_temp_documents_created))+".pdf"
                            
                            output.write(temp_filename)
                            
                            output_temp_documents_created.append(temp_filename)
                            
                            output = PdfFileMerger()
                            
                            ###
                            ## If override_sorting is "no_override", it means that there is no global sorting selected, so it follows the normal
                            ## sorting rules, and prints the report based on the order of Document Types.
                            ###
                            
                            if override_sorting == "no_override":
                            
                                #Start looping through the SourceDocTypeTemplates, making the consequent actions:
                                #
                                #-Make a variable for all  the SourceDocTypeTemplates contained in this Template
                                #   -Catch the equivalent SourceDocType
                                #   -Keep the min_selected and max_selected in two variables: start_range and end_range
                                #   -Force the end_range to start_range + max_limit_to_print_of_each
                                #   -Make a variable for all the extraction fields
                            
                                all_sourcedoctypestemplate = Legal_Discovery_object.sourcedoctypes_list.filter(checked = "checked").order_by('sequential_order')
                            
                                
                                exhibit_count = 1
                                pdf_string = ""
                                
                                '''Iteration of all the DocTypes to produce the Index (which gives the values of the OcrEntries in DocType Groups'''
                                
                                with transaction.commit_on_success():
                                    for doctype_template in all_sourcedoctypestemplate:
                                    
                                        equivalent_doctype = SourceDocType.objects.get(clean_name = doctype_template.clean_name)
                                        pretty_name = doctype_template.pretty_name
                                        start_range = doctype_template.min_selected
                                        end_range = doctype_template.max_selected
                                        #Edit, forcing the maximum amount of records per type. Delete to erase
                                        end_range = start_range + max_limit_to_print_of_each
                                        
                                        all_extraction_field_templates = doctype_template.extraction_fields.filter(checked = "checked").values('real_field_name','sequential_order','field_sorting','checked').order_by('sequential_order')
                                        
                                        #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
                                        
                                        corpus_include_fields = []
                                        corpus_sorting_fields = []
                                        
                                        
                                        for field in all_extraction_field_templates:
                                            
                                            corpus_include_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                        
                                            sorting_element = field["field_sorting"]
                                                
                                            if sorting_element == "down":
                                                    
                                                corpus_sorting_fields.append("-ocrrecord_link__"+(field["real_field_name"]))
                                                
                                            elif sorting_element == "up":
                                            
                                                corpus_sorting_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                            
                                            

                                        #Dictionary of Pdf information to Report, with relevant fields, sorted by fields
                                        
                                        corpus_include_fields_additional = corpus_include_fields
                                        
                                        corpus_include_fields_additional.append('sourcedoc_link__filename')
                                        corpus_include_fields_additional.append('sourcedoc_link__job_directory')
                                        
                                        #Takes the ones that fit with the doctype we are searching for
                                        
                                        corpus_base = corpus_pdfs_to_export.filter(modified_document_type = equivalent_doctype)
                                        
                                        #Takes only the values defined in corpus_include_fields
                                        
                                        if len(corpus_include_fields_additional):
                                            corpus_include_fields_base = corpus_base.values(*corpus_include_fields_additional)
                                        else:
                                            corpus_include_fields_base = corpus_base
                                        
                                        #Orders the records by the fields defined in corpus_sorting_fields
                                        
                                        if len(corpus_sorting_fields):
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by(*corpus_sorting_fields)
                                        else:
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by()
                                        

                                        #Making the cut, based on the start_range and end_range
                                        
                                        corpus_final = corpus_ordered_fields_base[start_range:end_range]
                                         
                                        
                                        #Cleaning the access lists to be used later
                                        
                                        access_list_ocr_names = []
                                        
                                        #print access_list_ocr_names
                                        
                                        for name_value in corpus_include_fields:
                                        
                                            if "ocrrecord_link__" in name_value:
                                            
                                                name_value = name_value.replace("ocrrecord_link__","")
                                                
                                                access_list_ocr_names.append(name_value)
                                        
                                        
                                        access_list_sourcepdf_names = ["job_directory","filename"]
                                        
                                        
                                        #Cleaning loop of the corpus_final
                                        
                                        for record in corpus_final:
                                        
                                            for key in record.items():
                                                
                                                if "ocrrecord_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("ocrrecord_link__","")
                                                     
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])
                                            
                                                elif "sourcedoc_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("sourcedoc_link__","")
                                            
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])

                                             
                                        
                                        #Ready to make the writing to the PDF loop
                                        
                                        
                                        
                                        #Index Loop
                                        
                                        
                                        '''Write command to begin outputing to a new page'''
                                        
                                        
                                        
                                        for record in corpus_final:
                                        
                                            pdf_string += "Exhibit "+str(exhibit_count)+": "+str(pretty_name)
                                            
                                            for ocr_name in access_list_ocr_names:
                                                
                                                cute_name = ExtractionField.objects.filter(real_field_name = ocr_name)[0].pretty_name
                                                                                            
                                                try:
                                                    
                                                    try:
                                                        
                                                        if (len(pdf_string.split("\n")[-1]) + len(" "+str(cute_name)+" "+(record[ocr_name]))) > 80:
                                                            test_string = "\n"
                                                            test_string2 = ".              -"
                                                        else:
                                                            test_string = ""
                                                            test_string2 = ""
                                                        
                                                        if record[ocr_name] != "MISSING" and record[ocr_name] != "UNREADABLE" and "Field" not in record[ocr_name] !="" :
                                                            pdf_string += " "+test_string+test_string2+str(cute_name)+" "+(record[ocr_name])
                                                          
                                                    except:
                                                        test_string = ""
                                                    
                                                except:
                                                    pdf_string += " "
                                                    
                                            
                                            '''Write command to output the existing pdf_string variable as a new row, then line break'''
                                            
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
                                                
                                                output.append(input1)
                                                
                                                pdf_string = ""

                                            exhibit_count += 1
                                        
                                        
                                        
                                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                    tmpfile.rollover()
                                    
                                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                                    string_to_pdf(the_canvas,pdf_string)
                                           
                                    the_canvas.save()
                                            
                                    input1 = PdfFileReader(tmpfile)
                                    
                                    output.append(input1)
                                    '''Write command to finish and save new page'''
                            
                            
                                exhibit_count = 1
                            
                                with transaction.commit_on_success():
                                    for doctype_template in all_sourcedoctypestemplate:
                                    
                                        equivalent_doctype = SourceDocType.objects.get(clean_name = doctype_template.clean_name)
                                        pretty_name = doctype_template.pretty_name
                                        start_range = doctype_template.min_selected
                                        end_range = doctype_template.max_selected
                                        #Edit, forcing the maximum amount of records per type. Delete to erase
                                        end_range = start_range + max_limit_to_print_of_each
                                        
                                        all_extraction_field_templates = doctype_template.extraction_fields.filter(checked = "checked").values('real_field_name','sequential_order','field_sorting','checked').order_by('sequential_order')
                                        
                                        #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
                                        
                                        corpus_include_fields = []
                                        corpus_sorting_fields = []
                                        
                                        
                                        for field in all_extraction_field_templates:
                                            
                                            corpus_include_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                        
                                            sorting_element = field["field_sorting"]
                                                
                                            if sorting_element == "down":
                                                    
                                                corpus_sorting_fields.append("-ocrrecord_link__"+(field["real_field_name"]))
                                                
                                            else:
                                            
                                                corpus_sorting_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                            
                                            

                                        #Dictionary of Pdf information to Report, with relevant fields, sorted by fields
                                        
                                        corpus_include_fields_additional = corpus_include_fields
                                        
                                        corpus_include_fields_additional.append('sourcedoc_link__filename')
                                        corpus_include_fields_additional.append('sourcedoc_link__job_directory')
                                        
                                        #Takes the ones that fit with the doctype we are searching for
                                        
                                        corpus_base = corpus_pdfs_to_export.filter(modified_document_type = equivalent_doctype)
                                        
                                        #Takes only the values defined in corpus_include_fields
                                        
                                        if len(corpus_include_fields_additional):
                                            corpus_include_fields_base = corpus_base.values(*corpus_include_fields_additional)
                                        else:
                                            corpus_include_fields_base = corpus_base
                                        
                                        #Orders the records by the fields defined in corpus_sorting_fields
                                        
                                        if len(corpus_sorting_fields):
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by(*corpus_sorting_fields)
                                        else:
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by()
                                        

                                        #Making the cut, based on the start_range and end_range
                                        
                                        corpus_final = corpus_ordered_fields_base[start_range:end_range]
                                         
                                        
                                        #Cleaning the access lists to be used later
                                        
                                        access_list_ocr_names = []
                                        
                                        #print access_list_ocr_names
                                        
                                        for name_value in corpus_include_fields:
                                        
                                            if "ocrrecord_link__" in name_value:
                                            
                                                name_value = name_value.replace("ocrrecord_link__","")
                                                
                                                access_list_ocr_names.append(name_value)
                                        
                                        
                                        access_list_sourcepdf_names = ["job_directory","filename"]
                                        
                                        
                                        #Cleaning loop of the corpus_final
                                        
                                        for record in corpus_final:
                                        
                                            for key in record.items():
                                                
                                                if "ocrrecord_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("ocrrecord_link__","")
                                                     
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])
                                            
                                                elif "sourcedoc_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("sourcedoc_link__","")
                                            
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])

                                             
                                        
                                        #Ready to make the writing to the PDF loop
                                        
                                        
                                        #Exhibit Title Pages + Pdfs Loop
                                        
                                        
                                        for record in corpus_final:
                                        
                                            '''Write command to begin outputing to a new page'''
                                        
                                            pdf_string = "Exhibit "+str(exhibit_count)
                                            
                                            '''Write command to finish and save new page'''
                                            
                                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                            tmpfile.rollover()
                                            
                                            
                                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                                            string_to_pdf(the_canvas,pdf_string)
                                               
                                            the_canvas.save()
                                                
                                            input1 = PdfFileReader(tmpfile)
                                            
                                            output.append(input1)
                                            
                                            
                                            '''Write command to begin outputing to a new page'''
                                            
                                            job_directory = ""
                                            filename = ""
                                            
                                            for sourcedoc_name in access_list_sourcepdf_names:
                                                
                                                if sourcedoc_name == "job_directory":
                                                
                                                    job_directory = record[sourcedoc_name]
                                                
                                                if sourcedoc_name == "filename":
                                                
                                                    filename = record[sourcedoc_name]
                                                
                                                
                                            source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(job_directory, filename)
                                                

                                            remoteFile = urlopen(Request(source_url)).read()
                                            memoryFile = StringIO(remoteFile)
                                            input_pdf = PdfFileReader(memoryFile)
                                            output.addPage(input_pdf.getPage(0))
                                    
                                            '''Write command to finish and save new page'''
                                            exhibit_count += 1

                                    
                                    
                                    outputStream = StringIO()
                                    output.write(outputStream)
                                    
                                    
                                    
                                    response.write(outputStream.getvalue())
                                    return response
                        
                        
                            
                            ###
                            ## If override_sorting is "override_by_date", it means that the global sorting method selected is By Date, which overrides
                            ## the normal, general sorting instructions, and presents the records in the report orderer by date, not taking into account the
                            ## ordering of the document types. It does take into account the amount of each indicated in the document type configurations panels.
                            ###
                            
                            elif override_sorting == "override_by_date":
                            
                                print "SORTING BY DAAATE"
                                #Creates a variable that will join all the selected documents from the different SourceDocTypes selected
                                #
                                #Start looping through the SourceDocTypeTemplates, making the consequent actions:
                                #
                                #   -Make a variable storing the length of the list of the selected documents by that type
                                #   -Add the selected documents in the appropriate number to the common list
                                #
                                #Take the joined list of documents selected and order it by Date
                                #Start looping through the ordered by Date joined list of documents selected, making the consequent actions:
                                #
                                #   -Keep the min_selected and max_selected in two variables: start_range and end_range
                                #   -Force the end_range to start_range + max_limit_to_print_of_each
                                #   -Make a variable for all the extraction fields
                                
                                try:
                                    max_documents = request.POST['max_documents']
                                    
                                except:
                                    max_documents = 10
                                
                                max_documents = 1000
                                
                                try:
                                    report_type = request.POST['report_type']
                                    
                                except:
                                    report_type = ""
                                
                                corpus_common_final = PdfRecord.objects.none()
                                
                                exhibit_count = 1
                                pdf_string = ""
                                
                                all_sourcedoctypestemplate = Legal_Discovery_object.sourcedoctypes_list.filter(checked = "checked")
                                                            
                                '''Iteration of all the DocTypes to select the appropriate documents (OcrEntries)'''
                                
                                with transaction.commit_on_success():
                                    for doctype_template in all_sourcedoctypestemplate:
                                    
                                        equivalent_doctype = SourceDocType.objects.get(clean_name = doctype_template.clean_name)

                                        start_range = doctype_template.min_selected
                                        end_range = doctype_template.max_selected
                                        #Edit, forcing the maximum amount of records per type. Delete to erase
                                        end_range = start_range + max_limit_to_print_of_each
                                        

                                        #Takes the ones that fit with the doctype we are searching for
                                        
                                        corpus_base = corpus_pdfs_to_export.filter(modified_document_type = equivalent_doctype)
                                        
                                        corpus_include_fields_base = corpus_base
                                        
                                        corpus_ordered_fields_base = corpus_include_fields_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')
                                        
                                        corpus_final = corpus_ordered_fields_base
                                        
                                        corpus_common_final = corpus_common_final | corpus_final
                                
                                
                                corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')
                                #corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Notes')
                                corpus_common_final = corpus_common_final[:max_documents]   
                                print "----z  "+str(len(corpus_common_final))
                                
                                with transaction.commit_on_success():
                                    for selected_entry_item in corpus_common_final:
                                    
                                        if exhibit_count % 5000 == 0:
                                            
                                           
                                            print "<-------------------------- ---------------------->"
                                            
                                            temp_filename = "legaldiscoverytemp/legaltempdocument"+str(len(output_temp_documents_created))+".pdf"
                                            output.write(temp_filename)
                                            output_temp_documents_created.append(temp_filename)
                                            
                                            output = PdfFileMerger()
                                            
                                            db.reset_queries()

                                        
                                        print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
                                    
                                        equivalent_doctype_template = Legal_Discovery_object.sourcedoctypes_list.get(clean_name = selected_entry_item.modified_document_type.clean_name)

                                        pretty_name = equivalent_doctype_template.pretty_name
                                        
                                        all_extraction_field_templates = equivalent_doctype_template.extraction_fields.filter(checked = "checked").values('real_field_name','sequential_order','field_sorting','checked').order_by('sequential_order')
                                        
                                        #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
                                        
                                        corpus_include_fields = []
                                        corpus_sorting_fields = []
                                        
                                        
                                        for field in all_extraction_field_templates:
                                            
                                            corpus_include_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                        
                                            sorting_element = field["field_sorting"]
                                                
                                            if sorting_element == "down":
                                                    
                                                corpus_sorting_fields.append("-ocrrecord_link__"+(field["real_field_name"]))
                                                
                                            elif sorting_element == "up":
                                            
                                                corpus_sorting_fields.append("ocrrecord_link__"+(field["real_field_name"]))
                                            
                                            

                                        #Dictionary of Pdf information to Report, with relevant fields, sorted by fields
                                        
                                        corpus_include_fields_additional = corpus_include_fields
                                        
                                        corpus_include_fields_additional.append('sourcedoc_link__filename')
                                        corpus_include_fields_additional.append('sourcedoc_link__job_directory')
                                        
                                        #Takes the ones that fit with the doctype we are searching for
                                        
                                        selected_with_values = PdfRecord.objects.filter(pk = selected_entry_item.pk)
                                        
                                        corpus_base = selected_with_values
                                        
                                        #Takes only the values defined in corpus_include_fields
                                        
                                        if len(corpus_include_fields_additional):
                                            corpus_include_fields_base = corpus_base.values(*corpus_include_fields_additional)
                                        else:
                                            corpus_include_fields_base = corpus_base
                                        
                                        #Orders the records by the fields defined in corpus_sorting_fields
                                        
                                        if len(corpus_sorting_fields):
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by(*corpus_sorting_fields)
                                        else:
                                            corpus_ordered_fields_base = corpus_include_fields_base.order_by()
                                        

                                        #Not making cut, because the entry is already decided upon
                                        
                                        corpus_final = corpus_ordered_fields_base
                                         
                                        
                                        #Cleaning the access lists to be used later
                                        
                                        access_list_ocr_names = []
                                        
                                        #print access_list_ocr_names
                                        
                                        for name_value in corpus_include_fields:
                                        
                                            if "ocrrecord_link__" in name_value:
                                            
                                                name_value = name_value.replace("ocrrecord_link__","")
                                                
                                                access_list_ocr_names.append(name_value)
                                        
                                        
                                        access_list_sourcepdf_names = ["job_directory","filename"]
                                        
                                        
                                        #Cleaning loop of the corpus_final
                                        
                                        for record in corpus_final:
                                        
                                            for key in record.items():
                                                
                                                if "ocrrecord_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("ocrrecord_link__","")
                                                     
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])
                                            
                                                elif "sourcedoc_link__" in key[0]:
                                                    
                                                    new_key = key[0].replace("sourcedoc_link__","")
                                            
                                                    record[new_key] = key[1]
                                                    
                                                    record.pop(key[0])

                                             
                                        
                                        #Ready to make the writing to the PDF loop
                                        
                                        
                                        #Index Loop
                                        
                                        
                                        '''Write command to begin outputing to a new page'''
                                        
                                        
                                        
                                        for record in corpus_final:
                                            

                                            pdf_string += "Exhibit "+str(exhibit_count)+": "+str(pretty_name)
                                            
                                            for ocr_name in access_list_ocr_names:
                                                
                                                cute_name = ExtractionField.objects.filter(real_field_name = ocr_name)[0].pretty_name
                                                                                            
                                                try:
                                                    
                                                    try:
                                                        
                                                        if (len(pdf_string.split("\n")[-1]) + len(" "+str(cute_name)+" "+(record[ocr_name]))) > 104:
                                                            test_string = "\n"
                                                            test_string2 = ".              -"
                                                        else:
                                                            test_string = ""
                                                            test_string2 = ""
                                                        
                                                        if record[ocr_name] != "MISSING" and record[ocr_name] != "UNREADABLE" and "Field" not in record[ocr_name] !="" :
                                                            pdf_string += " "+test_string+test_string2+str(cute_name)+" "+(record[ocr_name])
                                                          
                                                    except:
                                                        test_string = ""
                                                    
                                                except:
                                                    pdf_string += " "
                                                    
                                            
                                            '''Write command to output the existing pdf_string variable as a new row, then line break'''
                                            
                                            pdf_string += '\n'
                                            pdf_string += '\n'
                                            
                                            if pdf_string.count('\n') > 53:
                                            
                                                tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                    
                                                # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                                tmpfile.rollover()
                                              
                                                the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                                                string_to_pdf(the_canvas,pdf_string)
                                                       
                                                the_canvas.save()
                                                
                                                input1 = PdfFileReader(tmpfile)
                                                
                                                output.append(input1)
                                                
                                                pdf_string = ""

                                            exhibit_count += 1
                                        
                                  
                                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                    
                                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                    tmpfile.rollover()
                                  
                                    
                                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                                    string_to_pdf(the_canvas,pdf_string)
                                           
                                    the_canvas.save()
                                    
                                    input1 = PdfFileReader(tmpfile)
                                    
                                    output.append(input1)
                                   
                                    
                                    '''Write command to finish and save new page'''
                                
                                try:
                                
                                    temp_filename = "legaldiscoverytemp/legaltempdocument"+str(len(output_temp_documents_created))+".pdf"
                                    output.write(temp_filename)
                                    output_temp_documents_created.append(temp_filename)
                                    
                                    output = PdfFileMerger()
                                    
                                    db.reset_queries()
                                    
                                except:
                                
                                    print "empty"
                                
                            
                                exhibit_count = 1
                                
                                documents_to_include_in_output = ["icr","sourcedoc_pdfs"]
                                
                                if "sourcedoc_pdfs" in documents_to_include_in_output:
                                    print "fgrgergergggggggggggggggggggggggg----------------"
                                    with transaction.commit_on_success():
                                        for selected_entry_item in corpus_common_final:
                                        
                                            if exhibit_count % 50 == 0 or exhibit_count == 1:
                                            
                                                
                                                print "<-------------------------- ---------------------->"
                                                
                                                temp_filename = "legaldiscoverytemp/legaltempdocumentsourcedoc"+str(len(output_temp_documents_created))+".pdf"
                                                output.write(temp_filename)
                                                output_temp_documents_created.append(temp_filename)
                                                
                                                output = PdfFileMerger()
                                                
                                                db.reset_queries()

                                            
                                            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
                                        
                                        
                                            #Exhibit Title Pages + Pdfs Loop
                                            
                                            '''Write command to begin outputing to a new page'''
                                        
                                            pdf_string = "Exhibit "+str(exhibit_count)
                                            
                                            '''Write command to finish and save new page'''
                                            

                                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                            tmpfile.rollover()
                                            
                                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                                            string_to_pdf(the_canvas,pdf_string)
                                               
                                            the_canvas.save()
                                                
                                            input1 = PdfFileReader(tmpfile)
                                        
                                            output.append(input1)
                                            
                                            '''Write command to begin outputing to a new page'''
                                            
                                            job_directory = selected_entry_item.sourcedoc_link.job_directory
                                            filename = selected_entry_item.sourcedoc_link.filename
                                            
                                            source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(job_directory, filename)
                                                

                                            remoteFile = urlopen(Request(source_url)).read()
                                            memoryFile = StringIO(remoteFile)
                                            input_pdf = PdfFileReader(memoryFile)
                                            output.append(input_pdf)
                                            #output.addPage(input_pdf.getPage(0))
                                    
                                            '''Write command to finish and save new page'''
                                            exhibit_count += 1

                                
                                
                                    try:
                                    
                                        temp_filename = "legaldiscoverytemp/legaltempdocument"+str(len(output_temp_documents_created))+".pdf"
                                        output.write(temp_filename)
                                        output_temp_documents_created.append(temp_filename)
                                        
                                        output = PdfFileMerger()
                                        
                                        db.reset_queries()
                                        
                                    except:
                                    
                                        print "empty"
                                
                                
                                '''try:
                                    temp_output.write(temp_outputStream)
                                    output_streams_files_list.append(temp_outputStream)
                                    
                                    temp_outputStream = StringIO()
                                    temp_output = PdfFileMerger()
                                except:
                                    tried = ""'''
                                
                                final_output = PdfFileMerger()
                                
                                partial_output = PdfFileMerger()
                                
                                outputStream = StringIO()

                                print "-SHOULD HAPPEN JUST ONCE" 
                                #final_output.append(PdfFileReader(temp_outputStream))
                                
                                for filename in output_temp_documents_created:
                                    print "---->"+str(filename)   
                                    #final_output.append(PdfFileReader(temp_output_item))
                                    partial_output.append(PdfFileReader(file(filename, 'rb')))
                               
                                #To isolate the generated report for the ICR corpus
                               
                                partial_filename = "legaldiscoverytemp/icr-affidavitofrecords-final.pdf"
                                
                                partial_output.write(partial_filename)
                                
                                ##
                                
                                final_output.append(PdfFileReader(file(partial_filename, 'rb')))
                                
                                final_output.write(outputStream)
                                
                                response.write(outputStream.getvalue())
                                response.write(final_output)
                                return response
                                
                    
        else:

            default_method = True
            
        
    #When the Page refreshes, or the clicking decissions don't make sense, it falls back to the default configuration
    
    if default_method == True:
    
        used_document_types_dictionary_list = final_entries.values('modified_document_type__clean_name','modified_document_type__name','modified_document_type__number_extraction_fields').order_by().annotate(count=Count('id')).order_by('-modified_document_type__number_extraction_fields','-count')
    
        with transaction.commit_on_success():
        
            sequential_order = 0
        
            for item in used_document_types_dictionary_list:

                doctype = SourceDocType.objects.get(clean_name = item['modified_document_type__clean_name'] )

                new_element = {}
                new_element.update({"clean_name":str(doctype.clean_name)})
                new_element.update({"name":str(doctype.pretty_name)})
                new_element.update({"count":item['count']})
                new_element.update({"min_show":1})
                new_element.update({"max_show":item['count']})
                new_element.update({"min_selected":1})
                new_element.update({"max_selected":item['count']})
                new_element.update({"checked":"checked"})
                new_element.update({"sequential_order":sequential_order})
                new_element.update({"extraction_fields_sorting":str(doctype.extraction_fields_sorting)})
                 
                new_element.update({"id":doctype.pk})
                
                

                extraction_fields_list = doctype.extraction_fields.all().order_by('-importance').values('real_field_name','pretty_name','field_sorting')
                clean_extraction_fields_list = []
                
                sequential_order += 1
                
                sequential_order2 = 0
                
                for field in extraction_fields_list:
                    
                    new_extraction_marker = {}
                    
                    new_extraction_marker.update({"real_field_name":str(field["real_field_name"])})
                    new_extraction_marker.update({"name":str(field["pretty_name"])})
                    new_extraction_marker.update({"checked":"checked"})
                    new_extraction_marker.update({"field_sorting":str(field["field_sorting"])})
                    new_extraction_marker.update({"sequential_order":sequential_order2})
                    
                    sequential_order2 += 1
                    
                    clean_extraction_fields_list.append(new_extraction_marker)
                
                new_element.update({"extraction_fields":clean_extraction_fields_list})
                new_element.update({"number_extraction_fields":doctype.number_extraction_fields})
                
                document_types_list_dictionaries.append(new_element)
            

    
    legaldiscovery_templates_names_list = user_profile.created_legaldiscovery_templates.all().values_list('name',flat="True").distinct()
    
    
    context = {'user_type':user_type,'the_user':the_user,'document_types_list_dictionaries':document_types_list_dictionaries,
                'legaldiscovery_templates_names_list':legaldiscovery_templates_names_list}
    
    return render(request,'enersectapp/legal_discovery.html',context)
    
def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.setFont("Helvetica", 11)
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
    