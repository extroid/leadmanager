from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import Sum

from postmgr import post_lead, parse_csv_file, get_field_value
from msa_plugin.msafactory import validate_lead
from datetime import timedelta
from datetime import datetime 

import settings

class LeadConsumerException(Exception):
    pass    

class ValueHandler(object):
    def __init__ (self):
        self.options = None
    def set_options(self, data):
        self.options = data
        
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
        for fv in self.get_metagroup().get_values():
            if fv.field.name in names:
                names.remove(fv.field.name)
        return names
    def get_metagroup(self):
        return self.meta_group.all()[0]        
    class Meta:
        verbose_name=_(u'Lead consumer')
        verbose_name_plural=_(u'Lead consumers')
        
    def __unicode__ (self):
        return u'%s' % (self.name)

class LeadFieldValue(models.Model):
    "Represents a data field value"
    METHODS =( ('H','Get through HTTP request'),
               ('X','Get from XSD'),
               ('R','Get from record'),
               ('V','Get/Set as value'),
              )
    field = models.ForeignKey(LeadField, related_name='value_entry')
    refval = models.ForeignKey('LeadFieldValue', null=True, blank=True)
    value = models.CharField(max_length=256, null=True, blank=True)
    consumer = models.ForeignKey(LeadConsumer, related_name='values')
    uri = models.URLField(null=True, blank=True)
    method = models.CharField(max_length=1, choices=METHODS,null=True, blank=True)
    index = models.SmallIntegerField(default=-1,null=True, blank=True)
    attribute = models.BooleanField ( default=False )
    required = models.BooleanField ( default=True )
    ajax = models.BooleanField(default=False)
    partof = models.CharField(max_length=256, null=True, blank=True)
    partseq = models.SmallIntegerField(default=0)
    
    def __init__ (self, *args, **kwargs):
        super(LeadFieldValue,self).__init__(*args,**kwargs)
        self.options = None
    
    def get_url(self):
        return self.uri if self.refval is None else self.refval.uri
    
    class Meta:
        verbose_name=_(u'Lead Field Value')
        verbose_name_plural=_(u'Lead Field Values')
        
    def is_template(self):
        return self.refval is None
    def get_template(self):
        return self.refval
    def create_instance(self):
        self_val = self if self.is_template() else self.refval
        fv = LeadFieldValue(field = self_val.field, 
                       method=self_val.method,
                       uri=self_val.uri,
                       attribute = self_val.attribute,
                       required = self_val.required,
                       consumer=self_val.consumer, 
                       ajax = self_val.ajax,
                       index = self_val.index,
                       refval = self_val,
                       partof = self_val.partof,
                       partseq = self_val.partseq )  
        fv.save()
        return fv
    def is_input(self):
        return self.method in ('V','R') 
    def get_next_field(self):
        qset = self.groups.all()[0].data_values.filter(partseq=self.partseq+1)
        if qset.count()==0:
            return None
        return qset[0]
    def get_parts(self):
        if not self.partof: return None
        return [p for p in self.groups.all()[0].data_values.filter(partof=self.partof).order_by('partseq').all()]
    def is_dropdown(self):
        return self.method not in ('V','R')
    def get_options(self):
        if self.is_input(): return None
        handler = ValueHandler()
        def on_error_stop_waiting(msg):
            return True
        get_field_value ( self, self.groups.all()[0], handler.set_options, on_error_stop_waiting )
        
        return handler.options if handler.options else []
    def get_data(self):
        if self.method=='R':
            if self.index <0:
                return '* Not provided *'
            return self.entries.all()[0].get_data_as_list()[self.index]
        else:
            return self.value
            
    def __unicode__ (self):
        return u'%s:%s=[%s] by %s' % ( self.consumer.name, self.field.name, self.value, self.get_url())

