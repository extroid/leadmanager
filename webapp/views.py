from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from forms import LeadFileForm, LeadEntryForm

from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.utils import simplejson
from django.db.models import Sum

from datetime import date

from models import LeadFile, LeadConsumer, LeadEntry, LeadFieldValue, LeadTransaction, LeadFieldGroup
from models import ValueHandler
from msa_plugin.msafactory import csvMap, validate_lead as moss_validate_lead, get_required_field_value
from lxml.etree import XMLSyntaxError

class Value:
    def __init__ (self, key,val):
        self.title = key
        self.value = val
    def __str__ (self):
        return self.title

@csrf_protect
def index(request):
    if LeadEntry.objects.count()==0:
        return HttpResponseRedirect("/lead/moss/new_lead")
    class DayEntry(object):
        def __init__ (self, date):
            self.date = date
            self.niche = None
            self.source = None
            self.leads = 0
            self.revenue = 0
    leads_by_day = {}
    ld = [] 
    revenue = 0 
    nleads = LeadEntry.objects.count()
    for entry in LeadEntry.objects.order_by('-date','niche','source'):
        key = '%s_%s_%s' % (entry.date,entry.niche,entry.source )
        print key
        if  key not in leads_by_day:
            leads_by_day[key]=DayEntry(entry.date)
            leads_by_day[key].niche = entry.niche
            leads_by_day[key].source = entry.source
        if len(ld)==0 or ld[-1]!=leads_by_day[key]:
            ld.append(leads_by_day[key])    
        leads_by_day[key].leads += 1
        lead_rev = entry.get_payout()
        leads_by_day[key].revenue += lead_rev
        revenue += lead_rev
        
    return render_to_response('leadmanager.html', 
                              {'leads_by_day':ld, 'revenue': revenue,'nleads':nleads},
                              context_instance=RequestContext(request)
             
                              )
@csrf_protect        
def delete_lead(request):
    if request.method=='POST':
        lead_id = int(request.POST['lead_id'])
        lead = get_object_or_404(LeadEntry,pk=lead_id)
        for t in lead.transactions.all():
            t.delete()
        lead.delete()    
        return HttpResponseRedirect('/')

def set_value_options(values, group):
    q = []
    for fieldValue in values:
        if fieldValue.is_input():
            q.append((fieldValue, None)) 
            continue         
        handler = ValueHandler()
        get_required_field_value ( fieldValue, group, handler.set_options )
        q.append((fieldValue, handler.options))
    return q    
def get_options(request):
    if request.POST:
        fvid = int(request.POST['fieldvalue_id'])
        print 'fvid', fvid
        fieldValue = LeadFieldValue.objects.get(pk=fvid)
        print fieldValue
        options = {}
        fopt = fieldValue.get_options()
        print fopt
        for opt in fopt:
            options["%s_%s" % (fvid, opt)]=opt
        data={'code':'OK','options':options}  
        return HttpResponse(simplejson.dumps(data),mimetype='application/json')      
