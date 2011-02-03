#!/usr/bin/env python

#
# Generated Tue Jan 25 01:07:59 2011 by generateDS.py version 2.3b.
#

import sys

import msa as supermod

etree_ = None
Verbose_import_ = False
(   XMLParser_import_none, XMLParser_import_lxml,
    XMLParser_import_elementtree
    ) = range(3)
XMLParser_import_library = None
try:
    # lxml
    from lxml import etree as etree_
    XMLParser_import_library = XMLParser_import_lxml
    if Verbose_import_:
        print("running with lxml.etree")
except ImportError:
    try:
        # cElementTree from Python 2.5+
        import xml.etree.cElementTree as etree_
        XMLParser_import_library = XMLParser_import_elementtree
        if Verbose_import_:
            print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # ElementTree from Python 2.5+
            import xml.etree.ElementTree as etree_
            XMLParser_import_library = XMLParser_import_elementtree
            if Verbose_import_:
                print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree_
                XMLParser_import_library = XMLParser_import_elementtree
                if Verbose_import_:
                    print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree_
                    XMLParser_import_library = XMLParser_import_elementtree
                    if Verbose_import_:
                        print("running with ElementTree")
                except ImportError:
                    raise ImportError("Failed to import ElementTree from any known place")

def parsexml_(*args, **kwargs):
    if (XMLParser_import_library == XMLParser_import_lxml and
        'parser' not in kwargs):
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        kwargs['parser'] = etree_.ETCompatXMLParser()
    doc = etree_.parse(*args, **kwargs)
    return doc

#
# Globals
#

ExternalEncoding = 'ascii'

#
# Data representation classes
#

class MSALeadSub(supermod.MSALead):
    def __init__(self, Version='1.0', LeadData=None):
        super(MSALeadSub, self).__init__(Version, LeadData, )
supermod.MSALead.subclass = MSALeadSub
# end class MSALeadSub


class LeadDataSub(supermod.LeadData):
    def __init__(self, PartnerExcludeDirective=None, ContactDetails=None, InsurancePolicy=None, AutoLead=None, HomeLead=None):
        super(LeadDataSub, self).__init__(PartnerExcludeDirective, ContactDetails, InsurancePolicy, AutoLead, HomeLead, )
supermod.LeadData.subclass = LeadDataSub
# end class LeadDataSub


class PartnerExcludeDirectiveTypeSub(supermod.PartnerExcludeDirectiveType):
    def __init__(self, PartnerExclude=None):
        super(PartnerExcludeDirectiveTypeSub, self).__init__(PartnerExclude, )
supermod.PartnerExcludeDirectiveType.subclass = PartnerExcludeDirectiveTypeSub
# end class PartnerExcludeDirectiveTypeSub


class ContactDetailsTypeSub(supermod.ContactDetailsType):
    def __init__(self, FirstName=None, LastName=None, StreetAddress=None, City=None, State=None, ZIPCode=None, Email=None, PhoneNumbers=None, ResidenceStatus=None):
        super(ContactDetailsTypeSub, self).__init__(FirstName, LastName, StreetAddress, City, State, ZIPCode, Email, PhoneNumbers, ResidenceStatus, )
supermod.ContactDetailsType.subclass = ContactDetailsTypeSub
# end class ContactDetailsTypeSub


class PhoneNumbersSub(supermod.PhoneNumbers):
    def __init__(self, PhoneNumber=None):
        super(PhoneNumbersSub, self).__init__(PhoneNumber, )
supermod.PhoneNumbers.subclass = PhoneNumbersSub
# end class PhoneNumbersSub


class InsurancePolicyTypeSub(supermod.InsurancePolicyType):
    def __init__(self, NewPolicy=None, PriorPolicy=None):
        super(InsurancePolicyTypeSub, self).__init__(NewPolicy, PriorPolicy, )
supermod.InsurancePolicyType.subclass = InsurancePolicyTypeSub
# end class InsurancePolicyTypeSub


class NewPolicySub(supermod.NewPolicy):
    def __init__(self, RequestedCoverage=None, CoverageAmount=None):
        super(NewPolicySub, self).__init__(RequestedCoverage, CoverageAmount, )
supermod.NewPolicy.subclass = NewPolicySub
# end class NewPolicySub


class PriorPolicySub(supermod.PriorPolicy):
    def __init__(self, CurrentlyInsured=None, InsuranceCompany=None, PolicyExpirationDate=None, YearsContinuous=None, MonthsContinuous=None):
        super(PriorPolicySub, self).__init__(CurrentlyInsured, InsuranceCompany, PolicyExpirationDate, YearsContinuous, MonthsContinuous, )
supermod.PriorPolicy.subclass = PriorPolicySub
# end class PriorPolicySub


