#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import csv
import urllib, urllib2
from xml import sax
from xml.sax import parseString
import tempfile

from schema_enum import get_enums_from_xsd

#'residenceStatusPeriod':14,

csvMap = {'PersonalInfo.FirstName':2, 'PersonalInfo.LastName':3, 'PersonalInfo.Email':4, 'PersonalInfo.WorkPhone':5,'PersonalInfo.CellPhone':6, 
          'PersonalInfo.StreetAddress1':8, 'PersonalInfo.StreetAddress2':9,'PersonalInfo.City':10, 'PersonalInfo.State':12, 'PersonalInfo.ZIPCode':13,
          'PersonalInfo.BirthDate':15, 'PersonalInfo.Gender':16, 'PersonalInfo.MaritalStatus':17, 'Education':18, 
          'Occupation':19, 'Vehicle.Year':20,'Vehicle.Make':21,'Vehicle.Model':22,
          'VehUse':24,'Vehicle.Use.daily':25, 'VehUse.AnnualMiles':26, 'RequestedCoverage':29,'GarageType':31,
          'ComphrensiveDeductible':32,'CollisionDeductible':33,'Driver.SR22':36,'ResidenceStatus':37, 
          'Driver.LicenseIssuedAge':38, 'Driver.LicenseNumber':39, 'PersonalInfo.GoodStudentDiscount':40, 'sub-model':44
         }
def getStreetAddress(row, sep=' '):
    if not row[csvMap['PersonalInfo.StreetAddress2']]:
        return row[csvMap['PersonalInfo.StreetAddress1']]
    return sep.join((row[csvMap['PersonalInfo.StreetAddress1']], row[csvMap['PersonalInfo.StreetAddress2']]))
def getBirthday(dt):
    if '-' in dt: return dt
    if '/' in dt:
        d = map(int,dt.split('/'))
    elif '.' in dt:    
        d = map(int,dt.split('.'))
    if d[2]<1900:
        d[2]+=1900  
    return '%s-%02d-%02d' % (d[2],d[0],d[1])    
class ResponseHandler(sax.handler.ContentHandler):
    def __init__(self):
        self.mapping = {}
    
    def startElement(self, name, attributes):
        if name.lower() == "msaresponse":
            return
        self.buffer = ""
    
    def characters(self, data):
        self.buffer += data
    
    def endElement(self, name):
        if name.lower() == "msaresponse":
            return
        self.mapping[name.lower()] = self.buffer
        self.buffer = ""

class SubModelResponseHandler(sax.handler.ContentHandler):
    def __init__(self):
        self.mapping = {}
    def startElement(self, name, attributes):
        if name.lower() == "VehicleInfo".lower():
#            self.mapping[name.lower()]={'model-year':attributes['Year'], 'make':attributes['Make'],'model':attributes['Model']}
            return
        if name.lower() not in self.mapping:
            self.mapping[name.lower()]=[]    
        self.buffer = ""
    
    def characters(self, data):
        self.buffer += data
    
    def endElement(self, name):
        if name.lower() == "VehicleInfo".lower():
            return
        self.mapping[name.lower()].append(self.buffer)
        self.buffer = ""

