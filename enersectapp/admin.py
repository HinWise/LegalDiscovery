from django import forms
from django.forms import ModelMultipleChoiceField
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from enersectapp.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User,Group
from django.utils.translation import ugettext, ugettext_lazy as _
from django.shortcuts import render


def make_teamuser(modeladmin, request, queryset):
    
    
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders")[0]
    
    for user_item in queryset:
        if len(user_item.groups.all())==0:
            if user_item.groups.exclude(name=user_group.name):
                user_item.groups.add(user_group)
                user_item.is_staff = True
                user_item.is_active = True
                user_item.save()
                user_profile = UserProfile.objects.get(user = user)
                user_profile.user_company = user_group
                user_profile.save()
            
            
    '''if obj.is_superuser == False:
                if obj.username != the_user.username:
                    
                    obj.groups = user_group'''
    #queryset.update(groups=user_group)
    
make_teamuser.short_description = "Include Selected Users in your Company Team"


def assign_selected_to_user(modeladmin, request, queryset):
    
    the_user = request.user
    user_group = the_user.groups.all().exclude(name="TeamLeaders")[0]
    all_groups = Group.objects.all().exclude(name="TeamLeaders")
    all_users_from_group_not_myself = User.objects.filter(groups=user_group).exclude(username=the_user.username)
    sourcepdfs_list = ""
    
    for source in queryset:
        sourcepdfs_list += (str(source.id)+"|")
        
    
    if request.user.is_superuser:
            
            context = {'the_user':the_user,'user_group':user_group,'all_groups':all_groups,
            'sourcepdfs_list':sourcepdfs_list}
            return render(request,'enersectapp/sudo_assignsourcepdfsui.html',context)
            
    else:
        
        context = {'the_user':the_user,'user_group':user_group,'all_users_from_group_not_myself':all_users_from_group_not_myself,
        'sourcepdfs_list':sourcepdfs_list}
        return render(request,'enersectapp/lead_assignsourcepdfsui.html',context)
        
    
    '''for document in queryset:
        print document.job_directory'''
            
    '''if obj.is_superuser == False:
                if obj.username != the_user.username:
                    
                    obj.groups = user_group'''
    #queryset.update(groups=user_group)
    #print queryset
assign_selected_to_user.short_description = "Assign Selected Documents to a Team User"


class RecordAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Record Details",               {'fields': ['name','status','commentary','skip_counter',]}),
    ("Versioning Information",               {'fields': ['modification_date','modification_author','internalrecord_link']}),]
    list_display = ('name','skip_counter', 'status', 'commentary','modification_date','modification_author','internalrecord_link')
    
    list_filter = ['status']
    search_fields = ['status','modification_author']
    date_hierarchy = 'modification_date'
    
class PdfRecordAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Record Details",               {'fields': ['status','commentary','sourcedoc_link','companytemplate_link']}),
    ("Versioning Information",               {'fields': ['modification_date','modification_author','createdbymean','linked_style_class','error_style_class']}),]
    list_display = ('ocrrecord_link','sourcedoc_link','modified_document_type','id','record_link','status','audit_mark','audit_mark_saved','audit_mark_revision','commentary','modification_date','modification_author')
    
    ''','record_link','sourcedoc_link','ocrrecord_link','companytemplate_link'''
    search_fields = ['status','modified_document_type__name','audit_mark','audit_mark_saved','audit_mark_revision','modification_author','commentary','sourcedoc_link__filename','ocrrecord_link__OcrByCompany__name']
    
    
class OcrRecordAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Main Details",               {'fields': ['Amount', 'Company','IssueDate','Day','Month','Year','Document_Type']}),
    ("Extra Details",               {'fields': ['Currency', 'Address','City','Telephone','Country','Source_Bank_Account','PurchaseOrder_Number','Document_Number','Piece_Number','Page_Number']}),
    ("Tech Details",               {'fields': ['ContainsArabic','Blank','Notes','Unreadable','OcrByCompany','OcrAuthor','OcrCreationDate']}),]
    list_display = ('Document_Number','Amount','Company','Document_Type','OcrByCompany','OcrAuthor','OcrCreationDate', 'IssueDate','id','Source_Bank_Account','Page_Number','Piece_Number','Translation_Notes')
    
   
    search_fields = ['Document_Number','Amount','Company','IssueDate','=Document_Type','OcrByCompany__name','OcrAuthor__username']
    
    
class InternalRecordAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Record Details",               {'fields': ['Credit', 'Debit','Company','Day','Month','Year','LedgerYear','Memo']}),]
    list_display = ('Credit', 'Debit','Company','Day','Month','Year','LedgerYear','Memo')
    
    
    search_fields = ['Credit', 'Debit','Company','Day','Month','Year','LedgerYear','Memo']



class ExtractionFieldAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Extraction Field Details",               {'fields': ['name', 'pretty_name','real_field_name','importance','checked','field_sorting']}),]
    list_display = ('id','name', 'pretty_name','real_field_name','importance','checked','field_sorting')
    
    search_fields = ['id','name', 'pretty_name','real_field_name','importance','checked','field_sorting']

class ExtractionFieldTemplateAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Extraction Field Template Details",               {'fields': ['name', 'pretty_name','real_field_name','importance','checked','field_sorting']}),]
    list_display = ('id','sequential_order','name', 'pretty_name','real_field_name','importance','checked','field_sorting','modification_date','creation_user')
    
    search_fields = ['id','name', 'pretty_name','real_field_name','importance','checked','field_sorting','creation_user__username']
    
class SourceDocTypeAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Source Doc Type Details",               {'fields': ['name', 'pretty_name','extraction_fields']}),
    ("Optional Details",               {'fields': ['min_show','max_show','min_selected','max_selected','extraction_fields_sorting']}),
    ]
    list_display = ('id','name', 'pretty_name','clean_name','related_extraction_fields','number_extraction_fields','checked','min_show','max_show','min_selected','max_selected','extraction_fields_sorting')
    
    filter_horizontal = ('extraction_fields',)
    
    search_fields = ['id','name', 'pretty_name','clean_name','=checked','number_extraction_fields','min_show','max_show','min_selected','max_selected','extraction_fields_sorting']
    
    
class SourceDocTypeTemplateAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Source Doc Type Details",               {'fields': ['name', 'pretty_name','extraction_fields']}),
    ("Optional Details",               {'fields': ['min_show','max_show','min_selected','max_selected','extraction_fields_sorting']}),
    ]
    list_display = ('id','sequential_order','name', 'pretty_name','clean_name','related_extraction_fields','modification_date','creation_user','checked','min_show','max_show','min_selected','max_selected','extraction_fields_sorting')
    
    filter_horizontal = ('extraction_fields',)
    
    search_fields = ['id','name', 'pretty_name','clean_name','=checked','min_show','max_show','min_selected','max_selected','extraction_fields_sorting','creation_user__username']
    
class SourcePdfToHandleInline(admin.TabularInline):
    model = SourcePdfToHandle

class SourcePdfToHandleAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Source Pdf To Handle Details",               {'fields': ['checked', 'times_checked','assignedcompany','assigneduser','lot_number']}),]
    list_display = ('id','checked', 'times_checked','assignedcompany','assigneduser','lot_number')
    
    search_fields = ['id','=checked', 'times_checked','assignedcompany__name','assigneduser__username','lot_number']

class LegalDiscoveryTemplateAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Legal Discovery Template Details",               {'fields': ['name','general_sorting']}),]
    list_display = ('id','name', 'general_sorting','creation_date','modification_date','creation_user','related_sourcedoctypes_list')
    
    search_fields = ['id','=checked', 'general_sorting', 'times_checked','assignedcompany__name','assigneduser__username','sourcedoctypes_list__name']    


    
'''class SourcePdfForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(SourcePdfForm, self).__init__(*args, **kwargs)
        wtf = SourcePdfToHandle.objects.all();
        w = self.fields['assigndata'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.assignedcompany))
            print choice
        w.choices = choices'''
    
class SourcePdfAdmin(admin.ModelAdmin):
    #inlines = [SourcePdfToHandleAdmin,]
    
    actions = [assign_selected_to_user]
    
    fieldsets = [
    ("Source Pdf Details",               {'fields': ['job_directory', 'filename','document_type','visitedonce']}),]
    list_display = ('filename', 'job_directory','document_type','visitedonce','related_company','related_author','related_checked','modification_doctype_author','modification_doctype_date','modified_document_type')
    
    search_fields = ['filename', 'job_directory','document_type','visitedonce','modification_doctype_author__username','modification_doctype_date']
    
    
    def queryset(self, request):
   
        if request.user.is_superuser:
            return SourcePdf.objects.all()
        
        the_user = request.user
        user_group = the_user.groups.all().exclude(name="TeamLeaders")[0]
            
        return SourcePdf.objects.filter(assigndata__assignedcompany=user_group)

    
class CompanyOriginalAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Company Original Details",               {'fields': ['ledgeryear_original', 'accountnumber_original','companyname_original']}),]
    list_display = ('ledgeryear_original', 'accountnumber_original','companyname_original')
    
    search_fields = ['ledgeryear_original', 'accountnumber_original','companyname_original']


class CompanyTemplateAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Source Pdf Details",               {'fields': ['companyname_base', 'companyaddress_base','companytelephone_base','companycity_base','companycountry_base','company_original']}),]
    list_display = ('companyname_base', 'companyaddress_base','companytelephone_base','companycity_base','companycountry_base','company_original')
    
    
    search_fields = ['companyname_base', 'companyaddress_base','companytelephone_base','companycity_base','companycountry_base','company_original']

    
class ReportAdmin(admin.ModelAdmin):
    fieldsets = [
    ("Report Details",               {'fields': ['report_type', 'report_memo','report_author','report_company','report_date','report_viewed']}),]
    list_display = ('report_type', 'report_subtype','report_memo','report_author','report_company','report_date','report_viewed')
    
    
    search_fields = ['report_type', 'report_subtype','report_memo','report_author__username','report_company__name','report_date','report_viewed']

'''class UserProfileForm(forms.ModelForm): 
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        assignedsourcepdfs = ModelMultipleChoiceField(
        queryset=SourcePdf.objects.order_by('filename'), 
        required=False, widget=FilteredSelectMultiple)
        
        
        
        Keep this part commented
        wtf = SourcePdfToHandle.objects.all();
        w = self.fields['assigndata'].widget
        choices = []
        for choice in wtf:
            choices.append((choice.id, choice.assignedcompany))
            print choice
        w.choices = choices'''



    
class UserProfileAdmin(admin.ModelAdmin):
    
    list_display = ('user','user_company','assignation_locked','admin_created_legaldiscovery_templates')
    
    search_fields = ['user','user_company','assignation_locked']   
    
    fieldsets = [
    ("User Profile Details",               {'fields': ['user','user_company','assignation_locked','created_legaldiscovery_templates']}),]

    filter_horizontal = ('created_legaldiscovery_templates',)
    
 
class MyUserAdmin(UserAdmin):

    def queryset(self, request):
   
        global_user = request.user
        if request.user.is_superuser:
            return User.objects.all()
        
        else:
            the_user = request.user
            user_group = the_user.groups.all().exclude(name="TeamLeaders").exclude(name="Auditors").exclude(name="TeamAuditors").exclude(name="Arabic")[0]
            all_groups = Group.objects.all()
            all_users = User.objects.all()
            non_user_groups = all_groups.exclude(name=user_group)
            user_fromgroup_and_blanks = all_users.exclude(groups=non_user_groups) 
        
            return user_fromgroup_and_blanks
        
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        
        the_user = request.user
        user_group = the_user.groups.all()
        
        
        if the_user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
            
            
            return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]
             
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            
            '''if obj.is_superuser == False:
                if obj.username != the_user.username:
                    
                    obj.groups = user_group'''
                    
            perm_fields = ('is_active',)
            
            return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]
            
            '''perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
            
            
            return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]'''
            
        
        

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(UserInterfaceType)
admin.site.register(PdfRecord, PdfRecordAdmin)
admin.site.register(OcrRecord, OcrRecordAdmin)
admin.site.register(InternalRecord, InternalRecordAdmin)
admin.site.register(SourcePdf, SourcePdfAdmin)
admin.site.register(ExtractionField, ExtractionFieldAdmin)
admin.site.register(ExtractionFieldTemplate, ExtractionFieldTemplateAdmin)
admin.site.register(SourceDocType, SourceDocTypeAdmin)
admin.site.register(SourceDocTypeTemplate, SourceDocTypeTemplateAdmin)
admin.site.register(LegalDiscoveryTemplate, LegalDiscoveryTemplateAdmin)
admin.site.register(SourcePdfToHandle, SourcePdfToHandleAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(CompanyOriginal, CompanyOriginalAdmin)
admin.site.register(CompanyTemplate, CompanyTemplateAdmin)
admin.site.register(FilterSearchWords)