class AutoLeadTypeSub(supermod.AutoLeadType):
    def __init__(self, Vehicles=None, Drivers=None):
        super(AutoLeadTypeSub, self).__init__(Vehicles, Drivers, )
supermod.AutoLeadType.subclass = AutoLeadTypeSub
# end class AutoLeadTypeSub


class VehiclesSub(supermod.Vehicles):
    def __init__(self, Vehicle=None):
        super(VehiclesSub, self).__init__(Vehicle, )
supermod.Vehicles.subclass = VehiclesSub
# end class VehiclesSub


class VehicleSub(supermod.Vehicle):
    def __init__(self, Ownership=None, VehicleID=None, VIN=None, VehicleData=None, VehUse=None, ComphrensiveDeductible=None, CollisionDeductible=None, GarageType=None):
        super(VehicleSub, self).__init__(Ownership, VehicleID, VIN, VehicleData, VehUse, ComphrensiveDeductible, CollisionDeductible, GarageType, )
supermod.Vehicle.subclass = VehicleSub
# end class VehicleSub


class VehicleDataSub(supermod.VehicleData):
    def __init__(self, VehYear=None, VehMake=None, VehModel=None, VehSubmodel=None):
        super(VehicleDataSub, self).__init__(VehYear, VehMake, VehModel, VehSubmodel, )
supermod.VehicleData.subclass = VehicleDataSub
# end class VehicleDataSub


class DriversSub(supermod.Drivers):
    def __init__(self, Driver=None):
        super(DriversSub, self).__init__(Driver, )
supermod.Drivers.subclass = DriversSub
# end class DriversSub


class DriverSub(supermod.Driver):
    def __init__(self, DriverID=None, PersonalInfo=None, PrimaryVehicle=None, DriversLicense=None, DrivingRecord=None):
        super(DriverSub, self).__init__(DriverID, PersonalInfo, PrimaryVehicle, DriversLicense, DrivingRecord, )
supermod.Driver.subclass = DriverSub
# end class DriverSub


class PersonalInfoSub(supermod.PersonalInfo):
    def __init__(self, PersonID=None, Gender=None, MaritalStatus=None, RelationshipToApplicant=None, FirstName=None, LastName=None, BirthDate=None, SocialSecurityNumber=None, Occupation=None, MilitaryExperience=None, Education=None, CreditRating=None):
        super(PersonalInfoSub, self).__init__(PersonID, Gender, MaritalStatus, RelationshipToApplicant, FirstName, LastName, BirthDate, SocialSecurityNumber, Occupation, MilitaryExperience, Education, CreditRating, )
supermod.PersonalInfo.subclass = PersonalInfoSub
# end class PersonalInfoSub


class DriversLicenseSub(supermod.DriversLicense):
    def __init__(self, LicenseEverSuspendedRevoked=None, State=None, Number=None, LicensedAge=None):
        super(DriversLicenseSub, self).__init__(LicenseEverSuspendedRevoked, State, Number, LicensedAge, )
supermod.DriversLicense.subclass = DriversLicenseSub
# end class DriversLicenseSub


class DrivingRecordSub(supermod.DrivingRecord):
    def __init__(self, SR22Required=None, DriverTraining=None, DUIs=None, Accidents=None, Tickets=None, Claims=None):
        super(DrivingRecordSub, self).__init__(SR22Required, DriverTraining, DUIs, Accidents, Tickets, Claims, )
supermod.DrivingRecord.subclass = DrivingRecordSub
# end class DrivingRecordSub


class DUIsSub(supermod.DUIs):
    def __init__(self, DUI=None):
        super(DUIsSub, self).__init__(DUI, )
supermod.DUIs.subclass = DUIsSub
# end class DUIsSub


class DUISub(supermod.DUI):
    def __init__(self, Month=None, Year=None, State=None):
        super(DUISub, self).__init__(Month, Year, State, )
supermod.DUI.subclass = DUISub
# end class DUISub


class AccidentsSub(supermod.Accidents):
    def __init__(self, Accident=None):
        super(AccidentsSub, self).__init__(Accident, )
supermod.Accidents.subclass = AccidentsSub
# end class AccidentsSub


class AccidentSub(supermod.Accident):
    def __init__(self, Month=None, Year=None, Description=None, AtFault=None, WhatDamaged=None, InsurancePaidAmount=None):
        super(AccidentSub, self).__init__(Month, Year, Description, AtFault, WhatDamaged, InsurancePaidAmount, )
supermod.Accident.subclass = AccidentSub
# end class AccidentSub


class TicketsSub(supermod.Tickets):
    def __init__(self, Ticket=None):
        super(TicketsSub, self).__init__(Ticket, )