csvTitles =  [   "LoginID",
              "OrderDate"
              "FirstName",      # ContactDetail.FirstName 
              "LastName",       # ContactDetail.LastName
              "Email",          # ContactDetail.email 
              "Phone",          # ContactDetail.PhoneNumbers.PhoneNumber type="Work" 
              "Cell Phone",     # ContactDetail.PhoneNumbers.PhoneNumber type="Cell"
              "Night Phone",    
              "ShipToAddress1", # ContactDetail.StreetAddress
              "ShipToAddress2", # ContactDetail.StreetAddress
              "ShipToCity",     # ContactDetail.City
              "County",         
              "ShipToState",    # ContactDetail.State
              "ShipToZipcode",  # ContactDetail.ZIPCode
              "How long have you lived at your current residence?", # ContactDetail.ResidenceStatus YearsAt="4" MonthsAt="3" 
              "What is your Date of Birth?",    # Drivers.Driver.PersonalInfo.BirthDate
              "Gender",                         # Drivers.Driver.PersonalInfo Gender="Male" 
              "What is your marital status?",   # Drivers.Driver.PersonalInfo MaritalStatus="Single"  
              "What is your education level?",  # Drivers.Driver.PersonalInfo.Education / Bachelors Degree
              "What is your occupation",        # Drivers.Driver.PersonalInfo.Occupation
              "What is the year of your car?",
              "What is the make of your car?",
              "What is the model of your car?",
              "Is the vehicle financed leased or owned outright?",
              "What is the primary use for your vehicle?",                        # Vehicles.Vehicle.VehUse / Pleasure
              "Approximately how many miles is the car driven each day?",         # Vehicles.Vehicle.VehUse DailyCommuteMiles="5" 
              "About how many miles annually do you put on the car?",             # Vehicles.Vehicle.VehUse AnnualMiles="5000" 
              "How many miles does the vehicle have on it?",                      
              "What type of security system is on the vehicle?",
              "What level of coverage would you like your quotes for?",           # InsurancePolicy.NewPolicy.RequestedCoverage Standard Protection
              "Is the vehicle salvaged?",
              "Where is the vehicle parked at night?",
              "What is your preferred deductible for Comprehensive coverage?",    # Vehicles.Vehicle.VehUse.ComphrensiveDeductible
              "And what is your desired deductible for your Collision coverage?", # Vehicles.Vehicle.VehUse.ComissionDeductible
              "How would you say your credit rating is?",
              "What is the status of your license?",
              "Is there any type of special filing required - such as SR-22?",    # Drivers.Driver.DrivingRecord SR22Required="No"
              "Regarding your residence - do you own or rent?",                   # ContactDetail.ResidenceStatus Own from @OrderDate?
              "At what age did you get your drivers licence?",                    # Drivers.Driver.DriversLicense LicenseEverSuspendedRevoked="No"
              "What is your license number?",                                     # Drivers.Driver.DriversLicense.Number     
              "Is the driver of the primary vehicle insured a full time student?",# Drivers.Driver.PersonalInfo.Education GoodStudentDiscount="No" 
              "Do you need to add additional drivers other than yourself?",
              "In the Last 3 Years - Have you had any ACCIDENTS TICKETS or CLAIMS?:",
              "Have you had insurance coverage in the last 30 days?"]

