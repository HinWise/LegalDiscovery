
import enersectapp

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

import os
import shutil

import string
import random

def legal_discovery(request):
    
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
        
            new_created_template = False
        
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
                        
                        if action_mark == "export_template":
                        
                            new_created_template = True

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
        
        
                            ## Loop to have a list of all files in the folder, and delete all the .pdfs
                            
                            
                            
                            file_list = os.listdir('legaldiscoverytemp/output_files/')#os.chdir('legaldiscoverytemp/output_files')
                            
                            for item in file_list:
                            
                                if ".pdf" in str(item):
                                    os.remove('legaldiscoverytemp/output_files/'+str(item))
        
                            
                            
                            #Initialize the Pdf to be written
                            
                            output = PdfFileMerger()
                            
                            #Creating a list to divide the output in various files before merging them in one, for memory purposes
                            
                            output_temp_documents_created = []
                            

                            title_string = "Legal Discovery Report\n"
                            title_date = str(Legal_Discovery_object.modification_date)
                        
                            
                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                            tmpfile.rollover()
                                    
                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
                            string_to_pdf(the_canvas,title_string+title_date)
                                   
                            the_canvas.save()
                                            
                            input1 = PdfFileReader(tmpfile)
                             
                            output.append(input1)
                            #output.append(input1)
                            
                            
                            
                            
                            exhibit_count = 1
                            corpus_doccount = 1
                            
                            
                            
                            temp_filename = "legaldiscoverytemp/output_files/initial_cover__"+str(corpus_doccount).zfill(7)+".pdf"
                            
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
                                
                                '''response =  affidavit_mode(request)
                                
                                report_type = "affidavit"

                                if report_type == "affidavit" and new_created_template == True:

                                    remove_template(new_Legal_Discovery_Template)
                                
                                return response'''
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
    
    try:
        report_type = request.POST['report_type']
        
    except:
        report_type = "legal_discovery"
    
    
    document_corpus_list = []
    
    watermark_name = ""
    
    if report_type == "affidavit":
    
        try:
            affidavit_result = affidavit_mode(request)
            watermark_name = affidavit_result['watermark_name']
            
            if affidavit_result['response']:
            
                return affidavit_result['response']
            
            
        except:
        
            watermark_name = ""
            print "Failed to enter affidavit_mode"
          
        try:

            document_corpus_list = document_corpus_maker()
         
        except:
        
            document_corpus_list = []
        
        
            
    context = {'user_type':user_type,'the_user':the_user,'document_types_list_dictionaries':document_types_list_dictionaries,
                'legaldiscovery_templates_names_list':legaldiscovery_templates_names_list,'report_type':report_type,
                'document_corpus_list':document_corpus_list,'watermark_name':watermark_name}
    
    return render(request,'enersectapp/legal_discovery.html',context)