supermod.Tickets.subclass = TicketsSub
# end class TicketsSub


class TicketSub(supermod.Ticket):
    def __init__(self, Month=None, Year=None, Description=None):
        super(TicketSub, self).__init__(Month, Year, Description, )
supermod.Ticket.subclass = TicketSub
# end class TicketSub


class ClaimsSub(supermod.Claims):
    def __init__(self, Claim=None):
        super(ClaimsSub, self).__init__(Claim, )
supermod.Claims.subclass = ClaimsSub
# end class ClaimsSub


class ClaimSub(supermod.Claim):
    def __init__(self, Month=None, Year=None, Description=None, AtFault=None, WhatDamaged=None, InsurancePaidAmount=None):
        super(ClaimSub, self).__init__(Month, Year, Description, AtFault, WhatDamaged, InsurancePaidAmount, )
supermod.Claim.subclass = ClaimSub
# end class ClaimSub


class HomeLeadTypeSub(supermod.HomeLeadType):
    def __init__(self, PersonInfo=None, PropertyAddress=None, PropertyProfile=None, PropertyFeatures=None, Claims=None):
        super(HomeLeadTypeSub, self).__init__(PersonInfo, PropertyAddress, PropertyProfile, PropertyFeatures, Claims, )
supermod.HomeLeadType.subclass = HomeLeadTypeSub
# end class HomeLeadTypeSub


class PersonInfoSub(supermod.PersonInfo):
    def __init__(self, Gender=None, FirstName=None, LastName=None, BirthDate=None, CreditRating=None):
        super(PersonInfoSub, self).__init__(Gender, FirstName, LastName, BirthDate, CreditRating, )
supermod.PersonInfo.subclass = PersonInfoSub
# end class PersonInfoSub


class PropertyAddressSub(supermod.PropertyAddress):
    def __init__(self, PropAddress=None, PropCity=None, PropState=None, PropZIPCode=None):
        super(PropertyAddressSub, self).__init__(PropAddress, PropCity, PropState, PropZIPCode, )
supermod.PropertyAddress.subclass = PropertyAddressSub
# end class PropertyAddressSub


class PropertyProfileSub(supermod.PropertyProfile):
    def __init__(self, BusinessOrFarmingConducted=None, PropertyType=None, NumberUnits=None, DangerousDog=None, ConstructionDetails=None):
        super(PropertyProfileSub, self).__init__(BusinessOrFarmingConducted, PropertyType, NumberUnits, DangerousDog, ConstructionDetails, )
supermod.PropertyProfile.subclass = PropertyProfileSub
# end class PropertyProfileSub


class ConstructionDetailsSub(supermod.ConstructionDetails):
    def __init__(self, ExteriorWalls=None, Stories=None, Roof=None, Basement=None, BuiltYear=None, LivableSquareFootage=None, Bedrooms=None, Bathrooms=None, Garage=None, HeatingType=None, SecuritySystem=None, FireAlarm=None):
        super(ConstructionDetailsSub, self).__init__(ExteriorWalls, Stories, Roof, Basement, BuiltYear, LivableSquareFootage, Bedrooms, Bathrooms, Garage, HeatingType, SecuritySystem, FireAlarm, )
supermod.ConstructionDetails.subclass = ConstructionDetailsSub
# end class ConstructionDetailsSub


class PropertyFeaturesSub(supermod.PropertyFeatures):
    def __init__(self, Trampoline=None, HotTub=None, SumpPump=None, Deck=None, FireExtinguisher=None, CentralAirConditioning=None, DeadBolt=None, SmokeDetector=None, Sauna=None, Fireplace=None, SwimmingPool=None, WoodburningStove=None, valueOf_=None):
        super(PropertyFeaturesSub, self).__init__(Trampoline, HotTub, SumpPump, Deck, FireExtinguisher, CentralAirConditioning, DeadBolt, SmokeDetector, Sauna, Fireplace, SwimmingPool, WoodburningStove, valueOf_, )
supermod.PropertyFeatures.subclass = PropertyFeaturesSub
# end class PropertyFeaturesSub


class PhoneNumberTypeSub(supermod.PhoneNumberType):
    def __init__(self, Type=None, Number=None, Extension=None):
        super(PhoneNumberTypeSub, self).__init__(Type, Number, Extension, )
supermod.PhoneNumberType.subclass = PhoneNumberTypeSub
# end class PhoneNumberTypeSub


class ResidenceStatusTypeSub(supermod.ResidenceStatusType):
    def __init__(self, MonthsAt=None, YearsAt=None, valueOf_=None):
        super(ResidenceStatusTypeSub, self).__init__(MonthsAt, YearsAt, valueOf_, )
supermod.ResidenceStatusType.subclass = ResidenceStatusTypeSub
# end class ResidenceStatusTypeSub


