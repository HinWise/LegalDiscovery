import datetime
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User,Group
from django.db.models.signals import post_save


    
class InternalRecord(models.Model):
        
    AccountNum = models.CharField('Account Number',max_length=255)
    Company = models.CharField('Company',max_length=255)
    NoMvt = models.CharField('Number Movement',max_length=255)
    Journal = models.CharField('Journal',max_length=255)
    Day = models.CharField('Day',max_length=255)
    Month = models.CharField('Month',max_length=255)
    Year = models.CharField('Year',max_length=255)
    LedgerYear = models.CharField('Year',max_length=255)
    NoPiece = models.CharField('PieceNumber',max_length=255)
    Memo = models.CharField('Memo',max_length=255)
    S = models.CharField('S',max_length=255)
    Debit = models.CharField('Debit',max_length=255)
    Lett = models.CharField('Lett',max_length=255)    
    Credit = models.CharField('Credit',max_length=255)
    def __unicode__(self):
        return self.Memo  
   
        
class Record(models.Model):
    name = models.CharField(max_length=300, default="None")
    modification_date = models.DateTimeField('last date modified', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    modification_author = models.CharField(max_length=200, default="No one")
    datetime_date = models.DateTimeField('joined day/month/year of internalrecord linked',null=True, blank=True)
    commentary = models.CharField(max_length=2000, default="None")
    skip_counter = models.CharField(max_length=10, default='0')
    status = models.CharField(max_length=100, default="unlinked")
    linked_style_class = models.CharField(max_length=255, default="nolink")
    error_style_class = models.CharField(max_length=255, default="noerror")
    internalrecord_link = models.ForeignKey(InternalRecord)
    def __unicode__(self):
        return self.status


class UserInterfaceType(models.Model):
    name = models.CharField(max_length=255,default='Linking Interface')
    redirection_url = models.CharField(max_length=255,default='linkui/spiderweb/')
    def __unicode__(self):
        return self.name

class ExtractionField(models.Model):
    name = models.CharField(max_length=127, default="unnamed")
    pretty_name = models.CharField(max_length=127, default="Unnamed")
    real_field_name = models.CharField(max_length=127, default="NeedsInput")
    importance = models.IntegerField(default=0)
    checked = models.CharField(max_length=31,default="checked")
    field_sorting = models.CharField(max_length=31, default="default")

    def __unicode__(self):
        return self.name      
    
    class Meta:
        ordering = ['name']   
    
class ExtractionFieldTemplate(models.Model):
    name = models.CharField(max_length=127, default="unnamed")
    pretty_name = models.CharField(max_length=127, default="Unnamed")
    real_field_name = models.CharField(max_length=127, default="NeedsInput")
    importance = models.IntegerField(default=0)
    checked = models.CharField(max_length=31,default="checked")
    sequential_order = models.IntegerField(default=0)
    field_sorting = models.CharField(max_length=31, default="default")
    modification_date = models.DateTimeField('modification time of extraction field template', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    creation_user = models.ForeignKey(User,null=True,blank=True) 
    
    def __unicode__(self):
        return self.name      
    
    class Meta:
        ordering = ['modification_date']
    
class SourceDocType(models.Model):
    name = models.CharField(max_length=255, default="uncategorized")
    pretty_name = models.CharField(max_length=255, default="Uncategorized")
    clean_name = models.CharField(max_length=255, default="uncategorized" )
    extraction_fields = models.ManyToManyField(ExtractionField,related_name='extraction fields list', null=True, blank=True, default=None)
    number_extraction_fields = models.IntegerField(default=0)
    min_show = models.IntegerField(default=1)
    max_show = models.IntegerField(default=1)
    min_selected = models.IntegerField(default=1)
    max_selected = models.IntegerField(default=1)
    checked = models.CharField(max_length=31,default="checked")
    extraction_fields_sorting = models.CharField(max_length=31, default="importance")
    
    '''def __init__(self, *args, **kwargs):
        super(SourceDocType, self).__init__(*args, **kwargs)
        self.clean_name = self.name.lower().replace("'","").replace(" ","_")'''
        
    def save(self, *args, **kwargs):
        
        self.clean_name = self.name.lower().replace("'","").replace(" ","_")
        
        super(SourceDocType, self).save(*args, **kwargs)
        self.number_extraction_fields = len(self.extraction_fields.all())
        super(SourceDocType, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
    
    def related_extraction_fields(self):
        '''extraction_fields_names_list = ""
        extraction_fields_data_list = self.extraction_fields.all()
        for item in extraction_fields_data_list:
            extraction_fields_names_list += item.name + " , "
            
        return extraction_fields_names_list'''
        return self.extraction_fields.all().values_list('name',flat=True).order_by('importance')
        
    related_extraction_fields.short_description = 'Assigned Extraction Fields'
    
class SourceDocTypeTemplate(models.Model):
    name = models.CharField(max_length=255, default="uncategorized")
    pretty_name = models.CharField(max_length=255, default="Uncategorized")
    clean_name = models.CharField(max_length=255, default="uncategorized")
    extraction_fields = models.ManyToManyField(ExtractionFieldTemplate,related_name='extraction fields list', null=True, blank=True, default=None)
    number_extraction_fields = models.IntegerField(default=0)
    sequential_order = models.IntegerField(default=0)
    min_show = models.IntegerField(default=1)
    max_show = models.IntegerField(default=1)
    min_selected = models.IntegerField(default=1)
    max_selected = models.IntegerField(default=1)
    checked = models.CharField(max_length=31,default="checked")
    extraction_fields_sorting = models.CharField(max_length=31, default="modification_date")
    modification_date = models.DateTimeField('modification time of sourcedoc template', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    creation_user = models.ForeignKey(User,null=True,blank=True)
    
    '''def save(self, *args, **kwargs):
        
        self.clean_name = self.name.lower().replace("'","").replace(" ","_")
        self.number_extraction_fields = len(self.extraction_fields.all())
        super(SourceDocType, self).save(*args, **kwargs) '''
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['modification_date']
    
    def related_extraction_fields(self):
        '''extraction_fields_names_list = ""
        extraction_fields_data_list = self.extraction_fields.all()
        for item in extraction_fields_data_list:
            extraction_fields_names_list += item.name + " , "
            
        return extraction_fields_names_list'''
        return self.extraction_fields.all().values_list('name',flat=True).order_by('modification_date')
    related_extraction_fields.short_description = 'Assigned Extraction Fields'

class LegalDiscoveryTemplate(models.Model):
    name = models.CharField(max_length=127, default="Saved Template ")
    creation_date = models.DateTimeField('creation time of template', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    modification_date = models.DateTimeField('modification time of template', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    general_sorting = models.CharField(max_length=31, default="modification_date")
    creation_user = models.ForeignKey(User,null=True,blank=True)
    sourcedoctypes_list = models.ManyToManyField(SourceDocTypeTemplate,related_name='source doc template list', null=True, blank=True, default=None)
    
    
    '''def __init__(self, *args, **kwargs):
        super(LegalDiscoveryTemplate, self).__init__(*args, **kwargs)
        if self.name == "Saved Template ":
            self.name = self.name + str(self.pk)'''
        
        
    def __unicode__(self):
        return self.name      
    
    class Meta:
        ordering = ['creation_date'] 

    def related_sourcedoctypes_list(self):
        
        return self.sourcedoctypes_list.all().values_list('name',flat=True).order_by('modification_date')
        

class LotNumber(models.Model):

    lot_number = models.IntegerField(default=0,db_index = True)
    
    def __unicode__(self):
        return str(self.lot_number)
        
class SourcePdfToHandle(models.Model):
    checked = models.CharField(max_length=255, default="unchecked",db_index = True)
    times_checked = models.IntegerField(default=0)
    lot_number = models.IntegerField(default=0,db_index = True)
    date_checked = models.DateTimeField('date the document was checked by someone',null=True, blank=True)
    assignedcompany = models.ForeignKey(Group)
    assigneduser = models.ForeignKey(User)
    
    def __unicode__(self):
        return str(self.id) + " | " + str(self.assignedcompany.name) + " | " + str(self.assigneduser.username) + " | " + str(self.checked)
    class Meta:
        ordering = ['assignedcompany']         
        
class SourcePdf(models.Model):
    job_directory = models.CharField('Job directory',max_length=255)
    filename = models.CharField('Pdf filename',max_length=255)
    document_type = models.CharField(max_length=255, default="uncategorized")
    original_document_type = models.ForeignKey(SourceDocType,null=True,blank=True,related_name='source_original_document_type')
    original_document_type_string = models.CharField('DocType before using Category Changer Tool',max_length=255,default='No change')
    modified_document_type = models.ForeignKey(SourceDocType,null=True,blank=True,related_name='source_modified_document_type')
    modification_doctype_date = models.DateTimeField('last time doctype date modified', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    modification_doctype_author = models.ForeignKey(User,null=True,blank=True)
    size = models.CharField('Pdf size',max_length=255,default="none")
    multipart = models.CharField('Multipart document',max_length=255,default="none")
    multipart_num_total = models.CharField('Multipart Parts',max_length=255,default="none")
    multipart_filename = models.CharField('Multipart Filename',max_length=255,default="none")
    corrupt = models.CharField('Corrupt',max_length=255,default="no")
    visitedonce = models.CharField(max_length=255,default="none")
    Day = models.CharField('Day',max_length=31,default="")
    Month = models.CharField('Month',max_length=31,default="")
    Year = models.CharField('Year',max_length=31,default="")
    FullDate = models.CharField('Year',max_length=31,default="")
    Currency = models.CharField('Currency',max_length=63,default="")
    
    
    
    assigndata = models.ManyToManyField(SourcePdfToHandle,null=True, blank=True, default=None)
    def __unicode__(self):
        return self.filename
    class Meta:
        ordering = ['filename'] 
    def related_company(self):
        company_list = ""
        assigndata_list = self.assigndata.all()
        for item in assigndata_list:
            company_list += item.assignedcompany.name + " | "
            
        return company_list
    related_company.short_description = 'Assigned Companies'
    def related_author(self):
        author_list = ""
        assigndata_list = self.assigndata.all()
        for item in assigndata_list:
            author_list += item.assigneduser.username + " | "
            
        return author_list
    related_author.short_description = 'Assigned Data Entry Users'
    def related_checked(self):
        checked_list = ""
        assigndata_list = self.assigndata.all()
        for item in assigndata_list:
            checked_list += item.checked + " | "
            
        return checked_list
    related_checked.short_description = 'Data Entry Completed/Checked?'

    

        
class OcrRecord(models.Model):
    Document_Type = models.CharField('Document Type',max_length=255)
    Amount = models.CharField('Amount',max_length=255)
    Currency = models.CharField('Currency',max_length=255)
    Company = models.CharField('Company',max_length=255)
    Address = models.CharField('Address',max_length=255)
    Telephone = models.CharField('Telephone',max_length=255)
    City = models.CharField('City',max_length=255)
    Country = models.CharField('City',max_length=255)
    IssueDate = models.CharField('IssueDate',max_length=255)
    Day = models.CharField('Issue Day',max_length=255)
    Month = models.CharField('Issue Month',max_length=255)
    Year = models.CharField('Issue Year',max_length=255)
    Document_Number = models.CharField('Document Number',max_length=255)
    PurchaseOrder_Number = models.CharField('Purchase Order Number',max_length=255)
    Piece_Number = models.CharField('Piece Number',max_length=255)
    ContainsArabic = models.CharField('ContainsArabic',max_length=255)
    Page_Number = models.CharField('Page Number',max_length=255)
    Notes = models.CharField('Notes',max_length=255)
    Translation_Notes = models.CharField(max_length=255, default="NoTranslationField")
    Source_Bank_Account = models.CharField('Source Bank Account',max_length=255)
    Cheque_Number = models.CharField('Cheque Number for Remise de Cheques',max_length=255, default="NoChequeNumberField")
    Blank = models.CharField('Blank',max_length=255)
    Unreadable = models.CharField('Unreadable',max_length=255)
    OcrByCompany = models.ForeignKey(Group)
    OcrAuthor = models.ForeignKey(User)
    OcrCreationDate = models.CharField('OcrCreationDate',max_length=255)
    
    def __unicode__(self):
        return self.Company

class CompanyOriginal(models.Model):
    ledgeryear_original = models.CharField(max_length=255, default="None")
    accountnumber_original = models.CharField(max_length=255, default="None")
    companyname_original = models.CharField(max_length=255, default="None")
    def __unicode__(self):
        return self.companyname_original
    
class CompanyTemplate(models.Model):
    companyname_base = models.CharField(max_length=255, default="None",db_index = True)
    companyaddress_base = models.CharField(max_length=255, default="None")
    companytelephone_base = models.CharField(max_length=255, default="None")
    companycity_base = models.CharField(max_length=255, default="None")
    companycountry_base = models.CharField(max_length=255, default="None")
    company_original = models.ForeignKey(CompanyOriginal)
    def __unicode__(self):
        return self.company_original
    
    class Meta:
        ordering = ['companyname_base']

class PdfRecord(models.Model):
    name = models.CharField(max_length=255, default="Pdf Record")
    modification_date = models.DateTimeField('last date modified', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    modification_author = models.CharField(max_length=255, default="Xanto")
    datetime_date = models.DateTimeField('joined day/month/year of ocrrecord linked',null=True, blank=True)
    modified_document_type = models.ForeignKey(SourceDocType,null=True,blank=True,related_name='pdf_modified_document_type')
    modified_doctype_from = models.CharField(max_length=255, default="uncategorized")
    original_document_type = models.ForeignKey(SourceDocType,null=True,blank=True,related_name='pdf_original_document_type')
    modified_doctype_date = models.DateTimeField('last time doctype date modified', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    modified_doctype_author = models.ForeignKey(User,null=True,blank=True,related_name='pdf_modified_doctype_author')
    commentary = models.CharField(max_length=512, default="None")
    audit_mark = models.CharField(max_length=512, default="None")
    audit_mark_saved = models.CharField(max_length=512, default="None")
    audit_mark_revision = models.CharField(max_length=512, default="None")
    status = models.CharField(max_length=255, default="pdf_unlinked")
    translated = models.CharField(max_length=255, default="no")
    createdbymean = models.CharField(max_length=255, default="none")
    linked_style_class = models.CharField(max_length=255, default="nolink")
    error_style_class = models.CharField(max_length=255, default="noerror")
    skip_counter = models.CharField(max_length=10, default='0')
    record_link = models.ForeignKey(Record)
    sourcedoc_link = models.ForeignKey(SourcePdf)
    ocrrecord_link = models.ForeignKey(OcrRecord)
    companytemplate_link = models.ForeignKey(CompanyTemplate)
    EntryByCompany = models.ForeignKey(Group,null=True,blank=True)
    EntryAuthor = models.ForeignKey(User,null=True,blank=True)
    AssignedLotNumber = models.ForeignKey(LotNumber,null=True,blank=True)
    def __unicode__(self):
        return self.name
    
        
class FilterSearchWords(models.Model):
    pdf_searchword = models.CharField(max_length=255, default="all")
    pdf_filterword = models.CharField(max_length=255, default="pdf_all")
    def __unicode__(self):
        return self.pdf_filterword

class Report(models.Model):
    report_type = models.CharField(max_length=31, default="None")
    report_subtype = models.CharField(max_length=31, default="None")
    report_memo = models.CharField(max_length=255, default="")
    report_author = models.ForeignKey(User)
    report_company = models.ForeignKey(Group)
    report_date = models.DateTimeField('date the report was created', default=datetime.datetime.now().replace(tzinfo=timezone.utc))
    report_viewed = models.CharField(max_length=7, default="No")
    def __unicode__(self):
        return self.report_memo

        
class UserProfile(models.Model):  
    user = models.OneToOneField(User)
    user_company = models.ForeignKey(Group,null=True,blank=True)
    assignation_locked = models.CharField(max_length=31, default="not_locked")
    modifiedsourcepdfs_categorization_tool = models.ManyToManyField(SourcePdf,related_name='sourcepdfs_modified_categorization_tool', null=True, blank=True, default=None)
    modifiedsourcepdfs_blank_or_not_tool = models.ManyToManyField(SourcePdf,related_name='sourcepdfs_modified_blank_or_not_blank_tool', null=True, blank=True, default=None)
    modifiedpdfs_categorization_tool = models.ManyToManyField(PdfRecord,related_name='pdfs_modified_categorization_tool', null=True, blank=True, default=None)
    modifiedpdfs_translated_arabic = models.ManyToManyField(PdfRecord,related_name='pdfs_translated_arabic', null=True, blank=True, default=None)
    modifiedpdfs_audit_marked = models.ManyToManyField(PdfRecord,related_name='pdfs_audit_marked', null=True, blank=True, default=None)
    modifiedpdfs_audit_saved = models.ManyToManyField(PdfRecord,related_name='pdfs_audit_saved', null=True, blank=True, default=None)
    modifiedpdfs_audit_revision = models.ManyToManyField(PdfRecord,related_name='pdfs_audit_revisioned', null=True, blank=True, default=None)
    created_legaldiscovery_templates = models.ManyToManyField(LegalDiscoveryTemplate,related_name='legaldiscovery_templates', null=True, blank=True, default=None)
    #other fields here

    
    
    def __str__(self):  
          return "%s's profile" % self.user 

    def admin_created_legaldiscovery_templates(self):
        
        return self.created_legaldiscovery_templates.all().values_list('name',flat=True)     
    
    
     
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
        
        profile, created = UserProfile.objects.get_or_create(user=instance)  

        
post_save.connect(create_user_profile, sender=User)



class GroupProfile(models.Model):  
    group = models.OneToOneField(Group)
    unique_lot_number_list = models.ManyToManyField(LotNumber,related_name='lot_number_list', null=True, blank=True, default=None)
    
    
    def __str__(self):  
          return "%s's profile" % self.group 

     
def create_group_profile(sender, instance, created, **kwargs):  
    if created:  
        
        profile, created = GroupProfile.objects.get_or_create(group=instance)  

        
post_save.connect(create_group_profile, sender=Group)


