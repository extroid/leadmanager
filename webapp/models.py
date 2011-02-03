from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from postmgr import post_lead, parse_csv_file, get_field_value
from datetime import timedelta
from datetime import datetime 

import settings

class LeadConsumerException(Exception):
    pass    

class LeadField(models.Model):
    "Represents a data field"
    name = models.CharField(max_length=256, null=False, blank=False)
    class Meta:
        verbose_name=_(u'Lead Field')
        verbose_name_plural=_(u'Lead fields')
        
    def __unicode__ (self):
        return u'%s' % (self.name)

class LeadConsumer(models.Model):
    "Receives leads and returns status of the transactions"
    name = models.CharField(max_length=256, null=False, blank=False)
    affiliate_id = models.CharField(max_length=256, null=False, blank=False)
    password = models.CharField(max_length=256, null=False, blank=False)
    url = models.URLField()
    request_type = models.CharField(max_length=256, null=False, blank=False)
    
    def has_lead(self, lead):
        return LeadTransaction.objects.filter(lead=lead, consumer=self, result=u'S').count()>0
    
    def post_lead_callback(self, lead, price, code, message=None, custom_code=None):
        transaction = LeadTransaction(result=code)
        transaction.save()
        transaction.consumer.add(self)
        transaction.lead.add(lead)
        transaction.save()
        if transaction.is_successful():
            if transaction.is_sold():
                transaction.payout = price 
            else:
                transaction.proposed_payout = price
        else:
            transaction.custom_code = custom_code
            transaction.custom_message = message
        transaction.save()    
    def post_lead(self, lead):
        if self.has_lead ( lead ):
            raise LeadConsumerException ( )
        post_lead ( lead, self, self.post_lead_callback )
        return LeadTransaction.objects.filter(lead=lead, consumer=self).order_by('-attempt_datetime')[0]
    def get_diff(self, names):
        for fv in self.required_fileds.all():
            if fv.field.name in names:
                names.remove(fv.field.name)
        return names
    def get_not_grouped_values(self):
        "Values which do not have groups"
        return self.required_fields.filter(groups__isnull=True).all()        
    class Meta:
        verbose_name=_(u'Lead consumer')
        verbose_name_plural=_(u'Lead consumers')
        
    def __unicode__ (self):
        return u'%s' % (self.name)

class LeadFieldValue(models.Model):
    "Represents a data field value"
    METHODS =( ('H','Get through HTTP request'),
               ('X','Get from XSD')
              )
    field = models.ForeignKey(LeadField, related_name='value_entry')
    refval = models.ForeignKey('LeadFieldValue', null=True, blank=True)
    value = models.CharField(max_length=256, null=True, blank=True)
    consumer = models.ForeignKey(LeadConsumer, related_name='required_fileds')
    uri = models.URLField(null=True, blank=True)
    method = models.CharField(max_length=1, choices=METHODS,null=True, blank=True)
    index = models.SmallIntegerField(default=-1,null=True, blank=True)
    attribute = models.BooleanField ( default=False )
    required = models.BooleanField ( default=False )
    ajax = models.BooleanField(default=False)
    
    def get_url(self):
        if not self.refval: return self.uri
        else:
            return self.refval.uri
    class Meta:
        verbose_name=_(u'Lead Field Value')
        verbose_name_plural=_(u'Lead Field Values')
    def get_data(self):
        v = self 
        if self.refval:
            v = self.refval
        if v.index <0:
            return '* Not provided *'
        return self.entries.all()[0].get_data_as_list()[v.index]    
    def __unicode__ (self):
        return u'%s:%s=[%s] by %s' % ( self.consumer.name, self.field.name, self.value, self.get_url())

class LeadFieldGroup(models.Model):
    name = models.CharField(max_length=256 )
    rank = models.SmallIntegerField(default=-1)
    field_values = models.ManyToManyField(LeadFieldValue, related_name='groups', null=False, blank=False)
    refval = models.ForeignKey('LeadFieldGroup', null=True, blank=True)
    consumer = models.ForeignKey(LeadConsumer, related_name='groups') 
    
    class Meta:
        verbose_name=_(u'Lead source')
        verbose_name_plural=_(u'Lead sources')
        
    def create_instance(self):
        _rank = LeadFieldGroup.objects.filter(refval=self).count()-1
        return LeadFieldGroup(name = self.name, rank=_rank, consumer=self.consumer, refval = self)
    def get_value_templates(self):
        self_group = self if self.is_template() else self.refval
        return self.field_values.filter(refval__isnull=True, groups=self_group).all()
    def get_values(self):
        if self.is_template(): return self.get_value_templates() 
        return self.field_values.filter(refval__isnull=False, groups=self).all()    
    def is_template(self):
        return self.refval is None    
    def __unicode__ (self):
        return u'%s' % (self.name)
        
class LeadSource(models.Model):
    "Incoming data source"
    
    name = models.CharField(max_length=256, null=False, blank=False)
    missing_fields = models.ManyToManyField(LeadField, related_name='sources')
    
    def get_missing_field_names(self):
        return [f.name for f in self.missing_fields.all()]
     
    class Meta:
        verbose_name=_(u'Lead source')
        verbose_name_plural=_(u'Lead sources')
        
    def __unicode__ (self):
        return u'%s' % (self.name)
   
