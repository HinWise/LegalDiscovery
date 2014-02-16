# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ExtractionFieldTemplate'
        db.create_table(u'enersectapp_extractionfieldtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='unnamed', max_length=127)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(default='Unnamed', max_length=127)),
            ('real_field_name', self.gf('django.db.models.fields.CharField')(default='Blank', max_length=127)),
            ('importance', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('checked', self.gf('django.db.models.fields.CharField')(default='checked', max_length=31)),
            ('field_sorting', self.gf('django.db.models.fields.CharField')(default='default', max_length=31)),
            ('general_sorting', self.gf('django.db.models.fields.CharField')(default='modification_date', max_length=31)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 16, 0, 0))),
            ('creation_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'enersectapp', ['ExtractionFieldTemplate'])

        # Adding model 'SourceDocTypeTemplate'
        db.create_table(u'enersectapp_sourcedoctypetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='uncategorized', max_length=255)),
            ('pretty_name', self.gf('django.db.models.fields.CharField')(default='Uncategorized', max_length=255)),
            ('min_show', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('max_show', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('min_selected', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('max_selected', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('checked', self.gf('django.db.models.fields.CharField')(default='checked', max_length=31)),
            ('general_sorting', self.gf('django.db.models.fields.CharField')(default='modification_date', max_length=31)),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 16, 0, 0))),
            ('creation_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'enersectapp', ['SourceDocTypeTemplate'])

        # Adding M2M table for field extraction_fields on 'SourceDocTypeTemplate'
        m2m_table_name = db.shorten_name(u'enersectapp_sourcedoctypetemplate_extraction_fields')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('sourcedoctypetemplate', models.ForeignKey(orm[u'enersectapp.sourcedoctypetemplate'], null=False)),
            ('extractionfieldtemplate', models.ForeignKey(orm[u'enersectapp.extractionfieldtemplate'], null=False))
        ))
        db.create_unique(m2m_table_name, ['sourcedoctypetemplate_id', 'extractionfieldtemplate_id'])

        # Adding model 'LegalDiscoveryTemplate'
        db.create_table(u'enersectapp_legaldiscoverytemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Saved Template ', max_length=127)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 16, 0, 0))),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 16, 0, 0))),
            ('creation_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'enersectapp', ['LegalDiscoveryTemplate'])

        # Adding M2M table for field sourcedoctypes_list on 'LegalDiscoveryTemplate'
        m2m_table_name = db.shorten_name(u'enersectapp_legaldiscoverytemplate_sourcedoctypes_list')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('legaldiscoverytemplate', models.ForeignKey(orm[u'enersectapp.legaldiscoverytemplate'], null=False)),
            ('sourcedoctypetemplate', models.ForeignKey(orm[u'enersectapp.sourcedoctypetemplate'], null=False))
        ))
        db.create_unique(m2m_table_name, ['legaldiscoverytemplate_id', 'sourcedoctypetemplate_id'])

        # Adding M2M table for field created_legaldiscovery_templates on 'UserProfile'
        m2m_table_name = db.shorten_name(u'enersectapp_userprofile_created_legaldiscovery_templates')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'enersectapp.userprofile'], null=False)),
            ('legaldiscoverytemplate', models.ForeignKey(orm[u'enersectapp.legaldiscoverytemplate'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'legaldiscoverytemplate_id'])

        # Adding field 'ExtractionField.real_field_name'
        db.add_column(u'enersectapp_extractionfield', 'real_field_name',
                      self.gf('django.db.models.fields.CharField')(default='Blank', max_length=127),
                      keep_default=False)

        # Adding field 'ExtractionField.checked'
        db.add_column(u'enersectapp_extractionfield', 'checked',
                      self.gf('django.db.models.fields.CharField')(default='checked', max_length=31),
                      keep_default=False)

        # Adding field 'ExtractionField.field_sorting'
        db.add_column(u'enersectapp_extractionfield', 'field_sorting',
                      self.gf('django.db.models.fields.CharField')(default='default', max_length=31),
                      keep_default=False)

        # Adding field 'ExtractionField.general_sorting'
        db.add_column(u'enersectapp_extractionfield', 'general_sorting',
                      self.gf('django.db.models.fields.CharField')(default='importance', max_length=31),
                      keep_default=False)

        # Adding field 'SourceDocType.min_show'
        db.add_column(u'enersectapp_sourcedoctype', 'min_show',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'SourceDocType.max_show'
        db.add_column(u'enersectapp_sourcedoctype', 'max_show',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'SourceDocType.min_selected'
        db.add_column(u'enersectapp_sourcedoctype', 'min_selected',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'SourceDocType.max_selected'
        db.add_column(u'enersectapp_sourcedoctype', 'max_selected',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'SourceDocType.checked'
        db.add_column(u'enersectapp_sourcedoctype', 'checked',
                      self.gf('django.db.models.fields.CharField')(default='checked', max_length=31),
                      keep_default=False)

        # Adding field 'SourceDocType.general_sorting'
        db.add_column(u'enersectapp_sourcedoctype', 'general_sorting',
                      self.gf('django.db.models.fields.CharField')(default='count', max_length=31),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ExtractionFieldTemplate'
        db.delete_table(u'enersectapp_extractionfieldtemplate')

        # Deleting model 'SourceDocTypeTemplate'
        db.delete_table(u'enersectapp_sourcedoctypetemplate')

        # Removing M2M table for field extraction_fields on 'SourceDocTypeTemplate'
        db.delete_table(db.shorten_name(u'enersectapp_sourcedoctypetemplate_extraction_fields'))

        # Deleting model 'LegalDiscoveryTemplate'
        db.delete_table(u'enersectapp_legaldiscoverytemplate')

        # Removing M2M table for field sourcedoctypes_list on 'LegalDiscoveryTemplate'
        db.delete_table(db.shorten_name(u'enersectapp_legaldiscoverytemplate_sourcedoctypes_list'))

        # Removing M2M table for field created_legaldiscovery_templates on 'UserProfile'
        db.delete_table(db.shorten_name(u'enersectapp_userprofile_created_legaldiscovery_templates'))

        # Deleting field 'ExtractionField.real_field_name'
        db.delete_column(u'enersectapp_extractionfield', 'real_field_name')

        # Deleting field 'ExtractionField.checked'
        db.delete_column(u'enersectapp_extractionfield', 'checked')

        # Deleting field 'ExtractionField.field_sorting'
        db.delete_column(u'enersectapp_extractionfield', 'field_sorting')

        # Deleting field 'ExtractionField.general_sorting'
        db.delete_column(u'enersectapp_extractionfield', 'general_sorting')

        # Deleting field 'SourceDocType.min_show'
        db.delete_column(u'enersectapp_sourcedoctype', 'min_show')

        # Deleting field 'SourceDocType.max_show'
        db.delete_column(u'enersectapp_sourcedoctype', 'max_show')

        # Deleting field 'SourceDocType.min_selected'
        db.delete_column(u'enersectapp_sourcedoctype', 'min_selected')

        # Deleting field 'SourceDocType.max_selected'
        db.delete_column(u'enersectapp_sourcedoctype', 'max_selected')

        # Deleting field 'SourceDocType.checked'
        db.delete_column(u'enersectapp_sourcedoctype', 'checked')

        # Deleting field 'SourceDocType.general_sorting'
        db.delete_column(u'enersectapp_sourcedoctype', 'general_sorting')


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
        u'enersectapp.extractionfield': {
            'Meta': {'ordering': "['name']", 'object_name': 'ExtractionField'},
            'checked': ('django.db.models.fields.CharField', [], {'default': "'checked'", 'max_length': '31'}),
            'field_sorting': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '31'}),
            'general_sorting': ('django.db.models.fields.CharField', [], {'default': "'importance'", 'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'unnamed'", 'max_length': '127'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed'", 'max_length': '127'}),
            'real_field_name': ('django.db.models.fields.CharField', [], {'default': "'Blank'", 'max_length': '127'})
        },
        u'enersectapp.extractionfieldtemplate': {
            'Meta': {'ordering': "['modification_date']", 'object_name': 'ExtractionFieldTemplate'},
            'checked': ('django.db.models.fields.CharField', [], {'default': "'checked'", 'max_length': '31'}),
            'creation_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'field_sorting': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '31'}),
            'general_sorting': ('django.db.models.fields.CharField', [], {'default': "'modification_date'", 'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'unnamed'", 'max_length': '127'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'default': "'Unnamed'", 'max_length': '127'}),
            'real_field_name': ('django.db.models.fields.CharField', [], {'default': "'Blank'", 'max_length': '127'})
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
        u'enersectapp.legaldiscoverytemplate': {
            'Meta': {'ordering': "['creation_date']", 'object_name': 'LegalDiscoveryTemplate'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'creation_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Saved Template '", 'max_length': '127'}),
            'sourcedoctypes_list': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'source doc template list'", 'default': 'None', 'to': u"orm['enersectapp.SourceDocTypeTemplate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'})
        },
        u'enersectapp.ocrrecord': {
            'Address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Amount': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Blank': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'Cheque_Number': ('django.db.models.fields.CharField', [], {'default': "'NoChequeNumberField'", 'max_length': '255'}),
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
            'audit_mark_revision': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'audit_mark_saved': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'commentary': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '512'}),
            'companytemplate_link': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['enersectapp.CompanyTemplate']"}),
            'createdbymean': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '255'}),
            'datetime_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'error_style_class': ('django.db.models.fields.CharField', [], {'default': "'noerror'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linked_style_class': ('django.db.models.fields.CharField', [], {'default': "'nolink'", 'max_length': '255'}),
            'modification_author': ('django.db.models.fields.CharField', [], {'default': "'Xanto'", 'max_length': '255'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'modified_doctype_author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'modified_doctype_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
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
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '300'}),
            'skip_counter': ('django.db.models.fields.CharField', [], {'default': "'0'", 'max_length': '10'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unlinked'", 'max_length': '100'})
        },
        u'enersectapp.report': {
            'Meta': {'object_name': 'Report'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report_author': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'report_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']"}),
            'report_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
            'report_memo': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'report_subtype': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '31'}),
            'report_type': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '31'}),
            'report_viewed': ('django.db.models.fields.CharField', [], {'default': "'No'", 'max_length': '7'})
        },
        u'enersectapp.sourcedoctype': {
            'Meta': {'ordering': "['name']", 'object_name': 'SourceDocType'},
            'checked': ('django.db.models.fields.CharField', [], {'default': "'checked'", 'max_length': '31'}),
            'extraction_fields': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'extraction fields list'", 'default': 'None', 'to': u"orm['enersectapp.ExtractionField']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'general_sorting': ('django.db.models.fields.CharField', [], {'default': "'count'", 'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_selected': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'max_show': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'min_selected': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'min_show': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'uncategorized'", 'max_length': '255'}),
            'pretty_name': ('django.db.models.fields.CharField', [], {'default': "'Uncategorized'", 'max_length': '255'})
        },
        u'enersectapp.sourcedoctypetemplate': {
            'Meta': {'ordering': "['modification_date']", 'object_name': 'SourceDocTypeTemplate'},
            'checked': ('django.db.models.fields.CharField', [], {'default': "'checked'", 'max_length': '31'}),
            'creation_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'extraction_fields': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'extraction fields list'", 'default': 'None', 'to': u"orm['enersectapp.ExtractionFieldTemplate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'general_sorting': ('django.db.models.fields.CharField', [], {'default': "'modification_date'", 'max_length': '31'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_selected': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'max_show': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'min_selected': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'min_show': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
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
            'modification_doctype_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 16, 0, 0)'}),
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
            'created_legaldiscovery_templates': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'legaldiscovery_templates'", 'default': 'None', 'to': u"orm['enersectapp.LegalDiscoveryTemplate']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modifiedpdfs_audit_marked': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_audit_marked'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedpdfs_audit_revision': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_audit_revisioned'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedpdfs_audit_saved': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_audit_saved'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedpdfs_categorization_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_modified_categorization_tool'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedpdfs_translated_arabic': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'pdfs_translated_arabic'", 'default': 'None', 'to': u"orm['enersectapp.PdfRecord']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedsourcepdfs_blank_or_not_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sourcepdfs_modified_blank_or_not_blank_tool'", 'default': 'None', 'to': u"orm['enersectapp.SourcePdf']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'modifiedsourcepdfs_categorization_tool': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'sourcepdfs_modified_categorization_tool'", 'default': 'None', 'to': u"orm['enersectapp.SourcePdf']", 'blank': 'True', 'symmetrical': 'False', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'user_company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.Group']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['enersectapp']