xml = '''<?xml version="1.0" encoding="UTF-8"?>
<MSALead>
    <LeadData>
        <ContactDetails>
            <FirstName>Mike</FirstName>
            <LastName>Budd</LastName>
            <StreetAddress>3756 D Rt</StreetAddress>
            <City>Aliquippa</City>
            <State>PA</State>
            <ZIPCode>44843</ZIPCode>
            <Email>mike@test.com</Email>
            <PhoneNumbers>
                <PhoneNumber Type="Work">
                    <Number>7245834565</Number>
                    <Extension>5208</Extension>
                </PhoneNumber>
                <PhoneNumber Type="Home">
                    <Number>7245834563</Number>
                </PhoneNumber>
            </PhoneNumbers>
            <ResidenceStatus YearsAt="4" MonthsAt="3">Own</ResidenceStatus>
        </ContactDetails>
        <InsurancePolicy>
            <NewPolicy>
                <RequestedCoverage>Standard Protection</RequestedCoverage>
            </NewPolicy>
            <PriorPolicy CurrentlyInsured="Yes">
                <InsuranceCompany YearsWith="2" MonthsWith="6">10</InsuranceCompany>
                <PolicyExpirationDate>2010-06-01</PolicyExpirationDate>
                <YearsContinuous>2</YearsContinuous>
                <MonthsContinuous>6</MonthsContinuous>
            </PriorPolicy>
        </InsurancePolicy>
        <AutoLead>
            <Vehicles>
                <Vehicle VehicleID="1" Ownership="Yes">
                    <VIN>J8BE5J16067900000</VIN>
                    <VehUse AnnualMiles="5000" WeeklyCommuteDays="4" DailyCommuteMiles="5">Pleasure</VehUse>
                    <ComphrensiveDeductible>100</ComphrensiveDeductible>
                    <CollisionDeductible>100</CollisionDeductible>
                    <GarageType>No Cover</GarageType>
                </Vehicle>
            </Vehicles>
            <Drivers>
                <Driver DriverID="1">
                    <PersonalInfo Gender="Male" MaritalStatus="Single" RelationshipToApplicant="Self">
                        <FirstName>Mike</FirstName>
                        <LastName>Budd</LastName>
                        <BirthDate>1986-12-25</BirthDate>
                        <SocialSecurityNumber>207763376</SocialSecurityNumber>
                        <Occupation>Lawyer</Occupation>
                        <MilitaryExperience>No Military Experience</MilitaryExperience>
                        <Education GoodStudentDiscount="No">Bachelors Degree</Education>
                        <CreditRating Bankruptcy="No">Excellent</CreditRating>
                    </PersonalInfo>
                    <PrimaryVehicle>1</PrimaryVehicle>
                    <DriversLicense LicenseEverSuspendedRevoked="No">
                        <State>PA</State>
                        <Number>LIC2065</Number>
                        <LicensedAge>16</LicensedAge>
                    </DriversLicense>
                    <DrivingRecord SR22Required="No" DriverTraining="Yes">
                        <DUIs>
                            <DUI Year="2008" Month="05">
                                <State>PA</State>
                            </DUI>
                        </DUIs>
                        <Accidents>
                            <Accident Year="2009" Month="04">
                                <Description>Vehicle Hit Vehicle</Description>
                                <AtFault>No</AtFault>
                                <WhatDamaged>Property</WhatDamaged>
                                <InsurancePaidAmount>200</InsurancePaidAmount>
                            </Accident>
                        </Accidents>
                        <Tickets>
                            <Ticket Year="2010" Month="01">
                                <Description>Careless Driving</Description>
                            </Ticket>
                        </Tickets>
                        <Claims>
                            <Claim Year="2007" Month="05">
                                <Description>Fire Hail Water Damage</Description>
                                <AtFault>Yes</AtFault>
                                <WhatDamaged>Property</WhatDamaged>
                                <InsurancePaidAmount>500</InsurancePaidAmount>
                            </Claim>
                        </Claims>
                    </DrivingRecord>
                </Driver>
            </Drivers>
        </AutoLead>
    </LeadData>
</MSALead>'''
import msa
def num(x):
    if not x: return 0
    return x

def getGender(g):
    if g=='M': 
        return 'Male'
    else:
        return 'Female'
    
def get_reqval(label, row, lead):
    if lead.is_required_by_moss(label):
        return lead.get_moss_field_value(label)
    elif label in csvMap:
        return row[csvMap[label]]
    else:
        return None
    
def createPersonalInfo(personID, moss_driver):
    gender        = moss_driver.get_field_value('Gender')
    maritalStatus = moss_driver.get_field_value('MaritalStatus')
    firstName     = moss_driver.get_field_value('FirstName') 
    lastName      = moss_driver.get_field_value('LastName')
    birthDate     = getBirthday(moss_driver.get_field_value('BirthDate'))
    occupation    = moss_driver.get_field_value('Occupation')
    education_    = moss_driver.get_field_value('Education')
    militaryExperience = moss_driver.get_field_value('MilitaryExperience')
    creditRaiting = msa.CreditRatingType(Bankruptcy="No", valueOf_="Excellent")
    education     = msa.EducationType(moss_driver.get_field_value('GoodStudentDiscount'), education_)
    relationshipToApplicant = "Self"
    
    # socialSecurityNumber = militaryExperience = creditRating = None
    
    return msa.PersonalInfo(personID, 
                            Gender=gender, 
                            MaritalStatus=maritalStatus, 
                            RelationshipToApplicant=relationshipToApplicant, 
                            FirstName=firstName, 
                            LastName = lastName, 
                            BirthDate=birthDate, 
                            Occupation=occupation, 
                            Education=education, 
                            MilitaryExperience=militaryExperience,
                            CreditRating=creditRaiting)
