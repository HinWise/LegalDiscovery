
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

from pyPdf import PdfFileWriter, PdfFileReader
from urllib2 import Request, urlopen
from StringIO import StringIO

from django.db.models import Count

import json 

from django.views import generic
from django.utils import timezone
from datetime import timedelta
import datetime


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
        
        print "GOT HERE!--------------------------------------------------------->0 ALL GOES ALRIGHT"
        
        if action_mark == "choose_template":
        
            print "GOT HERE!--------------------------------------------------------->1 CHOOSEN TEMPLATE MARK"
        
            template_exists = selected_template in legaldiscovery_templates_names_list
        
            if selected_template == "New Template":
                
                print "GOT HERE!--------------------------------------------------------->2 CHOOSING NEW TEMPLATE, NORMAL ROUTE"
                
                default_method = True
        
            elif template_exists == False:
            
                print "GOT HERE!--------------------------------------------------------->3 TEMPLATE DOESNT EXIST, NORMAL ROUTE"
            
                default_method = True
            
            else:
            
                print "GOT HERE!--------------------------------------------------------->4  CHOOSING TEMPLATE THAT EXISTS"
                
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
                
                
        
        elif action_mark == "save_template" and len(stringified_legal_discovery_template) > 0:
        
            print "GOT HERE!--------------------------------------------------------->5 SAVE_TEMPLATE_MARK"
        
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
                print "GOT HERE!--------------------------------------------------------->7 SAVING NEW LEGALD TEMPLATE TYPE"
                
                with transaction.commit_on_success():
                
                    print selected_template
                
                    try:
                        new_Legal_Discovery_Template = LegalDiscoveryTemplate.objects.get(name=selected_template,creation_user=the_user)
                        
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