# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SourcePdf.Day'
        db.add_column(u'enersectapp_sourcepdf', 'Day',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=31),
                      keep_default=False)

        # Adding field 'SourcePdf.Month'
        db.add_column(u'enersectapp_sourcepdf', 'Month',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=31),
                      keep_default=False)

        # Adding field 'SourcePdf.Year'
        db.add_column(u'enersectapp_sourcepdf', 'Year',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=31),
                      keep_default=False)

        # Adding field 'SourcePdf.FullDate'
        db.add_column(u'enersectapp_sourcepdf', 'FullDate',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=31),
                      keep_default=False)

        # Adding field 'SourcePdf.Currency'
        db.add_column(u'enersectapp_sourcepdf', 'Currency',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=63),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SourcePdf.Day'
        db.delete_column(u'enersectapp_sourcepdf', 'Day')

        # Deleting field 'SourcePdf.Month'
        db.delete_column(u'enersectapp_sourcepdf', 'Month')

        # Deleting field 'SourcePdf.Year'
        db.delete_column(u'enersectapp_sourcepdf', 'Year')

        # Deleting field 'SourcePdf.FullDate'
        db.delete_column(u'enersectapp_sourcepdf', 'FullDate')

        # Deleting field 'SourcePdf.Currency'
        db.delete_column(u'enersectapp_sourcepdf', 'Currency')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'enersectapp.companyoriginal': {
            'Meta': {'object_name': 'CompanyOriginal'},
            'accountnumber_original': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'companyname_original': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledgeryear_original': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'})
        },
        u'enersectapp.companytemplate': {
            'Meta': {'ordering': "['companyname_base']", 'object_name': 'CompanyTemplate'},
            'company_original': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.CompanyOriginal']"}),
            'companyaddress_base': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'companycity_base': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'companycountry_base': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'companyname_base': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'companytelephone_base': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'enersectapp.filtersearchwords': {
            'Meta': {'object_name': 'FilterSearchWords'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pdf_filterword': ('django.db.models.fields.CharField', [], {'default': "'pdf_all'", 'max_length': '255'}),
            'pdf_searchword': ('django.db.models.fields.CharField', [], {'default': "'all'", 'max_length': '255'})
        },
        u'enersectapp.internalrecord': {
            'AccountNum': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Company': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Credit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Day': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Debit': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Journal': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'LedgerYear': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Lett': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Memo': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'object_name': 'InternalRecord'},
            'Month': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'NoMvt': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'NoPiece': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'S': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Year': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'enersectapp.ocrrecord': {
            'Address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Amount': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Blank': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'City': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Company': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ContainsArabic': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Currency': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Day': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Document_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Document_Type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'IssueDate': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Meta': {'object_name': 'OcrRecord'},
            'Month': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Notes': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'OcrAuthor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'OcrByCompany': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'OcrCreationDate': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Page_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Piece_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'PurchaseOrder_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Source_Bank_Account': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Telephone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Translation_Notes': ('django.db.models.fields.CharField', [], {'default': "'NoTranslationField'", 'max_length': '255'}),
            'Unreadable': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Year': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'enersectapp.pdfrecord': {
            'Meta': {'object_name': 'PdfRecord'},
            'audit_mark': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'commentary': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'companytemplate_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.CompanyTemplate']"}),
            'createdbymean': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'datetime_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'error_style_class': ('django.db.models.fields.CharField', [], {'default': "'noerror'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linked_style_class': ('django.db.models.fields.CharField', [], {'default': "'nolink'", 'max_length': '255'}),
            'modification_author': ('django.db.models.fields.CharField', [], {'default': "'Xanto'", 'max_length': '255'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)'}),
            'modified_doctype_author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'modified_doctype_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)'}),
            'modified_doctype_from': ('django.db.models.fields.CharField', [], {'default': "'uncategorized'", 'max_length': '255'}),
            'modified_document_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pdf_modified_document_type'", 'null': 'True', 'to': u"orm['enersectapp.SourceDocType']"}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Pdf Record'", 'max_length': '255'}),
            'ocrrecord_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.OcrRecord']"}),
            'original_document_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pdf_original_document_type'", 'null': 'True', 'to': u"orm['enersectapp.SourceDocType']"}),
            'record_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.Record']"}),
            'skip_counter': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'sourcedoc_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.SourcePdf']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pdf_unlinked'", 'max_length': '255'}),
            'translated': ('django.db.models.fields.CharField', [], {'default': "'no'", 'max_length': '255'})
        },
        u'enersectapp.record': {
            'Meta': {'object_name': 'Record'},
            'commentary': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '2000'}),
            'datetime_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'error_style_class': ('django.db.models.fields.CharField', [], {'default': "'noerror'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internalrecord_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.InternalRecord']"}),
            'linked_style_class': ('django.db.models.fields.CharField', [], {'default': "'nolink'", 'max_length': '255'}),
            'modification_author': ('django.db.models.fields.CharField', [], {'default': "'No one'", 'max_length': '200'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '300'}),
            'skip_counter': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unlinked'", 'max_length': '100'})
        },
        u'enersectapp.report': {
            'Meta': {'object_name': 'Report'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report_author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'report_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)'}),
            'report_memo': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'report_subtype': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '31'}),
            'report_type': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '31'}),
            'report_viewed': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '7'})
        },
        u'enersectapp.sourcedoctype': {
            'Meta': {'object_name': 'SourceDocType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'uncategorized'", 'max_length': '255'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'default': "'Uncategorized'", 'max_length': '255'})
        },
        u'enersectapp.sourcepdf': {
            'Currency': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '63'}),
            'Day': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '31'}),
            'FullDate': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '31'}),
            'Meta': {'ordering': "['filename']", 'object_name': 'SourcePdf'},
            'Month': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '31'}),
            'Year': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '31'}),
            'assigndata': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['enersectapp.SourcePdfToHandle']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'corrupt': ('django.db.models.fields.CharField', [], {'default': "'no'", 'max_length': '255'}),
            'document_type': ('django.db.models.fields.CharField', [], {'default': "'uncategorized'", 'max_length': '255'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_directory': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'modification_doctype_author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'modification_doctype_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 1, 14, 0, 0)'}),
            'modified_document_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'source_modified_document_type'", 'null': 'True', 'to': u"orm['enersectapp.SourceDocType']"}),
            'multipart': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'multipart_filename': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'multipart_num_total': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'original_document_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'source_original_document_type'", 'null': 'True', 'to': u"orm['enersectapp.SourceDocType']"}),
            'original_document_type_string': ('django.db.models.fields.CharField', [], {'default': "'No change'", 'max_length': '255'}),
            'size': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'visitedonce': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'})
        },
        u'enersectapp.sourcepdftohandle': {
            'Meta': {'ordering': "['assignedcompany']", 'object_name': 'SourcePdfToHandle'},
            'assignedcompany': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'assigneduser': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'checked': ('django.db.models.fields.CharField', [], {'default': "'unchecked'", 'max_length': '255'}),
            'date_checked': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lot_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'times_checked': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'enersectapp.userinterfacetype': {
            'Meta': {'object_name': 'UserInterfaceType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Linking Interface'", 'max_length': '255'}),
            'redirection_url': ('django.db.models.fields.CharField', [], {'default': "'linkui/spiderweb/'", 'max_length': '255'})
        },
        u'enersectapp.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'assignation_locked': ('django.db.models.fields.CharField', [], {'default': "'not_locked'", 'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedpdfs_categorization_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_modified_categorization_tool'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedpdfs_translated_arabic': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_translated_arabic'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedsourcepdfs_blank_or_not_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sourcepdfs_modified_blank_or_not_blank_tool'", 'default': 'None', 'to': u"orm['enersectapp.SourcePdf']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedsourcepdfs_categorization_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sourcepdfs_modified_categorization_tool'", 'default': 'None', 'to': u"orm['enersectapp.SourcePdf']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'user_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['enersectapp']