class InsuranceCompanyTypeSub(supermod.InsuranceCompanyType):
    def __init__(self, MonthsWith=None, YearsWith=None, valueOf_=None):
        super(InsuranceCompanyTypeSub, self).__init__(MonthsWith, YearsWith, valueOf_, )
supermod.InsuranceCompanyType.subclass = InsuranceCompanyTypeSub
# end class InsuranceCompanyTypeSub


class VehUseTypeSub(supermod.VehUseType):
    def __init__(self, AnnualMiles=None, WeeklyCommuteDays=None, DailyCommuteMiles=None, valueOf_=None):
        super(VehUseTypeSub, self).__init__(AnnualMiles, WeeklyCommuteDays, DailyCommuteMiles, valueOf_, )
supermod.VehUseType.subclass = VehUseTypeSub
# end class VehUseTypeSub


class EducationTypeSub(supermod.EducationType):
    def __init__(self, GoodStudentDiscount=None, valueOf_=None):
        super(EducationTypeSub, self).__init__(GoodStudentDiscount, valueOf_, )
supermod.EducationType.subclass = EducationTypeSub
# end class EducationTypeSub


class CreditRatingTypeSub(supermod.CreditRatingType):
    def __init__(self, Bankruptcy=None, valueOf_=None):
        super(CreditRatingTypeSub, self).__init__(Bankruptcy, valueOf_, )
supermod.CreditRatingType.subclass = CreditRatingTypeSub
# end class CreditRatingTypeSub


class HomeCoverageTypeSub(supermod.HomeCoverageType):
    def __init__(self, PersonalLiability=None, Deductible=None, valueOf_=None):
        super(HomeCoverageTypeSub, self).__init__(PersonalLiability, Deductible, valueOf_, )
supermod.HomeCoverageType.subclass = HomeCoverageTypeSub
# end class HomeCoverageTypeSub


class HomeLeadSub(supermod.HomeLead):
    def __init__(self, PersonInfo=None, PropertyAddress=None, PropertyProfile=None, PropertyFeatures=None, Claims=None):
        super(HomeLeadSub, self).__init__(PersonInfo, PropertyAddress, PropertyProfile, PropertyFeatures, Claims, )
supermod.HomeLead.subclass = HomeLeadSub
# end class HomeLeadSub


class AutoLeadSub(supermod.AutoLead):
    def __init__(self, Vehicles=None, Drivers=None):
        super(AutoLeadSub, self).__init__(Vehicles, Drivers, )
supermod.AutoLead.subclass = AutoLeadSub
# end class AutoLeadSub


class InsurancePolicySub(supermod.InsurancePolicy):
    def __init__(self, NewPolicy=None, PriorPolicy=None):
        super(InsurancePolicySub, self).__init__(NewPolicy, PriorPolicy, )
supermod.InsurancePolicy.subclass = InsurancePolicySub
# end class InsurancePolicySub


class ContactDetailsSub(supermod.ContactDetails):
    def __init__(self, FirstName=None, LastName=None, StreetAddress=None, City=None, State=None, ZIPCode=None, Email=None, PhoneNumbers=None, ResidenceStatus=None):
        super(ContactDetailsSub, self).__init__(FirstName, LastName, StreetAddress, City, State, ZIPCode, Email, PhoneNumbers, ResidenceStatus, )
supermod.ContactDetails.subclass = ContactDetailsSub
# end class ContactDetailsSub


class PartnerExcludeDirectiveSub(supermod.PartnerExcludeDirective):
    def __init__(self, PartnerExclude=None):
        super(PartnerExcludeDirectiveSub, self).__init__(PartnerExclude, )
supermod.PartnerExcludeDirective.subclass = PartnerExcludeDirectiveSub
# end class PartnerExcludeDirectiveSub



def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    if hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'MSALead'
        rootClass = supermod.MSALead
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    doc = None
    return rootObj


def parseString(inString):
    from StringIO import StringIO
    doc = parsexml_(StringIO(inString))
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'MSALead'
        rootClass = supermod.MSALead
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('<?xml version="1.0" ?>\n')
    rootObj.export(sys.stdout, 0, name_=rootTag,
        namespacedef_='')
    return rootObj


def parseLiteral(inFilename):
    doc = parsexml_(inFilename)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'MSALead'
        rootClass = supermod.MSALead
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    doc = None
    sys.stdout.write('#from msa import *\n\n')
    sys.stdout.write('import msa as model_\n\n')
    sys.stdout.write('rootObj = model_.MSALead(\n')
    rootObj.exportLiteral(sys.stdout, 0, name_="MSALead")
    sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""

def usage():
    print USAGE_TEXT
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    root = parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()


