# coding: utf-8
"""
Manages lead posts to registered lead consumers 
"""

from settings import LEAD_ROUTES, LEAD_PARSERS, LEAD_FIELDS
import settings
import urllib, urllib2

from msa_plugin.msafactory import get_lead_as_xml 

def fallback_post_lead(consumer, lead, callback ):
    callback(lead,0,'E', '%s is  misconfigured! Check your plugin settings.' % consumer.name)


def post_lead(lead, consumer, callback):
    try:
        return  getattr(settings,LEAD_ROUTES[consumer.name], fallback_post_lead)(
                                                                                            consumer, 
                                                                                            lead,
                                                                                            callback)
    except KeyError:
        callback(lead,0,'E')
            
def get_field_value(fieldValue, group, callback):    
    LEAD_FIELDS[fieldValue.consumer.name] ( fieldValue, group, callback )
    
def parse_csv_file(filename, cb):        
    getattr(settings, LEAD_PARSERS['csv'])(filename, cb)
    
def main():
    
    s = 'jmtidalgo;1.4.11;BONNIE;BELL;ezerinkc@netscape.net;8164717556;;8164717556;2313 Erie St;;KANSAS CITY;clay;MO;64116;20 years 1 months;11.15.50;M;Single;Masters;Retired;1985;CHEVROLET;CELEBRITY;Owned;Pleasure;10;5000;100000;No;State;;Street;No;No;Excellent;Active;No;Own;16;;No;No;no;Yes'
    record = s.split(';')
    
    xml = get_lead_as_xml ( record )
    print xml
    
    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='MOSS',
                              uri='http://msadev1.msaff.com/xml-post/lead.php',
                              user='CD1',
                              passwd='CD1')
    opener = urllib2.build_opener(auth_handler)
    # ...and install it globally so it can be used with urlopen.
    urllib2.install_opener(opener)
    
    data=urllib.urlencode({'AffiliateID':'CD1',
                    'Password':'CD1',
                    'Product':'auto',
                    'LeadData':xml,
                    'RequestType':'direct'})
    
    print urllib2.urlopen('http://msadev1.msaff.com/xml-post/lead.php', data).read()
    
    
if __name__ == '__main__':
    main()    
