# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'InternalRecord'
        db.create_table(u'enersectapp_internalrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('AccountNum', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Company', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('NoMvt', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Journal', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Day', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Month', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Year', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('LedgerYear', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('NoPiece', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Memo', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('S', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Debit', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Lett', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Credit', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['InternalRecord'])

        # Adding model 'Record'
        db.create_table(u'enersectapp_record', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='None', max_length=300)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 31, 0, 0))),
            ('modification_author', self.gf('django.db.models.fields.CharField')(default='No one', max_length=200)),
            ('commentary', self.gf('django.db.models.fields.CharField')(default='None', max_length=2000)),
            ('skip_counter', self.gf('django.db.models.fields.CharField')(default='0', max_length=10)),
            ('status', self.gf('django.db.models.fields.CharField')(default='unlinked', max_length=100)),
            ('internalrecord_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.InternalRecord'])),
        ))
        db.send_create_signal(u'enersectapp', ['Record'])

        # Adding model 'UserInterfaceType'
        db.create_table(u'enersectapp_userinterfacetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Linking Interface', max_length=255)),
            ('redirection_url', self.gf('django.db.models.fields.CharField')(default='linkui/spiderweb/', max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['UserInterfaceType'])

        # Adding model 'SourcePdfToHandle'
        db.create_table(u'enersectapp_sourcepdftohandle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('checked', self.gf('django.db.models.fields.CharField')(default='unchecked', max_length=255)),
            ('times_checked', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('lot_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date_checked', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('assignedcompany', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('assigneduser', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'enersectapp', ['SourcePdfToHandle'])

        # Adding model 'SourcePdf'
        db.create_table(u'enersectapp_sourcepdf', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('job_directory', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('document_type', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('size', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('multipart', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('visitedonce', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['SourcePdf'])

        # Adding M2M table for field assigndata on 'SourcePdf'
        m2m_table_name = db.shorten_name(u'enersectapp_sourcepdf_assigndata')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sourcepdf', models.ForeignKey(orm[u'enersectapp.sourcepdf'], null=False)),
            ('sourcepdftohandle', models.ForeignKey(orm[u'enersectapp.sourcepdftohandle'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sourcepdf_id', 'sourcepdftohandle_id'])

        # Adding model 'OcrRecord'
        db.create_table(u'enersectapp_ocrrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Document_Type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Amount', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Currency', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Company', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Telephone', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('City', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Country', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('IssueDate', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Day', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Month', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Year', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Document_Number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('PurchaseOrder_Number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Piece_Number', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ContainsArabic', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Notes', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Source_Bank_Account', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Blank', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('Unreadable', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('OcrByCompany', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.Group'])),
            ('OcrAuthor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('OcrCreationDate', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['OcrRecord'])

        # Adding model 'CompanyOriginal'
        db.create_table(u'enersectapp_companyoriginal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledgeryear_original', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('accountnumber_original', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('companyname_original', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['CompanyOriginal'])

        # Adding model 'CompanyTemplate'
        db.create_table(u'enersectapp_companytemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('companyname_base', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('companyaddress_base', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('companytelephone_base', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('companycity_base', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('companycountry_base', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('company_original', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.CompanyOriginal'])),
        ))
        db.send_create_signal(u'enersectapp', ['CompanyTemplate'])

        # Adding model 'PdfRecord'
        db.create_table(u'enersectapp_pdfrecord', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Pdf Record', max_length=255)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2013, 10, 31, 0, 0))),
            ('modification_author', self.gf('django.db.models.fields.CharField')(default='Xanto', max_length=255)),
            ('commentary', self.gf('django.db.models.fields.CharField')(default='None', max_length=512)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pdf_unlinked', max_length=255)),
            ('createdbymean', self.gf('django.db.models.fields.CharField')(default='none', max_length=255)),
            ('linked_style_class', self.gf('django.db.models.fields.CharField')(default='nolink', max_length=255)),
            ('error_style_class', self.gf('django.db.models.fields.CharField')(default='noerror', max_length=255)),
            ('record_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.Record'])),
            ('sourcedoc_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.SourcePdf'])),
            ('ocrrecord_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.OcrRecord'])),
            ('companytemplate_link', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['enersectapp.CompanyTemplate'])),
        ))
        db.send_create_signal(u'enersectapp', ['PdfRecord'])

        # Adding model 'FilterSearchWords'
        db.create_table(u'enersectapp_filtersearchwords', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pdf_searchword', self.gf('django.db.models.fields.CharField')(default='all', max_length=255)),
            ('pdf_filterword', self.gf('django.db.models.fields.CharField')(default='pdf_all', max_length=255)),
        ))
        db.send_create_signal(u'enersectapp', ['FilterSearchWords'])


    def backwards(self, orm):
        # Deleting model 'InternalRecord'
        db.delete_table(u'enersectapp_internalrecord')

        # Deleting model 'Record'
        db.delete_table(u'enersectapp_record')

        # Deleting model 'UserInterfaceType'
        db.delete_table(u'enersectapp_userinterfacetype')

        # Deleting model 'SourcePdfToHandle'
        db.delete_table(u'enersectapp_sourcepdftohandle')

        # Deleting model 'SourcePdf'
        db.delete_table(u'enersectapp_sourcepdf')

        # Removing M2M table for field assigndata on 'SourcePdf'
        db.delete_table(db.shorten_name(u'enersectapp_sourcepdf_assigndata'))

        # Deleting model 'OcrRecord'
        db.delete_table(u'enersectapp_ocrrecord')

        # Deleting model 'CompanyOriginal'
        db.delete_table(u'enersectapp_companyoriginal')

        # Deleting model 'CompanyTemplate'
        db.delete_table(u'enersectapp_companytemplate')

        # Deleting model 'PdfRecord'
        db.delete_table(u'enersectapp_pdfrecord')

        # Deleting model 'FilterSearchWords'
        db.delete_table(u'enersectapp_filtersearchwords')


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
            'Piece_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'PurchaseOrder_Number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Source_Bank_Account': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Telephone': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Unreadable': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Year': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'enersectapp.pdfrecord': {
            'Meta': {'object_name': 'PdfRecord'},
            'commentary': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'companytemplate_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.CompanyTemplate']"}),
            'createdbymean': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'error_style_class': ('django.db.models.fields.CharField', [], {'default': "'noerror'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linked_style_class': ('django.db.models.fields.CharField', [], {'default': "'nolink'", 'max_length': '255'}),
            'modification_author': ('django.db.models.fields.CharField', [], {'default': "'Xanto'", 'max_length': '255'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 31, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Pdf Record'", 'max_length': '255'}),
            'ocrrecord_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.OcrRecord']"}),
            'record_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.Record']"}),
            'sourcedoc_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.SourcePdf']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pdf_unlinked'", 'max_length': '255'})
        },
        u'enersectapp.record': {
            'Meta': {'object_name': 'Record'},
            'commentary': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '2000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'internalrecord_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.InternalRecord']"}),
            'modification_author': ('django.db.models.fields.CharField', [], {'default': "'No one'", 'max_length': '200'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 10, 31, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '300'}),
            'skip_counter': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unlinked'", 'max_length': '100'})
        },
        u'enersectapp.sourcepdf': {
            'Meta': {'ordering': "['filename']", 'object_name': 'SourcePdf'},
            'assigndata': ('django.db.models.fields.related.ManyToManyField', [], {'default': 'None', 'to': u"orm['enersectapp.SourcePdfToHandle']", 'null': 'True', 'symmetrical': 'False', 'blank': 'True'}),
            'document_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_directory': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'multipart': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
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
        }
    }

    complete_apps = ['enersectapp']