class LeadEntry(models.Model):
    "Represents common lead entry"
    date = models.DateField(auto_now_add=True, editable=False)
    first_name = models.CharField(max_length=256, null=False, blank=False)
    last_name = models.CharField(max_length=256, null=False, blank=False)
    city = models.CharField(max_length=256, null=False, blank=False)
    state = models.CharField(max_length=256, null=True, blank=True)
    record = models.TextField()
    required_fields = models.ManyToManyField(LeadFieldValue, related_name='entries', null=True, blank=True)
    field_groups = models.ManyToManyField(LeadFieldGroup, related_name='entries', null=True, blank=True)
    niche = models.ForeignKey('InsuranceTypes', verbose_name=_(u'Niche'))
    source = models.ForeignKey(LeadSource)
    
    def is_sold(self, consumer):
        return self.transactions.filter(result='S', consumer=consumer).count()>0
    def get_payout(self, consumer=None):
        if consumer:
            if not self.is_sold ( consumer ): return 0
            return self.transactions.get(consumer=consumer).payout
        else:
            l = self.transactions.filter(result='S').aggregate(Sum('payout'))
            print l
            if 'payout__sum' in l and l['payout__sum']:
                return l['payout__sum']
            else:
                return 0
    
    def get_moss_required_fields(self):
        MOSS = LeadConsumer.objects.get(name='MOSS')
        
        qset = LeadFieldValue.objects.filter(consumer=MOSS, refval__isnull=True)
        
#        qset = LeadFieldValue.objects.filter(field__sources__in=self.get_file().source.missing_fields.all(), 
#                                             consumer=MOSS, refval__isnull=True)
        fields = []
        class Handler(object):
            def __init__ (self):
                self.options = None
            def set_options(self, data):
                self.options = data
                
        for refFieldValue in qset:
            if self.required_fields.filter(consumer=MOSS, field=refFieldValue.field).count()==0:
                print 'Clone field', refFieldValue
                fieldValue          = LeadFieldValue() 
                fieldValue.refval   = refFieldValue
                fieldValue.field    = refFieldValue.field
                fieldValue.method   = refFieldValue.method
                fieldValue.consumer = refFieldValue.consumer
                
#                fieldValue = LeadFieldValue(consumer=MOSS, field=refFieldValue.field, refval = refFieldValue )
                fieldValue.save()
                self.required_fields.add(fieldValue)
                self.save()
            else:
                fieldValue = self.required_fields.get(consumer=MOSS, field=refFieldValue.field)
            handler = Handler()
            get_field_value ( fieldValue, self, handler.set_options )
            if len(handler.options)==1:
                fieldValue.value=handler.options[0]
                fieldValue.save()
            elif fieldValue.get_data() in handler.options:
                fieldValue.value=fieldValue.get_data()
                fieldValue.save()    
            fields.append({'value':fieldValue, 'options':handler.options})
        return fields    
    def is_required_by_moss(self, field_name):
        fset = LeadField.objects.filter(name=field_name)
        if fset.count()==0: 
            return False
        MOSS = LeadConsumer.objects.get(name='MOSS')
        return self.required_fields.filter(field=fset[0], consumer=MOSS).count()>0
    def get_moss_field_value(self, field_name):
        print 'get field value', field_name
        MOSS = LeadConsumer.objects.get(name='MOSS')
        return self.required_fields.get(field__name=field_name, consumer=MOSS).value    
    def is_moss_complete(self):
        MOSS = LeadConsumer.objects.get(name='MOSS')
        numberOfFields = LeadFieldValue.objects.filter(consumer=MOSS, refval__isnull=True).count()
#        numberOfFields = LeadFieldValue.objects.filter(consumer=MOSS, entries=self, value__isnull=True).count()

#        numberOfFields = self.get_file().source.missing_fields.count()
        qset = self.required_fields.filter(value__isnull=False)
        return numberOfFields-qset.count()==0 
    def is_complete(self):
        return self.is_moss_complete()
    
    def save(self, *args, **kwargs):
        super(LeadEntry, self).save(*args, **kwargs) # Call the "real" save() method.
        
    def get_file(self):
        if self.parent_file.count()==0: return None
        return self.parent_file.all()[0]
    
    def get_price(self, consumer):
        return self.get_payout(consumer)
        
    def get_moss_price(self):
        return self.get_payout(LeadConsumer.objects.get(name="MOSS"))
    def set_data_record(self, data=[]):
        self.record = ';'.join(data)
    def get_data_as_list(self):
        data = self.record.split(u';')
        for field in self.required_fields.all():
            data.append(field.value)
        return data    
    def get_ia_latest_price(self):
        IA = LeadConsumer.objects.get(name="IA")
        q = LeadTransaction.objects.filter(consumer=IA, lead=self, proposed_payout__gt=0).order_by('-attempt_datetime')
        if len(q)>0:
            attempt_time = q[0].attempt_datetime
            diff = datetime.now-timedelta(attempt_time)
            if diff.days>1:
                return 0
            else:
                return q[0].proposed_payout  
        return 0   
            
    def get_ia_price(self):
        return self.get_price ( LeadConsumer.objects.get(name="IA") )
    
    def get_parent_file(self):
        return self.parent_file.all()[0]
    
    class Meta:
        verbose_name=_(u'Lead entry')
        verbose_name_plural=_(u'Lead entries')
        
    def __unicode__ (self):
        return u'%s %s | %s | %s' % (self.first_name, self.last_name, self.city, self.state)  
        