class LeadFieldGroup(models.Model):
    name = models.CharField(max_length=256 )
    data_values = models.ManyToManyField(LeadFieldValue, related_name='groups', null=True)
    refval = models.ForeignKey('LeadFieldGroup', null=True, blank=True)
    consumer = models.ForeignKey(LeadConsumer, related_name='meta_group')
    parent = models.ForeignKey('LeadFieldGroup', related_name='children', null=True)
    onlyone = models.BooleanField(default=False) 
    class Meta:
        verbose_name=_(u'Lead field group')
        verbose_name_plural=_(u'Lead field groups')
        
    def create_instance(self):
        "Creates another sibling of self type"
        self_group = self if self.is_template() else self.refval 
        g = LeadFieldGroup(name = self_group.name, 
                           consumer=self_group.consumer, 
                           refval = self_group, 
                           onlyone = self_group.onlyone)
        g.save()
        g.create_data()
        return g
    def create_data(self):
        for fv in self.get_value_templates():
            self.data_values.add(fv.create_instance())
        self.save()
    def create_instance_tree(self):
        "Creates another sibling and all its children. Returns new instance"
        self_new=self.create_instance()
        self_new.parent = self.parent
        self_new.save()
        self.create_tree(self_new)
        return self_new
    def create_tree(self, instance):
        for group_tpl in instance.get_subgroups():
            subinstance = group_tpl.create_instance()
            subinstance.parent=instance
            subinstance.save()
            group_tpl.create_tree ( subinstance )
        return instance      
    
    def delete_instance_tree(self):
        if self.is_template(): return 
        for value in self.get_values():
            value.delete()    
        for child in self.children.all():
            child.delete_instance_tree()
        self.delete()    
        
    def visit_instance_tree(self, value_visitor, node_visitor=None, node_order=None):
        if self.is_template(): return 
        if node_visitor:
                node_visitor(self)
        for value in self.get_values():
            value_visitor ( self, value )    
        if not node_order:    
            for child in self.children.all():
                child.visit_instance_tree ( value_visitor, node_visitor )
        else:
            for child in self.children.order_by(*node_order):
                child.visit_instance_tree ( value_visitor, node_visitor )        
            
    def get_subgroups(self):
        "Gets group template objects"
        self_group = self if self.is_template() else self.refval
        return self_group.children.all()
    
    def get_subgroup_instances(self, group_name):
        "Gets group instances of given group by its name"
        if self.children is None or self.children.filter(name=group_name).count()==0:
            return None  
        else: 
            return self.children.filter(name=group_name).all()
        
    def get_instances(self):
        self_group = self if self.is_template() else self.refval
        return LeadFieldGroup.objects.filter(parent=self.parent, refval = self_group).all()
    def get_value_templates(self):
        self_group = self if self.is_template() else self.refval
        return self_group.data_values.filter(refval__isnull=True).order_by('-partof','partseq').all()
    def get_values(self):
        if self.is_template(): return self.get_value_templates() 
        return self.data_values.filter(refval__isnull=False, groups=self).order_by('-partof','partseq').all()
    def set_value_data(self, field_name, data):
        if self.is_template(): return None 
        fv = self.data_values.get(refval__isnull=False, groups=self, field__name=field_name)
        fv.value = data
        fv.save() 
    def get_value_data(self, field_name):  
        qset = self.data_values.filter(refval__isnull=False, groups=self, field__name=field_name)
        return None if len(qset) ==0 else qset[0].value  
    def get_field_value(self,field_name):
        return self.get_value_data(field_name)
    def is_template(self):
        return self.refval is None
    def check_required_complete(self):
        for reqfld in self.data_values.filter(required=True):
            if reqfld.value is None:
                return False  
    def is_complete(self, find_root=True):
        if self.is_template(): return True
        root = self
        if self.parent and find_root:
            while root.parent:
                root = root.parent
        if not root.check_required_complete(): return False
        for child in root.children.all():
            if not child.is_complete(False):
                return False
        return True
    def get_lead(self):
        root = self
        while root.parent: 
            root = root.parent
        return root.entries.all()[0]
    def get_level(self):    
        level = 0
        root = self
        while root.parent: 
            root = root.parent
            level+=1
        return level
    def get_ident(self):
        if self.get_level()==0: return 0
        return self.get_level()-1    
    def print_template_tree(self, grp = None, ident=1):
        if grp is None:
            grp = self
            print '%s (%s)' %(self.name,len(self.get_instances())) 
        s = ' '*ident    
        for sub in grp.get_subgroups():
            print '%s (%s)' %(s+sub.name,len(grp.get_instances()))
            sub.print_template_tree(sub, ident+1)
        print s       
    def get_flat_structure(self):
        flat_data = [] 
        val_flat = lambda x,y: x and y
        def flatter(group):
            print '*** ',group.name
            title = group.name
            if group.get_level()==1 and not group.onlyone:
                title+=' %d' % group.get_index()
            flat_data.append((group, title))
        for child in self.children.order_by('name'):
            if child.is_template(): continue 
            print 'flatting tree ', child.name   
            child.visit_instance_tree(val_flat,flatter)
        return flat_data    
    def get_index(self):
        if self.is_template(): return -1
        if not self.parent: return 0
        children = [grp for grp in self.parent.children.filter(name=self.name)]
        return children.index(self)+1
         
    def __unicode__ (self):
        return u'%s' % (self.name)
        