def createDriver(moss_driver):
    moss_drv_lic = moss_driver.get_instance_subgroup('DriversLicense')
    moss_drv_rec = moss_driver.get_instance_subgroup('DrivingRecord')
    
    primaryVehicle=1
    driverID = 1
    personalInfo = createPersonalInfo(driverID, moss_driver)
    
    driversLicense = msa.DriversLicense(LicenseEverSuspendedRevoked=moss_drv_lic.get_field_value('LicenseEverSuspendedRevoked'), 
                                        Number=moss_drv_lic.get_field_value('LicenseNumber') or None, 
                                        LicensedAge=moss_drv_lic.get_field_value('LicenseIssuedAge'), 
                                        State=moss_drv_lic.get_field_value('State'))
    
    drivingRecord = msa.DrivingRecord ( moss_drv_rec.get_field_value('Driver.SR22'), 
                                        DriverTraining="Yes" )

    return msa.Driver(driverID, personalInfo, primaryVehicle, driversLicense, drivingRecord)

def createDrivers(row, lead):
    drivers = msa.Drivers()
    for moss_driver  in lead.get_moss_data().get_subgroup('Driver').get_instances():
        drivers.add_Driver ( createDriver ( moss_driver ) )
    return drivers
def createVechicles(row, lead):
    veh_moss = lead.get_moss_data().get_subgroup('Vehicle')
    vehicleID = 0
    vehicles = msa.Vehicles()
    for vehicle in veh_moss.get_instances():
        vehicleID += 1
        vehicleData = msa.VehicleData ( VehYear=vehicle.get_field_value('model-year'), 
                                        VehMake=vehicle.get_field_value('make'), 
                                        VehModel=vehicle.get_field_value('model'), 
                                        VehSubmodel=vehicle.get_field_value('sub-model') )
        
        vehUse = msa.VehUseType( valueOf_=vehicle.get_field_value('VehUse'), 
                                AnnualMiles=vehicle.get_field_value('VehUse.AnnualMiles'),  
                                DailyCommuteMiles=vehicle.get_field_value('DailyCommuteMiles'), 
                                WeeklyCommuteDays="0" 
                                )
        ownership = 'Yes' 
        comphrensiveDeductible = vehicle.get_field_value('ComphrensiveDeductible')
        collisionDeductible = vehicle.get_field_value('CollisionDeductible')
        garageType = vehicle.get_field_value('GarageType')
        vehicle = msa.Vehicle(Ownership=ownership, VehicleID=vehicleID, VehicleData=vehicleData, VehUse=vehUse, ComphrensiveDeductible=comphrensiveDeductible, CollisionDeductible=collisionDeductible, GarageType=garageType)
        vehicles.add_Vehicle(vehicle)
    
    return vehicles

def createAutoLead(lead):
    autoLead = msa.AutoLead(createVechicles(lead), createDrivers (lead) )
    return autoLead 
def createHomeLead(lead):
    personInfo = propertyAddress = propertyProfile = propertyFeatures = claims = None
    homeLead = msa.HomeLead(personInfo, propertyAddress, propertyProfile, propertyFeatures, claims)
    # Return homeLead instance here
    return None

def createContactDetails(lead):
    moss = lead.get_moss_data()  
    firstName     = moss.get_field_value('FirstName') 
    lastName      = moss.get_field_value('LastName')