def document_corpus_maker():
    
    corpus_list = ["icr","sourcepdfs","grandelivre","albaraka","transactions"]
    
    all_documents = []
    
    for corpus_type in corpus_list:
    
        temp_documents = os.listdir('legaldiscoverytemp/output_files/'+corpus_type+"/")
        all_documents.extend(temp_documents)
    
    all_documents = sorted(all_documents)
    
    print all_documents
    
    document_corpus_list = []
    
    icr_corpus_dict = {}
    icr_corpus_contents_list = []
    sourcepdfs_corpus_dict = {}
    sourcepdfs_corpus_contents_list = []
    grandelivre_corpus_dict = {}
    grandelivre_corpus_contents_list = []
    albaraka_corpus_dict = {}
    albaraka_corpus_contents_list = []
    transactions_corpus_dict = {}
    transactions_corpus_contents_list = []
    
    for file in all_documents:
        
        file_dict = {}
        
        if "icr" in file:
            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            icr_corpus_contents_list.append(file_dict)
            
        if "sourcepdfs" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            sourcepdfs_corpus_contents_list.append(file_dict)
            
        if "grandelivre" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            grandelivre_corpus_contents_list.append(file_dict)
            
        if "albaraka" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            albaraka_corpus_contents_list.append(file_dict)
            
        if "transactions" in file:

            file_dict["file_name"] = file
            file_dict["downloaded"] = "Not Downloaded"
            
            transactions_corpus_contents_list.append(file_dict)
            
            
            
    icr_corpus_dict["corpus_name"] = "icr"
    icr_corpus_dict["corpus_contents"] = icr_corpus_contents_list
    
    sourcepdfs_corpus_dict["corpus_name"] = "sourcepdfs"
    sourcepdfs_corpus_dict["corpus_contents"] = sourcepdfs_corpus_contents_list
    
    grandelivre_corpus_dict["corpus_name"] = "grandelivre"
    grandelivre_corpus_dict["corpus_contents"] = grandelivre_corpus_contents_list
    
    albaraka_corpus_dict["corpus_name"] = "albaraka"
    albaraka_corpus_dict["corpus_contents"] = albaraka_corpus_contents_list
    
    transactions_corpus_dict["corpus_name"] = "transactions"
    transactions_corpus_dict["corpus_contents"] = transactions_corpus_contents_list
    
    document_corpus_list.append(icr_corpus_dict)
    document_corpus_list.append(sourcepdfs_corpus_dict)
    document_corpus_list.append(grandelivre_corpus_dict)
    document_corpus_list.append(albaraka_corpus_dict)
    document_corpus_list.append(transactions_corpus_dict)
    
    
    return document_corpus_list 
    
def string_to_pdf(canvas,string):

    splited_string = string.split("\n")
                            
    times = 0
    
    for item in splited_string:
        
        canvas.setFont("Helvetica", 11)
        canvas.drawString(2,800-(14*times),item)
        
        times +=1
                            
def remove_template(template_object):

    print template_object
    
    try:
    
        with transaction.commit_on_success():
            for sourcedoc_template in template_object.sourcedoctypes_list.all():

                for extractionfield_template in sourcedoc_template.extraction_fields.all():
         
                    extractionfield_template.delete()
            
                sourcedoc_template.delete()

        template_object.delete()
        
        return True
        
    except:
    
        return False
        
   


def affidavit_mode(request):

    
    #If an AffidavitInstance already exists, take its' watermark_name,
    #if not, create an AffidavitInstance, which will have the default name "00000000"

    response = ""
    
    try:
    
        watermark_name = AffidavitInstance.objects.all()[0].watermark_name
        
    except:

        new_AffidavitInstance = AffidavitInstance()
        new_AffidavitInstance.save()
        
        watermark_name = ""
    
    
    try:
        
        affidavit_mode_action = request.POST["affidavit_action_mark"]


    except:

        affidavit_mode_action = ""

    
    print affidavit_mode_action
    
    if affidavit_mode_action == "create_instance_watermark":
        
            watermark_name = create_instance_watermark(request,watermark_name)
            print watermark_name
    
    if watermark_name != "":
    
        print "Watermark Generated, Instance Available"

        if affidavit_mode_action == "generate_corpus_files_action":
            
            generate_corpus_output(request,watermark_name)
    
        if affidavit_mode_action == "merge_corpus_files_action":
            
            response = merge_corpus_output(request,watermark_name)
    
        if affidavit_mode_action == "download_file_action":
            
            response = download_file_output(request,watermark_name)
    

    else:
    
        #The user hasn't generated a watermarked instance yet, so there is no possibility of creating any files
        #Return no values
    
        print "Default Affidavit Instance, no watermark generated"
    
    print "THIS IS WATERMARK --->" + watermark_name
    
    return {"watermark_name":watermark_name,"response":response}
    
    ## Loop to have a list of all files in the folder, and delete all the .pdfs
    
    ##~~~~delete_temp_affidavit_files()
    
    
    
    ##This block is functional, and merging all the things into one .PDF to be exported in the response
    #Changed to a .zip
    
    '''final_output = PdfFileMerger()
    
    partial_output = PdfFileMerger()
    
    outputStream = StringIO()

    print "-SHOULD HAPPEN JUST ONCE" 
    #final_output.append(PdfFileReader(temp_outputStream))
    
    for filename in output_temp_documents_created:
        print "---->"+str(filename)   
        #final_output.append(PdfFileReader(temp_output_item))
        partial_output.append(PdfFileReader(file(filename, 'rb')))
   
    #To isolate the generated report for the ICR corpus
   
    partial_filename = "legaldiscoverytemp/output_files/icr-affidavitofrecords-final.pdf"
    
    partial_output.write(partial_filename)
    
    ##
    
    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    
    final_output.write(outputStream)'''
    

    ## Loop to have a list of all files in the folder, '''and delete all the .pdfs'''
    
    '''file_list = os.listdir('legaldiscoverytemp/output_files/')'''#os.chdir('legaldiscoverytemp/output_files')
    
    '''for item in file_list:
    
        if ".pdf" in str(item):
            os.remove('legaldiscoverytemp/output_files/'+str(item))'''