@csrf_protect    
def new_lead(request, consumer_name):
    lead = None
    if consumer_name=='moss':
        consumer = get_object_or_404(LeadConsumer, name='MOSS')
        
        titles = consumer.get_metagroup().get_value_templates()
        if request.method=='GET':
            return render_to_response('mossform.html', 
                                  {'titles': titles, 'lead':lead, 'form':LeadEntryForm()},
                                    context_instance=RequestContext(request)
                                  )
        elif request.method=='POST':
            lead = None
            
            leadForm = LeadEntryForm ( request.POST )
            if not leadForm.is_valid():
                return render_to_response('mossform.html', 
                                  {'titles': titles, 'lead':lead, 'form':leadForm},
                                    context_instance=RequestContext(request)
                                  )
            if 'lead_id' in request.POST:
                lead = get_object_or_404 ( LeadEntry, pk=int(request.POST['lead_id']) )
            else:
                lead = LeadEntry( )
                
            lead.source = leadForm.cleaned_data['source']
            lead.niche = leadForm.cleaned_data['niche'] 
                
            try:    
                if 'lead_id' not in request.POST:
                    lead.first_name = request.POST['First Name']            
                    lead.last_name = request.POST['Last Name']
                    lead.state = request.POST['State']
                    lead.city = request.POST['City']
                    lead.save()
                    
                    moss_data = lead.create_or_get_moss_data()
                    for fieldValue in moss_data.get_values():
                        moss_data.set_value_data(fieldValue.field.name,request.POST[fieldValue.field.name]) 
                    return render_to_response('mossform.html', 
                                  {'titles': moss_data.get_values(), 'rootgroup':moss_data, 'lead':lead, 'form':leadForm},
                                  context_instance=RequestContext(request)
                                  )
                else:
                    try:
                        moss_validate_lead ( lead )
                        return HttpResponseRedirect('/lead/moss/new_lead')
                    except XMLSyntaxError, msg:
                        return render_to_response('mossform.html', 
                              {'titles': lead.get_moss_data().get_values(), 
                               'rootgroup':lead.get_moss_data(), 
                               'lead':lead, 
                               'error':msg,
                               'form':leadForm
                               },
                              context_instance=RequestContext(request)
                              )         
            except KeyError, e:
                return render_to_response('mossform.html', 
                              {'titles': moss_data.get_values(), 'error':e,'form':leadForm},
                              context_instance=RequestContext(request)
                              )    
                
def new_group(request):
    if request.POST:
        refgroup = int(request.POST['refgrp'])
        group_template = get_object_or_404(LeadFieldGroup, pk=refgroup);
        newgrp = group_template.create_instance_tree()
        newgrp.parent = group_template.parent
        newgrp.save()
        if len(newgrp.get_subgroups())==0:
            print 'responding a group'
            return render_to_response('group_instance.html', {'group': newgrp, 'new_instance':True})
        else:
            print 'responding a rootgroup'
            return render_to_response('group_tree.html', {'rootgroup': newgrp, 'add_to_tree':True, 'new_instance':True})
@csrf_protect
def show_leadsperday(request, qdate):
    try:
        da = map(int,qdate.split('-'))
        d = date(*da)
        leads = LeadEntry.objects.filter(date=d)
        day_total = LeadTransaction.objects.filter(lead__date=d, result='S').aggregate(Sum('payout'))['payout__sum']
        return render_to_response('leadsperday_table.html', 
                                  {'date':d,
                                   'leads':leads, 
                                   'day_total':day_total},
                                   context_instance=RequestContext(request), 
                                   mimetype='text/html')
    except LeadEntry.DoesNotExist, e:
        print e
                    
def show_leadfile(request, leadfileno):
    try:
        leadFile = LeadFile.objects.get(pk=leadfileno)
        return render_to_response('leadfile_table.html', {'lead_file':leadFile}, mimetype='text/html')
    except LeadFile.DoesNotExist:
        print 'LeadFile pk=%s does not exists' % leadfileno
        
@csrf_protect
def show_lead(request, leadno):
    try:
        lead = LeadEntry.objects.get(pk=leadno)
        return render_to_response('lead_table.html', 
                                  {'lead':lead, 
                                   'titles':lead.get_moss_data().get_values(), 
                                   'rootgroup':lead.get_moss_data()
                                   }, 
                                   context_instance=RequestContext(request))
    except LeadEntry.DoesNotExist:
        print 'LeadEntry pk=%s does not exists' % leadno
def save_field_value(request):
    if request.POST:
        try:
            field_id = int(request.POST['field_id'])
            field_value = request.POST['value']
            lfv = get_object_or_404(LeadFieldValue, pk=field_id)
            lfv.value = field_value 
            lfv.save()
            data={'code':'OK', 'entry_id':lfv.groups.all()[0].get_lead().id, 'is_complete':lfv.groups.all()[0].is_complete()}
            return HttpResponse(simplejson.dumps(data),mimetype='application/json')
        except Exception, msg:
            data={'code':'NOK','message':msg}
            return HttpResponse(simplejson.dumps(data),mimetype='application/json')