#    streetAddress = getStreetAddress ( row )
    streetAddress = moss.get_field_value('StreetAddress')
    city          = moss.get_field_value('City')
    state         = moss.get_field_value('State')
    ZIPCode       = moss.get_field_value('ZIPCode')
    email         = moss.get_field_value('Email')  
    
    phoneNumbers  = msa.PhoneNumbers()
    if moss.get_field_value('Work Phone'):
        phoneNumbers.add_PhoneNumber( msa.PhoneNumberType ('Work', moss.get_field_value('Work Phone')) )
    if moss.get_field_value('Home Phone'):
        phoneNumbers.add_PhoneNumber( msa.PhoneNumberType ('Work', moss.get_field_value('Home Phone')) )    
    if moss.get_field_value('Cell Phone'):
        phoneNumbers.add_PhoneNumber( msa.PhoneNumberType ('Cell', moss.get_field_value('Cell Phone')) )                                                                 
       
#    residenceStatusPeriod = row[csvMap['residenceStatusPeriod']]

    monthsAt = moss.get_field_value('MonthsAt')
    yearsAt = moss.get_field_value('YearsAt')
    residenceStatus_ = moss.get_field_value('ResidenceStatus')
    
    residenceStatus = msa.ResidenceStatusType( MonthsAt=monthsAt, 
                                                 YearsAt=yearsAt, 
                                                 valueOf_=residenceStatus_
                                                )

    return msa.ContactDetails(firstName, lastName, streetAddress, city, state, ZIPCode, email, phoneNumbers, residenceStatus)
def createInsurancePolicy(row, lead):
    moss = lead.get_moss_data()
    requestedCoverage = moss.get_field_value('RequestCoverage')

    newPolicy = msa.NewPolicy ( RequestedCoverage=requestedCoverage )
    priorPolicy = msa.PriorPolicy(CurrentlyInsured="No")
    insurancePolicy = msa.InsurancePolicy(NewPolicy=newPolicy, PriorPolicy=priorPolicy)
    
    return insurancePolicy

def createLeadData(lead):
    partnerExcludeDirective = None
    insurancePolicy = createInsurancePolicy(lead) 
    autoLead = createAutoLead(lead)
    homeLead = createHomeLead(lead)
    contactDetails = createContactDetails (lead)
    
    leadData = msa.LeadData(partnerExcludeDirective, contactDetails, insurancePolicy, autoLead, homeLead)
    return leadData
def createMSALead(lead):
    return msa.MSALead(LeadData=createLeadData(lead))

def createOpener(name, url, affiliate_id, password):
    # Create an OpenerDirector with support for Basic HTTP Authentication...
    auth_handler = urllib2.HTTPBasicAuthHandler()
    if affiliate_id:
        auth_handler.add_password(realm=name,
                                  uri=url,
                                  user=affiliate_id,
                                  passwd=password)
    opener = urllib2.build_opener(auth_handler)
    # ...and install it globally so it can be used with urlopen.
    urllib2.install_opener(opener)

def post_lead(consumer, lead, callback=None):
    xml_request = get_lead_as_xml ( lead )
    print xml_request
    
    createOpener(consumer.name,consumer.url,consumer.affiliate_id, consumer.password)
    
    data=urllib.urlencode({'AffiliateID':consumer.affiliate_id,
                            'Password':consumer.password,
                            'Product':lead.niche.short_name,
                            'LeadData':xml_request,
                            'RequestType':consumer.request_type
                        })
    
    response_xml = urllib2.urlopen(consumer.url, data).read()
    print response_xml
    handler = ResponseHandler()
    parseString ( response_xml, handler )
    
    if handler.mapping['status'].lower().startswith('accepted'):
        callback(lead, float(handler.mapping['payout']), 'S')
    else:
        callback(lead, 0, 'F', handler.mapping['errordescription'],handler.mapping['errorcode'])
    
def get_required_field_value(value, group, callback):
    if value.field.name in ('model-year','make','model','sub-model'):
        
        queryCarData(value, 
                     group.get_field_value('model-year'), 
                     group.get_field_value('make'), 
                     group.get_field_value('model'), 
                     callback)
    elif value.method == 'X':
        import os.path
        file = os.path.join(os.path.dirname(__file__),'MSA.xsd')
        print 'parsing XSD at %s' % file 
        msa_xsd_enums = get_enums_from_xsd(file)
        print 'Looking up %s' % value.get_url()
        callback(msa_xsd_enums[value.get_url()])
            