class LeadSource(models.Model):
    "Incoming data source"
    
    name = models.CharField(max_length=256, null=False, blank=False)
     
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
    data_groups = models.ManyToManyField(LeadFieldGroup, related_name='entries', null=True, blank=True)
    niche = models.ForeignKey('InsuranceTypes', verbose_name=_(u'Niche'))
    source = models.ForeignKey(LeadSource)
    
    def is_sold(self, consumer):
        return self.transactions.filter(result='S', consumer=consumer).count()>0
    def get_payout(self, consumer=None):
        if consumer:
            if not self.is_sold ( consumer ): return 0
            return self.transactions.get(consumer=consumer, payout__gt=0).payout
        else:
            l = self.transactions.filter(result='S').aggregate(Sum('payout'))
            if 'payout__sum' in l and l['payout__sum']:
                return l['payout__sum']
            else:
                return 0
    def get_moss_data(self):
        MOSS = LeadConsumer.objects.get(name='MOSS')
        if self.data_groups.filter(consumer=MOSS).count()==0: return None
        return self.data_groups.get(consumer=MOSS)
    
    def create_or_get_moss_data (self):
        if self.get_moss_data(): return self.get_moss_data() 
        MOSS = LeadConsumer.objects.get(name='MOSS')
        
        moss_data = MOSS.get_metagroup().create_instance_tree()
        self.data_groups.add(moss_data)
        return moss_data
    def delete_moss_data(self):
        moss_data = self.get_moss_data()
        if moss_data:
            moss_data.delete_instance_tree()
            
    def delete_lead(self):
        self.delete_moss_data()        
        self.delete ( )
        
    def option_collector(self, group, fieldValue):  
        if fieldValue.is_input(): return         
        
        get_field_value ( fieldValue, group, fieldValue.set_options )
        if fieldValue.options and len(fieldValue.options)==1:
            fieldValue.value=fieldValue.options[0]
            fieldValue.save()
        elif fieldValue.options and fieldValue.get_data() in fieldValue.options:
            fieldValue.value=fieldValue.get_data()
            fieldValue.save()    
#            fieldValue.set_options(handler.options)
        print fieldValue.options                
    def get_moss_value_options(self, option_collector):
        moss_data = self.create_or_get_moss_data()
        moss_data.visit_instance_tree ( option_collector )    
        return moss_data    
    
    def get_moss_field_value(self, field_name, group='Lead'):
        print 'get field value', field_name
        MOSS = LeadConsumer.objects.get(name='MOSS')
        return LeadFieldValue.get(field__name=field_name, consumer=MOSS, groups=group).value    
    
    def is_moss_complete(self):
        try:
            validate_lead ( self )
            return True
        except:
            return False
#        return self.get_moss_data().is_complete()

    def is_complete(self):
        return self.is_moss_complete()
    
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
        entry.get_moss_value_options()
    def get_niche(self):
        return self.insurance_type.name
    def get_filename(self):
        fullname =  self.lead_file.file.name
        return fullname[fullname.rfind('/')+1:]    
    def parse_lead(self):
        parse_csv_file( str(self.lead_file.file), self.handle_lead_entry)
        
    def __unicode__ (self):
        return u'%s-%s' % (self.lead_file, self.upload_date)
    
    