def generate_corpus_output(request,watermark_name):
    
    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""
    
    documents_corpus_to_include_in_output = []
    documents_corpus_to_include_in_output.append(corpus_to_include)
    
    print corpus_to_include
    print documents_corpus_to_include_in_output
    
    if "icr" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("icr","cover")
        delete_temp_affidavit_files("icr","partial")
        delete_temp_affidavit_files("icr","merge")
        
        generate_icr_output(request,watermark_name)
        
    
    if "sourcepdfs" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("sourcepdfs","cover")
        delete_temp_affidavit_files("sourcepdfs","partial")
        delete_temp_affidavit_files("sourcepdfs","merge")
        
        generate_sourcepdfs_output(request,watermark_name)
        
    if "grandelivre" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("grandelivre","cover")
        delete_temp_affidavit_files("grandelivre","partial")
        delete_temp_affidavit_files("grandelivre","merge")
        
        generate_grandelivre_output(request,watermark_name)
        
    if "albaraka" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("albaraka","cover")
        delete_temp_affidavit_files("albaraka","partial")
        delete_temp_affidavit_files("albaraka","merge")
        
        generate_albaraka_output(request,watermark_name)
        
    if "transactions" in documents_corpus_to_include_in_output:
        
        delete_temp_affidavit_files("transactions","cover")
        delete_temp_affidavit_files("transactions","partial")
        delete_temp_affidavit_files("transactions","merge")
        
        generate_transactions_output(request,watermark_name)