def queryCarData(fieldValue, year=None, make=None, model=None, callback=None):
    
    data = {'affiliate_id':fieldValue.consumer.affiliate_id,
                            'password':fieldValue.consumer.password,
                        }
        
    if year: data['year']=year
    if make: data['make']=make
    if model: data['model']=model
    
    can_do_request = year is not None 
    
    if fieldValue.field.name=='sub-model': 
        can_do_request = can_do_request and make and model
    if fieldValue.field.name=='model': 
        can_do_request = year and make 
    if not can_do_request:
        print 'can not get [%s] having %s %s %s' % ( fieldValue.field.name, year, make, model)
        callback(None)
        return
    data=urllib.urlencode(data)
    response_xml = urllib2.urlopen(fieldValue.get_url(), data).read()
    
    handler = SubModelResponseHandler()
    parseString ( response_xml, handler )
    if callback:
        callback(handler.mapping[fieldValue.field.name])

def getModels(consumer, year, make):
    createOpener(consumer.name,'http://msadev1.msaff.com/xml-post/get_vehicle_info.php',consumer.affiliate_id, consumer.password)
    print consumer.affiliate_id, consumer.password  
    data=urllib.urlencode({'AffiliateID':consumer.affiliate_id,
                            'Password':consumer.password,
                            'year':year,
                            'make':make,
                        })
    
    response_xml = urllib2.urlopen('http://msadev1.msaff.com/xml-post/get_vehicle_info.php', data).read()
    print response_xml
#    handler = ResponseHandler()
#    parser.setContentHandler(handler)
#    parseString ( response_xml, handler )
    
def get_lead_as_xml( lead ):
    "Creates object structure. NOT THREAD SAFE!"
    msaLead = createMSALead ( lead )
    output = tempfile.TemporaryFile()
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    msaLead.export(output, 0,namespacedef_='')
    output.seek(0)    
    data = output.read()
    output.close()
    return data

def validate_lead( lead ):
    from lxml import etree
    import os.path
    file = os.path.join(os.path.dirname(__file__),'MSA.xsd')
    with open(file) as xsdFile:
        xsdText = etree.XML(xsdFile.read())
        schema = etree.XMLSchema(xsdText)
        parser = etree.XMLParser(schema = schema)
        etree.fromstring ( get_lead_as_xml(lead), parser )
    

def export_lead(row, header, firstName, lastName, city, state):
    if header: return
    msaLead = createMSALead(row)
    with open("%s %s_%s_%s.xml" % (firstName, lastName, city, state),'wb') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        msaLead.export(output, 0,namespacedef_='')
    
def parse_lead_file(file, row_callback = export_lead):
    with open(file, 'rb') as csvFile:
#        rows = csv.reader(csvFile, delimiter=';', quotechar='"')
        rows = csv.reader(csvFile)
        for idx, row in enumerate(rows):
            if not row[0]: continue
            row_callback(row,header=idx==0, 
                         firstName = row [ csvMap['PersonalInfo.FirstName'] ],
                         lastName = row [ csvMap['PersonalInfo.LastName'] ],
                         city  = row [ csvMap['PersonalInfo.city'] ],
                         state  = row [ csvMap['PersonalInfo.state'] ]
                         )
            
             
def main():
    parse_lead_file('../../../Ben-01-05-11-AUTO-confirmed-5.csv')
#    rows = csv.reader(open('Ben-01-05-11-AUTO-confirmed-5.csv', 'rb'), delimiter=';', quotechar='"')
#    for idx, row in enumerate(rows):
#        if idx>0:
#            msaLead = createMSALead(row)
#            firstName     = row [ csvMap['FirstName'] ] 
#            lastName      = row [ csvMap['LastName'] ]
#            output = open("%s_%s.xml" % (firstName, lastName),'wb')
#            msaLead.export(output, 0)
#            output.flush()
#            output.close()
        
if __name__ == '__main__':
    main()        
    
