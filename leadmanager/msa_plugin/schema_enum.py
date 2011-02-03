from xml import sax
from xml.sax import parse

class XSDEnumResponseHandler(sax.handler.ContentHandler):
    def __init__(self):
        self.mapping = {}
        self.restriction = None
        self.myenum = None
    
    def startElement(self, name, attributes):
        if name.lower() == "xs:simpletype":
            self.mapping[attributes['name']]=[]
            self.myenum = attributes['name'] 
        if name.lower() == "xs:restriction":
            self.restriction=attributes['base']
        if name.lower() == "xs:enumeration" and self.myenum and self.restriction:        
            self.mapping[self.myenum].append(attributes['value'])
    
    def characters(self, data):
        pass
    
    def endElement(self, name):
        if name.lower() == "xs:simpletype":
            self.restriction = None
            self.myenum = None
            
def get_enums_from_xsd(file):
    handler = XSDEnumResponseHandler()
    parse(file, handler)
    return handler.mapping

if __name__ == '__main__':
    xsd = get_enums_from_xsd('MSA.xsd')
    print xsd['MonthsAtType']