def generate_icr_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['max_documents']
        
    except:
        max_documents = 10

    max_documents = 2500

    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "Icr Corpus Report\n"

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))

    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,title_string+title_date)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = PdfRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    pdf_string = ""

    all_sourcedoctypes = SourceDocType.objects.filter(extraction_fields__isnull = False).distinct()

                                
    '''Iteration of all the DocTypes to select the appropriate documents (OcrEntries)'''

    with transaction.commit_on_success():
        for doctype in all_sourcedoctypes:
       
            #Takes the ones that fit with the doctype we are searching for

            corpus_pdfs_to_export = PdfRecord.objects.filter(audit_mark = "None").distinct()

            corpus_base = corpus_pdfs_to_export.filter(modified_document_type = doctype)

            corpus_final = corpus_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

            corpus_common_final = corpus_common_final | corpus_final
            

    corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

    corpus_common_final = corpus_common_final[:max_documents]

    
    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % 1000 == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["Amount","Currency","IssueDate","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]
            corpus_sorting_fields = ["Amount","Currency","IssueDate","Company","Piece_Number","Document_Number","Source_Bank_Account","PurchaseOrder_Number","Cheque_Number","Address","City","Country","Telephone","Page_Number","Notes","Translation_Notes"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = PdfRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                pretty_name = record.modified_document_type.pretty_name
                
                ocr_record_final = record.ocrrecord_link
                
                pdf_string += "Exhibit "+str(exhibit_count)+": "+str(pretty_name)
                
                for field_name in corpus_include_fields:
                    
                    try:
                        field_content = str(getattr(ocr_record_final, field_name))
                    except:
                        field_content = ""
                    
                    cute_name = str(ExtractionField.objects.filter(real_field_name = field_name)[0].pretty_name)
                    
                    try:
                        
                        try:
                            
                            if (len(pdf_string.split("\n")[-1]) + len(" "+cute_name+" "+field_content)) > 104:
                                test_string = "\n"
                                test_string2 = ".              -"
                            else:
                                test_string = ""
                                test_string2 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and "arabic translation" not in field_content and field_content != "no":
                                pdf_string += " "+test_string+test_string2+cute_name+" "+field_content
                              
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

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
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

        temp_filename = "legaldiscoverytemp/output_files/"+"icr"+"/"+"icr__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"
            
            

def generate_sourcepdfs_output(request,watermark_name):

    try:
        max_documents = request.POST['max_documents']
        
    except:
        max_documents = 10
    
    max_documents = 200
    
    #Initialize the Pdf to be written
    
    output = PdfFileMerger()
    
    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []
    

    title_string = "Source Pdfs Corpus Report\n"
    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))
    
    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)
    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()
            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )
    string_to_pdf(the_canvas,title_string+title_date)
           
    the_canvas.save()
                    
    input1 = PdfFileReader(tmpfile)
     
    output.append(input1)
    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"
    
    output.write(temp_filename)
    
    output_temp_documents_created.append(temp_filename)
    
    output = PdfFileMerger()
    
    
    corpus_common_final = PdfRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    pdf_string = ""
    
    all_sourcedoctypes = SourceDocType.objects.filter(extraction_fields__isnull = False).distinct()
    
                                
    '''Iteration of all the DocTypes to select the appropriate documents (OcrEntries)'''
    
    with transaction.commit_on_success():
        for doctype in all_sourcedoctypes:
       
            #Takes the ones that fit with the doctype we are searching for
            
            corpus_pdfs_to_export = PdfRecord.objects.filter(audit_mark = "None").distinct()
            
            corpus_base = corpus_pdfs_to_export.filter(modified_document_type = doctype)

            corpus_final = corpus_base.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')

            corpus_common_final = corpus_common_final | corpus_final
            

    corpus_common_final = corpus_common_final.order_by('ocrrecord_link__Year','ocrrecord_link__Month','ocrrecord_link__Day')
    
    corpus_common_final = corpus_common_final[:max_documents]
    
    did_page_jump = False  


    print "------------- STARTING SOURCE PDFS ----------------"
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
        
            created_page = False
        
            if doc_iterator % 100 == 0 and doc_iterator != 0:
            
                
                print "<-------------------------- "+str(doc_iterator)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page == True
                
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
            
            #source_url = "http://54.200.180.182/sourcepdfs/%s/%s" %(job_directory, filename)
                

            '''remoteFile = urlopen(Request(source_url)).read()
            memoryFile = StringIO(remoteFile)
            input_pdf = PdfFileReader(memoryFile)
            output.append(input_pdf)
            '''
            
            if "/srv/" in os.path.dirname(__file__):
                
                file_url = "%s/%s" %(job_directory, filename)
                
                source_url = os.path.join(os.path.abspath(enersectapp.__path__[0]),os.pardir,os.pardir,"/var/www/evs",file_url)
                
            else :
                #print str(os.path.abspath(enersectapp.__path__[0]))
                file_url = "%s/%s" %(job_directory, filename)
                
                source_url = os.path.join(os.path.abspath(enersectapp.__path__[0]), os.pardir ,"legaldiscoverytemp/source_pdfs",file_url)
                
            
            output.append(PdfFileReader(file(source_url, 'rb')))
            

            '''Write command to finish and save new page'''
            
            db.reset_queries()
            
            exhibit_count += 1
            doc_iterator = exhibit_count - 1


   
    try:
    
        temp_filename = "legaldiscoverytemp/output_files/"+"sourcepdfs"+"/"+"sourcepdfs__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"
    

