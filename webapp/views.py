from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from forms import LeadFileForm, LeadEntryForm

from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.utils import simplejson
from django.db.models import Sum

from datetime import date

from models import LeadFile, LeadConsumer, LeadEntry, LeadFieldValue, LeadTransaction
from msa_plugin.msafactory import csvMap, validate_lead as moss_validate_lead
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
            
@csrf_protect    
def new_lead(request, consumer_name):
    lead = None
    if consumer_name=='moss':
        consumer = get_object_or_404(LeadConsumer, name='MOSS')
        titles = [x for x in csvMap.keys()]
        titles = consumer.get_diff(titles)
        titles.sort()
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
                lead.first_name = request.POST['PersonalInfo.FirstName']            
                lead.last_name = request.POST['PersonalInfo.LastName']
#                lead.state = request.POST['PersonalInfo.State']
                lead.city = request.POST['PersonalInfo.City']
                
                record = ['' for x in range(0, 44)]

                titles = []        
                for attr in request.POST:
                    if attr not in csvMap: continue
                    record[csvMap[attr]]=request.POST[attr]
                    titles.append(Value(attr,request.POST[attr]))
                lead.set_data_record(record)
                lead.save()
                if 'lead_id' not in request.POST: 
                    return render_to_response('mossform.html', 
                                  {'titles': titles, 'lead':lead, 'form':leadForm},
                                  context_instance=RequestContext(request)
                                  )
                else:
                    lead.state = lead.get_moss_field_value('PersonalInfo.State')
                    lead.save()
                    try:
                        moss_validate_lead ( lead )
                        return HttpResponseRedirect('/lead/moss/new_lead')
                    except XMLSyntaxError, msg:
                        return render_to_response('mossform.html', 
                              {'titles': titles, 'lead':lead, 'error':msg,'form':leadForm},
                              context_instance=RequestContext(request)
                              )         
            except KeyError, e:
                return render_to_response('mossform.html', 
                              {'titles': titles, 'error':e,'form':leadForm},
                              context_instance=RequestContext(request)
                              )    
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
        data = lead.get_data_as_list()
        MOSS = LeadConsumer.objects.get(name='MOSS')
        titles = [x for x in csvMap.keys()]
        titles = MOSS.get_diff(titles)
        titles.sort()
        values = []
        for attr in titles:
            values.append(Value(attr,data[csvMap[attr]]))
        
        return render_to_response('lead_table.html', {'lead':lead, 'values':values}, context_instance=RequestContext(request))
    except LeadFile.DoesNotExist:
        print 'LeadEntry pk=%s does not exists' % leadno

def save_field_value(request):
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
                data={'code':'OK', 'entry_id':lfv.entries.all()[0].id, 'is_complete':lfv.entries.all()[0].is_complete()}
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
