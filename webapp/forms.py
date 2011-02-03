# -*- coding: utf-8 -*-
from django.forms import ModelForm, PasswordInput
from django import forms
from django.utils.translation import ugettext_lazy as _

from models import LeadFile, LeadConsumer, LeadEntry

class LeadFileForm ( ModelForm ):
    class Meta:
        model = LeadFile
        exclude = ('entries','header')
    def __init__ (self, *args, **kwargs):
        super (LeadFileForm,self).__init__(*args, **kwargs)
        
class LeadConsumerForm(ModelForm):
    class Meta:
        model = LeadConsumer
        widgets = {
            'password': PasswordInput(),
        }
        
class LeadEntryForm ( ModelForm ):
    class Meta:
        model = LeadEntry
        fields = ('niche','source')
                
        
        
            