def save_csv_field_value(request):
    if request.POST:
        try:
            lead_id = int(request.POST['lead_id'])
            field_name = request.POST['name']
            field_value = request.POST['value']
            lead = get_object_or_404(LeadEntry, pk=lead_id)
            data = lead.get_data_as_list()
            data[csvMap[field_name]] = field_value
            lead.set_data_record(data)
            lead.save()
            
            data={'code':'OK', 'field_name':field_name,'lead_id':lead.id, 'is_complete':lead.is_complete()}
            return HttpResponse(simplejson.dumps(data),mimetype='application/json')
        except Exception, msg:
            data={'code':'NOK','message':msg}
            return HttpResponse(simplejson.dumps(data),mimetype='application/json')
        
def save_required_field_value(request,consumer_name):
    if request.POST:
        if consumer_name=='moss':
            try:
                fid = int(request.POST['field'])
                lfv = get_object_or_404(LeadFieldValue, id=fid)
                lfv.value=request.POST['value']
                lfv.save()
                data={'code':'OK', 'entry_id':lfv.groups.all()[0].get_lead().id, 'is_complete':lfv.groups.all()[0].is_complete()}
                parts = lfv.get_parts()
                if parts and len(parts)>0:
                    next = lfv.get_next_field()
                    print 'next field', next
                    if next:
                        print 'Parts',parts
                        parts = [p for p in parts[parts.index(next):]]
                        for p in parts:
                            p.value = None
                            p.save()
                        print 'Parts ID',parts
                        parts = [p.id for p in parts] 
                        options = {}
                        fopt = next.get_options()
                        for opt in fopt:
                            options["%s_%s" % (next.id, opt)]=opt
                        data['next']=next.id
                        data['options']=options    
                        data['clear_selection']=parts
                return HttpResponse(simplejson.dumps(data),mimetype='application/json')
            except Exception,e:
                data={'code':'NOK','message':e}
                return HttpResponse(simplejson.dumps(data),mimetype='application/json')
                
def post_lead(request, consumer_name, leadno):
    print 'post_lead %s %s' % (consumer_name, leadno)
    
    if consumer_name=='moss':
        lead = get_object_or_404(LeadEntry, pk=int(leadno))
        consumer = get_object_or_404(LeadConsumer, name=consumer_name.upper())
        t = consumer.post_lead(lead)
        if t.result == 'S':
            data={'code':'OK','price':t.payout}
        else:
            data={'code':t.custom_code,'message':t.custom_message}
    elif consumer_name=='ia':
        data={'code':'NOK','message':'Is out of service!'}
    return HttpResponse(simplejson.dumps(data),mimetype='application/json')

def delete_leadfile(request, leadfileno):
    if request.method=='POST':
        leadFile = get_object_or_404(LeadFile, id = int(leadfileno))
        for lead in leadFile.entries.all():
            if lead.transactions.count()==0:
                lead.delete ( )
        leadFile.delete()
        return HttpResponse('OK')
        
@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        
        form = LeadFileForm(request.POST, request.FILES )
        if form.is_valid():
#            handle_uploaded_file(request.FILES['lead_file'])
            leadFile = LeadFile(lead_file=form.cleaned_data['lead_file'], 
                                insurance_type=form.cleaned_data['insurance_type'],
                                cost=float(form.cleaned_data['cost']))
            leadFile.save()
            leadFile.parse_lead()
            return render_to_response('upload.html', {'lead_file':leadFile, 'form': form}, context_instance=RequestContext(request))
    else:
        return render_to_response('upload.html', {'form': LeadFileForm()}, context_instance=RequestContext(request))    