class LeadTransaction(models.Model):
    "Represents lead entry transaction posted onto given lead consumer. Keeps result"
    OPCODES =( ('S','Sold'),
               ('P','Got offer'),
               ('D','Access Denied'),
               ('F','Transaction Failure'),
               ('E','System Error')
              )
    attempt_datetime = models.DateTimeField(auto_now_add=True, editable=False)
    lead = models.ManyToManyField(LeadEntry, related_name='transactions', editable=False)
    consumer = models.ManyToManyField(LeadConsumer, related_name='transactions', editable=False)
    result = models.CharField(max_length=1, choices=OPCODES, editable=False)
    payout = models.FloatField(default=0)
    proposed_payout= models.FloatField(default=0)
    custom_code = models.CharField(max_length=255, null=True, blank=True, editable=False)
    custom_message = models.CharField(max_length=255, null=True, blank=True, editable=False)
    
    class Meta:
        verbose_name=_(u'Lead transaction')
        verbose_name_plural=_(u'Leads transactions')
        
    def is_successful(self):
        return self.result=='S' or self.result=='P'
    def is_sold(self):
        return self.result=='S'
    
    def __unicode__ (self):
        s = u'%s %s -> %s [%s] ' % (self.attempt_datetime.strftime('%c'), self.lead.all()[0], self.consumer.all()[0].name, self.get_result_display())
        if not self.is_successful():
            s+= '(%s: %s)' % (self.custom_code, self.custom_message)
        elif self.is_sold():
            s+'(payout %s)' % self.payout
        else:
            s+'(payout %s)' % self.proposed_payout
        return s
    
class InsuranceTypes ( models.Model ):
    name = models.CharField (max_length=256, null=False, blank=False)
    short_name = models.CharField(max_length=256, null=False, blank=False)
    
    class Meta:
        verbose_name=_(u'Insurance Types')
        verbose_name_plural=_(u'Insurance Types')
        
    def __unicode__ (self):
        return u'%s' % (self.name)
    
class LeadFile(models.Model):
    "Represents common lead CSV file to be uploaded and parsed. Contains Lead entries"
    lead_file = models.FileField ( upload_to=settings.LEAD_FILE_DIR, help_text='Make sure your CSV file has Excel format (fields are separated with a <tt>comma</tt>)' )
    upload_date = models.DateTimeField(auto_now_add=True, editable=False)
    entries = models.ManyToManyField(LeadEntry, related_name='parent_file', null=True)
    insurance_type = models.ForeignKey(InsuranceTypes, verbose_name=_(u'Niche'))
    cost = models.FloatField(default=0)
    source = models.ForeignKey(LeadSource, related_name='file', default=1)
    header = models.TextField(null=True, blank=True)
    has_header = models.BooleanField (default=1)
    
    class Meta:
        verbose_name=_(u'Lead file')
        verbose_name_plural=_(u'Lead files')
    def get_total_revenue(self):
        return LeadTransaction.objects.all().aggregate(Sum('payout'))['payout__sum']
    def get_total_cost(self):
        return LeadFile.objects.all().aggregate(Sum('cost'))['cost__sum']
    def get_revenue(self):
        return self.entries.all().aggregate(Sum('transactions__payout'))['transactions__payout__sum']
    def get_moss_revenue(self):
        return self.entries.filter(transactions__consumer__name='MOSS').aggregate(Sum('transactions__payout'))['transactions__payout__sum']
    
    def get_header_labels(self):
        if not self.has_header: return []
        return self.header.split(';')     
    def handle_lead_entry(self, row, header, firstName, lastName, city, state):
        if header and self.has_header:
            self.header = u';'.join(row)
            self.save()
            return
        
        entry = LeadEntry( 
                           first_name=firstName, 
                           last_name=lastName,
                           city=city,
                           state=state, 
                           record=u';'.join(row),
                           source = self.source,
                           niche = self.insurance_type
                          )
        entry.save()
        self.entries.add(entry)
        self.save()
        entry.get_moss_required_fields()
    def get_niche(self):
        return self.insurance_type.name
    def get_filename(self):
        fullname =  self.lead_file.file.name
        return fullname[fullname.rfind('/')+1:]    
    def parse_lead(self):
        parse_csv_file( str(self.lead_file.file), self.handle_lead_entry)
        
    def __unicode__ (self):
        return u'%s-%s' % (self.lead_file, self.upload_date)
    
    