def generate_grandelivre_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['max_documents']
        
    except:
        max_documents = 10

    max_documents = 2500

    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "GrandeLivre Corpus Report\n"

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))

    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,title_string+title_date)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = PdfRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    pdf_string = ""

               

    corpus_common_final = InternalRecord.objects.all().order_by('Year','Month','Day')

    corpus_common_final = corpus_common_final[:max_documents]

    
    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % 500 == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["InternalRecordIndex","BestTransactionMatch","IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["InternalRecordIndex","BestTransactionMatch","IssueDate","Credit","Piece_Number","Day","Month","Year","NoPiece","ExchangeRate","Company","AccountNum","NoMvt","Memo","Lett","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = InternalRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                 
                
                pdf_string += "Exhibit "+str(exhibit_count)+": "
                
                for field_name in corpus_include_fields:
                    
                    try:
                        field_content = str(getattr(record, field_name))
                    except:
                        field_content = ""
                    
                    
                    try:
                        
                        try:
                            
                            if (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > 104:
                                test_string = "\n"
                                test_string2 = ".              -"
                            else:
                                test_string = ""
                                test_string2 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None":
                                pdf_string += " "+test_string+test_string2+field_name+" "+field_content
                              
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

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
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

        temp_filename = "legaldiscoverytemp/output_files/"+"grandelivre"+"/"+"grandelivre__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"


def generate_albaraka_output(request,watermark_name):
    
    
    try:
        max_documents = request.POST['max_documents']
        
    except:
        max_documents = 10

    max_documents = 200

    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "AlBaraka Corpus Report\n"

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))

    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,title_string+title_date)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = BankRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    pdf_string = ""

               

    corpus_common_final = BankRecord.objects.all().order_by('ValueYear','ValueMonth','ValueDay')

    corpus_common_final = corpus_common_final[:max_documents]

    
    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % 50 == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                print "---------"+str("albaraka")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["BankRecordIndex","TransactionIndex","Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["BankRecordIndex","TransactionIndex","Amount","PostDay","PostMonth","PostYear","ValueDay","ValueMonth","ValueYear","Libelle","Reference","Description","TransactionId","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = BankRecord.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                 
                
                pdf_string += "Exhibit "+str(exhibit_count)+": "
                
                for field_name in corpus_include_fields:
                    
                    try:
                        field_content = str(getattr(record, field_name))
                    except:
                        field_content = ""
                    
                    
                    try:
                        
                        try:
                            
                            if (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > 104:
                                test_string = "\n"
                                test_string2 = ".              -"
                            else:
                                test_string = ""
                                test_string2 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None":
                                pdf_string += " "+test_string+test_string2+field_name+" "+field_content
                              
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

                    did_page_jump = True
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
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

        temp_filename = "legaldiscoverytemp/output_files/"+"albaraka"+"/"+"albaraka__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"


def generate_transactions_output(request,watermark_name):
    
    
    print "Arrived Transactions Corpus"
    
    try:
        max_documents = request.POST['max_documents']
        
    except:
        max_documents = 10

    max_documents = 200

    #Initialize the Pdf to be written
    
    output = PdfFileMerger()

    #Creating a list to divide the output in various files before merging them in one, for memory purposes
    
    output_temp_documents_created = []


    title_string = "Transactions Corpus Report\n"

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))

    
    tmpfile = tempfile.SpooledTemporaryFile(1048576)

    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
    tmpfile.rollover()

            
    the_canvas = canvas.Canvas(tmpfile,pagesize=A4 )

    string_to_pdf(the_canvas,title_string+title_date)

           
    the_canvas.save()
    input1 = PdfFileReader(tmpfile)

     
    output.append(input1)

    #output.append(input1)
    
    
    exhibit_count = 1
    corpus_doccount = 1
    

    temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__cover__"+str(corpus_doccount).zfill(7)+".pdf"

    output.write(temp_filename)

    output_temp_documents_created.append(temp_filename)

    output = PdfFileMerger()

    
    corpus_common_final = BankRecord.objects.none()
    
    exhibit_count = 1
    corpus_doccount = 1
    doc_iterator = exhibit_count - 1
    pdf_string = ""

               

    corpus_common_final = TransactionTable.objects.all().order_by('CompleteValueDate','CompletePostDate','ValueYear')

    corpus_common_final = corpus_common_final[:max_documents]

    
    
    did_page_jump = False
    
    with transaction.commit_on_success():
        for selected_entry_item in corpus_common_final:
    
            created_page = False
        
            if doc_iterator % 50 == 0 and doc_iterator != 0:
                
                if did_page_jump == False:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""
                
                

                print "<--------------------------"+ str(exhibit_count)+" ---------------------->"
                print "---------"+str("transactions")+"--------"
                
                temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
                corpus_doccount += 1
                output.write(temp_filename)
                output_temp_documents_created.append(temp_filename)
                
                output = PdfFileMerger()
                
                created_page = True
                
                db.reset_queries()
                

            print "----- " +str(selected_entry_item.pk)+ " ---- " + str(exhibit_count)
        

            #For each of the checked extract_fields in this doctype, correct the sorting, to be used in the order of the pdfs to export
            
            corpus_include_fields = ["TransactionIndex","NumberBankRecordIndexes","BankRecordsListOriginalArray","NumberInternalRecordIndexes","InternalRecordListOriginalArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]
            corpus_sorting_fields = ["TransactionIndex","NumberBankRecordIndexes","BankRecordsListOriginalArray","NumberInternalRecordIndexes","InternalRecordListOriginalArray","CompletePostDate","CompleteValueDate","DateDiscrepancy","Amount","AmountDiscrepancy","ValueYear","Libdesc","Reftran","Provenance","BankAccount","BankName","BankCurrency"]


            #Not making cut, because the entry is already decided upon
            
            corpus_final = TransactionTable.objects.filter(pk = selected_entry_item.pk)
            

            for record in corpus_final:
                
                 
                
                pdf_string += "Exhibit "+str(exhibit_count)+": "
                
                for field_name in corpus_include_fields:
                    
                    try:
                        field_content = str(getattr(record, field_name))
                    except:
                        field_content = ""
                    
                    
                    try:
                        
                        try:
                            
                            if field_name == "BankRecordsListOriginalArray" or field_name == "InternalRecordListOriginalArray":
                            
                                test_string = "\n"
                                test_string2 = ".              -"
                                test_string3 = ".                   -"
                                test_string4 = test_string + test_string3
                                
                                records_list = field_content.split(",")
                                
                                field_content = ""
                                
                                records_count = 0
                                
                                line_break_count = 1
                                
                                temp_sum_line = 0
                                
                                for actual_record in records_list:
                                
                                    temp_sum_line = len(field_content) + len(actual_record)
                                
                                    #If length of string plus new content is greater than the line width with margin, introduce
                                    #a new indented line
                                
                                    if temp_sum_line >= 80 * line_break_count:
                                    
                                        field_content += test_string4
                                        line_break_count += 1
                                    
                                    field_content += str(actual_record)+","
                                    
                                    records_count += 1
                                    
                                
                                field_content += test_string + test_string2
                            
                            elif (len(pdf_string.split("\n")[-1]) + len(" "+field_name+" "+field_content)) > 104:
                                test_string = "\n"
                                test_string2 = ".              -"
                                test_string4 = ""
                            else:
                                test_string = ""
                                test_string2 = ""
                                test_string4 = ""
                            
                            if field_content != "MISSING" and field_content != "UNREADABLE" and "Field" not in field_content and field_content !="" and field_content !="None":
                                
                                pdf_string += " "+test_string+test_string2+field_name+ test_string4 +" "+field_content
                                
                                if pdf_string.count('\n') > 50:
                
                                    pdf_string += '\n'
                    
                                    pdf_string_templist = pdf_string.split('\n')
                                    pdf_string = ""
                                    pdf_string_temp = ""
                
                                    iterator_index = 0
                                    iterator_set = 0
                                    
                                    
                                    for list_element in pdf_string_templist:
                
                                        iterator_index += 1
                                        iterator_set += 1
                                        pdf_string_temp += list_element
                                        pdf_string_temp += '\n'
                                        
                                        if iterator_set > 50 or iterator_index == len(pdf_string_templist)+1:
                                            
                                            iterator_set = 0
                                        
                                            tmpfile = tempfile.SpooledTemporaryFile(1048576)
                                
                                            # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                                            tmpfile.rollover()
                                          
                                            the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                                            string_to_pdf(the_canvas,pdf_string_temp)
                                                   
                                            the_canvas.save()
                                            
                                            input1 = PdfFileReader(tmpfile)
                                            
                                            output.append(input1)
                                            
                                            pdf_string_temp = ""
                                            
                                            

                                            did_page_jump = True
                                
                              
                        except:
                            test_string = ""
                        
                    except:
                        pdf_string += " "
                        
                
                '''Write command to output the existing pdf_string variable as a new row, then line break'''
                
                pdf_string += '\n'
                pdf_string += '\n'
                
                '''if pdf_string.count('\n') > 45:
                
                    tmpfile = tempfile.SpooledTemporaryFile(1048576)
        
                    # temp file in memory of no more than 1048576 bytes (or it gets written to disk)
                    tmpfile.rollover()
                  
                    the_canvas = canvas.Canvas(tmpfile,pagesize=A4)
                    string_to_pdf(the_canvas,pdf_string)
                           
                    the_canvas.save()
                    
                    input1 = PdfFileReader(tmpfile)
                    
                    output.append(input1)
                    
                    pdf_string = ""

                    did_page_jump = True'''
                    
                exhibit_count += 1
                doc_iterator = exhibit_count - 1
        
        
        
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

        temp_filename = "legaldiscoverytemp/output_files/"+"transactions"+"/"+"transactions__"+str(watermark_name)+"__partial__"+str(corpus_doccount).zfill(7)+".pdf"
        corpus_doccount += 1
        output.write(temp_filename)
        output_temp_documents_created.append(temp_filename)
        
        output = PdfFileMerger()
        
        db.reset_queries()
        
    except:
    
        print "empty"        

def merge_corpus_output(request,watermark_name):

    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""

    corpus_to_include = str(corpus_to_include)


    file_list = os.listdir('legaldiscoverytemp/output_files/'+corpus_to_include+'/')

    file_list = sorted(file_list)

    final_output = PdfFileMerger()


    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+str(corpus_to_include)+"__"+str(watermark_name)+"__cover__0000001.pdf"
    

    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    

    partial_output = PdfFileMerger()

    outputStream = StringIO()

    #Line added to include the cover in the .zip file
    partial_output.append(PdfFileReader(file(partial_filename, 'rb')))
    
    #final_output.append(PdfFileReader(temp_outputStream))
    
    count = 0

    for filename in file_list:
        print "---->"+str(filename)
                  
        #final_output.append(PdfFileReader(temp_output_item))
        if corpus_to_include in filename and "partial" in filename:
            print "---->"+str(corpus_to_include) 
            partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+filename
            partial_output.append(PdfFileReader(file(partial_filename, 'rb')))

            count += 1
   
    #To isolate the generated report for the selected corpus

    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count)+"_files.pdf"

    partial_output.write(partial_filename)

    ##
    
    final_output.append(PdfFileReader(file(partial_filename, 'rb')))

    final_output.write(outputStream)

    ##
    
    myZipFile = shutil.make_archive("legaldiscoverytemp/output_files_final/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count+1)+"_files", "zip", "legaldiscoverytemp/output_files"+"/"+corpus_to_include)
    #myZipFile.write(outputStream)

    test_file = open("legaldiscoverytemp/output_files_final/"+corpus_to_include+"/"+corpus_to_include+"__"+str(watermark_name)+"__merge__"+str(count+1)+"_files.zip", "rb")

    ###
    
    ##If .pdf instead
    #response = HttpResponse(mimetype="application/pdf")
    #response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files/legal_discovery_report_%s.pdf' %(title_date)

    response = HttpResponse(test_file, mimetype="application/zip")

    title_date = str(datetime.datetime.now().replace(tzinfo=timezone.utc))
    
    response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files_final/'+corpus_to_include+'/'+corpus_to_include+'__'+str(watermark_name)+'__'+str(count+1)+'_files_report__%s.zip' %(title_date)

    ##If .pdf instead, this line is necessary:
    #response.write(outputStream.getvalue())
    return response
    
def download_file_output(request,watermark_name):

    try:
        corpus_to_include = request.POST["selected_corpus_mark"]
    except:
        corpus_to_include = ""

    corpus_to_include = str(corpus_to_include)

    try:
        file_to_include = request.POST["selected_file_mark"]
    except:
        file_to_include = ""

    file_to_include = str(file_to_include)
        

    final_output = PdfFileMerger()

    
    outputStream = StringIO()
    

    partial_filename = "legaldiscoverytemp/output_files/"+corpus_to_include+"/"+str(file_to_include)
    

    final_output.append(PdfFileReader(file(partial_filename, 'rb')))
    

    final_output.write(outputStream)


    ###

    ##If .pdf instead
    response = HttpResponse(mimetype="application/pdf")

    response['Content-Disposition'] = 'attachment; filename=legaldiscoverytemp/output_files/'+corpus_to_include+'/'+str(file_to_include)


    ##If .pdf instead, this line is necessary:
    response.write(outputStream.getvalue())

    return response
    
    
def create_instance_watermark(request,watermark_name):

    new_watermark = id_generator()
    
    delete_temp_affidavit_files("all","all")
    
    AffidavitInstance.objects.all().delete()
    
    new_AffidavitInstance = AffidavitInstance()
    new_AffidavitInstance.watermark_name = new_watermark
    
    new_AffidavitInstance.save()
    
    return new_watermark
    
def affidavit_watermark_everything(corpus_common_final):

    #Brings up a new watermark of 8 digits
    
    new_watermark = id_generator()

    
def delete_temp_affidavit_files(corpus,partial_or_merge):

    corpus_list = ["icr","sourcepdfs","grandelivre","albaraka","transactions"]

    file_list = []
    
    if corpus == "all":
    
        for corpus_type in corpus_list:
            print corpus_type
            temp_list = os.listdir('legaldiscoverytemp/output_files/'+corpus_type+"/")#os.chdir('legaldiscoverytemp/output_files')
            file_list.extend(temp_list)
    
    else:
    
        file_list = os.listdir('legaldiscoverytemp/output_files/'+corpus+"/")#os.chdir('legaldiscoverytemp/output_files')
        
    for item in file_list:
    
        to_remove = False

        if partial_or_merge == "all":
            
                to_remove = True

        if ".pdf" in str(item):

            if corpus in str(item):

                if partial_or_merge == "partial":
                
                    if "partial" in str(item):
                    
                        to_remove = True
                
                if partial_or_merge == "merge":    
                
                    if "merge" in str(item):
                    
                        to_remove = True
                
                if partial_or_merge == "cover":  
                
                    if "cover" in str(item):
                    
                        to_remove = True
          

            if to_remove == True:    
        
                if corpus == "all":
                    for corpus_type in corpus_list:
            
                        try:
                            os.remove('legaldiscoverytemp/output_files/'+corpus_type+'/'+str(item))    
                        except:
                            print "Not in that folder"
                            
                            try:
                                os.remove('legaldiscoverytemp/output_files_final/'+corpus_type+'/'+str(item))    
                            except:
                                "Not in that folder"
                            

                else:

                    try:
                        os.remove('legaldiscoverytemp/output_files/'+corpus+'/'+str(item))    
                    except:
                        print "Not in that folder"
                            
                        try:
                            os.remove('legaldiscoverytemp/output_files_final/'+corpus+'/'+str(item))    
                        except:
                            "Not in that folder"
                            
    
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))