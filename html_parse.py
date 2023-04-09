import json
import os
import re
from bs4 import BeautifulSoup

class PersonalInformation:
    
    def __init__(self, parserObj):
        self.parser = parserObj
        answer_boxes = self.parser.select ("td.answerbox")
        texts = [answer_box.text.strip() for answer_box in answer_boxes]
        [self.name, self.maiden, self.address, self.city, self.state, self.zip, self.passport_number, self.issued_date, self.expired_date,
         self.country_of_issuance, self.country_of_legal_residence, self.aliases, self.home_phone, self.email_address, self.date_of_availability] = texts
        personal_info = {
            "Name": self.name,
            "Maiden": self.maiden,
            "Address": self.address,
            "City": self.city,
            "State": re.sub("\s+", "", self.state),
            "Zip": self.zip,
            "Passport Number": self.passport_number,
            "Issued Date": self.issued_date,
            "Expired Date":self.expired_date,
            "Country of Issuance":self.country_of_issuance,
            "Country of Legal Residence": self.country_of_legal_residence,
            "Aliases": self.aliases,
            "Home Phone": self.home_phone,
            "Email Address": self.email_address,
            "Date of Availability": self.date_of_availability
        }
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Personal Information'] = personal_info

        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class AddressHistory:
    def __init__(self, parserObj):
        self.parser = parserObj
        trs = self.parser.select ("tr")
        trs.remove (trs[0])
        self.permanent = []
        self.history = []
        
        for i in range (len(trs)):
            tr = trs[i]
            tds = tr.select("td")
            if i == 0:
                self.permanent = {
                    "Address" : tds[1].text,
                    "City" : tds[2].text,
                    "State" : re.sub("\s+", "",tds[3].text),
                    "Zip" : tds[4].text
                }
            else:
                history_item = {
                    "From" : tds[0].text,
                    "To" : tds[1].text,
                    "Address" : tds[2].text,
                    "City" : tds[3].text,
                    "State" : re.sub("\s+", "",tds[4].text),
                    "Zip" : tds[5].text
                }
                self.history.append(history_item)
        
        AddressHistory = {
            "Permanent": self.permanent,
            "History" : self.history
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Address History'] = AddressHistory
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class EducationHistory:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return

        self.education_summary = {}
        self.education_history = []
        self.education_achievements = ""
        
        for i in range (len(tbodys)):
            tbody = tbodys[i]
            
            if i == 0:
                tds = tbody.select("td")
                self.education_summary = {
                    "YearOfCollege" : tds[1].text,
                    "Degree" : tds[3].text,
                    "FluentInEnglish" : tds[5].text,
                    "OtherLanguages" : tds[7].text
                }
            elif i==(len(tbodys)-2):
                continue
            elif i==(len(tbodys)-3):
                tds = tbody.select("td")
                education_history_item = {
                    "type" : tds[0].text.strip(),
                    "From" : tds[2].text,
                    "To" : tds[4].text,
                    "School" : tds[6].text.strip(),
                    "Address" : tds[8].text,
                    "City" : tds[10].text,
                    "State" : tds[12].text,
                    "Program" : tds[18].text,
                    "Graduate" : tds[21].text,
                    "GPA" : tds[23].text
                }
                self.education_history.append(education_history_item)
            elif i==(len(tbodys)-1):
                tds = tbody.select("td")
                self.education_achievements = re.sub("\s+", " ",tds[0].text).replace("\n"," ").strip(),
            else:
                tds = tbody.select("td")
                education_history_item = {
                    "type" : tds[0].text.strip(),
                    "From" : tds[2].text,
                    "To" : tds[4].text,
                    "School" : tds[6].text.strip(),
                    "Address" : tds[8].text,
                    "City" : tds[10].text,
                    "State" : tds[12].text,
                    "Program" : re.sub("\s+", " ",tds[15].text).replace("\n"," ").strip(),
                    "Graduate" : tds[18].text,
                    "GPA" : tds[20].text
                }
                self.education_history.append(education_history_item)
        EducationHistory = {
            "Summary": self.education_summary,
            "History" : self.education_history,
            "Achievements": self.education_achievements
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Education History'] = EducationHistory
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class DriversRecord:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return

        self.summary = {}
        self.violations = []
        
        summary_tds = tbodys[0].select("td")
        self.summary = {
            "License" : summary_tds[1].text.strip(),
            "State" : summary_tds[3].text.strip(),
            "Class" : summary_tds[5].text.strip(),
            "Expires" : summary_tds[7].text.strip()
        }

        violations = tbodys[1].select("tr")
        for i in range(1,len(violations)):
            tds = violations[i].select("td")
            violation_item = {
                "Violation" : tds[0].text.strip(),
                "Date" : tds[1].text,
                "City" : tds[2].text,
                "County" : tds[3].text,
                "State" : tds[4].text,
                "Disposition" : tds[5].text
            }
            self.violations.append(violation_item)
        DriversRecord = {
            "Summary": self.summary,
            "Violations" : self.violations
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Drivers Record'] = DriversRecord
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class CriminalRecord:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td")

        self.criminal_record = {
            "Driving while Impaired" : tds[1].text.strip(),
            "Under the Influence" : tds[3].text.strip(),
            "Driving While Intoxicated" : tds[5].text.strip(),
            "License Suspended" : tds[7].text.strip(),
            "License Revoked" : tds[9].text.strip(),
            "Additional Details" : tds[11].text.strip(),
            "Past 10years Criminal" : tds[13].text.strip(),
            "IfYes" : tds[15].text.strip()
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Criminal Record'] = self.criminal_record
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class EmploymentGeneral:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        EmploymentGeneral = {}
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")
        EmploymentGeneral['LegalToWork'] = tds[0].text
        EmploymentGeneral['AbleToRelocate'] = tds[1].text

        tbody = tbodys[1]
        tds = tbody.select ("td.answerbox")
        EmploymentGeneral['ContactPresent'] = tds[0].text
        EmploymentGeneral['ContactPrevious'] = tds[1].text
        
        tbody = tbodys[2]
        tds = tbody.select ("td.answerbox")
        EmploymentGeneral['EverDischarged'] = tds[0].text
        
        tbody = tbodys[4]
        tds = tbody.select ("td.answerbox")
        EmploymentGeneral['Details'] = tds[0].text
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Employment General'] = EmploymentGeneral
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class EmploymentHistory:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        EmploymentHistory = []
        for tbody in tbodys:
            item = {}
            trs = tbody.select ("tr")
            tds = trs[0].select ("td.answerbox")
            item['From'] = tds[0].text
            item['To'] = tds[1].text

            tds = trs[1].select ("td.answerbox")
            item['Company'] = tds[0].text
            item['Part121'] = tds[1].text
            item['Part135'] = tds[1].text
            
            tds = trs[2].select ("td.answerbox")
            item['Address'] = tds[0].text

            tds = trs[3].select ("td.answerbox")
            item['City'] = tds[0].text
            item['State'] = tds[1].text
            item['Zip'] = tds[2].text

            tds = trs[4].select ("td.answerbox")
            item['Position'] = tds[0].text

            tds = trs[5].select ("td.answerbox")
            item['Duties'] = tds[0].text

            tds = trs[6].select ("td.answerbox")
            item['ACFlown'] = tds[0].text

            tds = trs[7].select ("td.answerbox")
            item['HoursPerMonth'] = tds[0].text

            tds = trs[8].select ("td.answerbox")
            item['Supervisor'] = tds[0].text
            item['Phone'] = tds[1].text

            tds = trs[9].select ("td.answerbox")
            item['ReasonForLeaving'] = tds[0].text
            EmploymentHistory.append (item)
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Employment History'] = EmploymentHistory
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class EmploymentPresent:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td.answerbox")

        self.employment_present = {
            "From" : tds[0].text.strip(),
            "To" : tds[1].text.strip(),
            "Company" : tds[2].text.strip(),
            "Part121" : tds[3].text.strip(),
            "Part135" : tds[4].text.strip(),
            "Address" : tds[5].text.strip(),
            "City" : tds[6].text.strip(),
            "State" : tds[7].text.strip(),
            "Zip" : tds[8].text.strip(),
            "Position" : tds[9].text.strip(),
            "Duties" : tds[10].text.strip(),
            "AC Flown" : re.sub("\s+", " ",tds[11].text).replace("\n"," ").strip(),
            "Hours per Month" : tds[12].text.strip(),
            "Supervisor" : tds[13].text.strip(),
            "Phone" : tds[14].text.strip(),
            "Reason for Leaving" : tds[15].text.strip(),
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Employment Present'] = self.employment_present
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class UnemploymentFurlough:
    def __init__(self, parserObj):

        self.unemployment_history = []
        self.unemployment_details = ""

        self.parser = parserObj
        no_record = self.parser.select('[class="section noresults"]') 
        if len(no_record)>0:
            pass
        else:
            self.unemployment_history = []
            tds = self.parser.select("td")
            self.unemployment_details = re.sub("\s+", " ",tds[1].text).replace("\n"," ").strip()

        UnemploymentFurlough = {
            "History": self.unemployment_history,
            "Details" : self.unemployment_details
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['UnemploymentFurlough'] = UnemploymentFurlough
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class EmploymentMisc:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td")

        self.employment_misc = {
            "Professional Memberships" : re.sub("\s+", " ",tds[1].text).replace("\n"," ").strip(),
            "Achievements and Awards" : re.sub("\s+", " ",tds[3].text).replace("\n"," ").strip(),
            "Volunteer Charity Work" : re.sub("\s+", " ",tds[5].text).replace("\n"," ").strip(),
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Employment Misc'] = self.employment_misc
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class PilotExperienceGeneral:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td")

        self.pilotexperience_general = {
            "Chief Pilot" : tds[1].text.strip(),
            "Director of Operations" : tds[3].text.strip(),
            "Director of Safety" : tds[5].text.strip(),
            "Check Airman" : tds[7].text.strip(),
            "FAA Examiner" : tds[9].text.strip(),
            "FAA Approved Program Examiner" : tds[11].text.strip(),
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Pilot Experience General'] = self.pilotexperience_general
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class PilotCertificatesRatings:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td")

        self.pilotcertificates_ratings = {
            "Airplane MultiEngine Land (AMEL)" : tds[1].text.strip(),
            "Cert. Number" : tds[3].text.strip(),
            "Issue Date" : tds[5].text.strip(),
            "Flight Engineer Cert. Number" : tds[8].text.strip(),
            "Flight Engineer Issue Date" : tds[10].text.strip(),
            "Flight Engineer FE Turbojet" : tds[16].text.strip(),
            "Flight Engineer FE Turboprop" : tds[18].text.strip(),
            "Flight Engineer FE Reciprocating" : tds[20].text.strip(),
            "Airplane SEL" : tds[22].text.strip(),
            "Airplane MEL" : tds[24].text.strip(),
            "Airplane SES" : tds[26].text.strip(),
            "Airplane MES" : tds[28].text.strip(),
            "Rotor Helicopter" : tds[30].text.strip(),
            "Rotor Gyroplane" : tds[32].text.strip(),
            "Airship" : tds[38].text.strip(),
            "Balloon" : tds[40].text.strip(),
            "Powered Lift" : tds[46].text.strip(),
            "Glider" : tds[48].text.strip(),
            "Turbojet Typed" : tds[54].text.strip(),
            "B-737 Typed" : tds[56].text.strip(),
            "Large Aircraft Typed" : tds[58].text.strip(),
            "Instrument Airplane" : tds[60].text.strip(),
            "Instrument Helicopter" : tds[62].text.strip(),
            "Instrument Powered Lift" : tds[64].text.strip()
            
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Pilot Certificates Ratings'] = self.pilotcertificates_ratings
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class InstructorCertificatesRatings:
    def __init__(self, parserObj):
        self.parser = parserObj
        tds = self.parser.select ("td")

        self.instructorcertificates_ratings = {
            "Flight Instructor" : tds[1].text.strip(),
            "Flight Instructor Issue Date" : tds[3].text.strip(),
            "Ground School" : tds[9].text.strip(),
            "Ground School Issue Date" : tds[11].text.strip(),
            "Airplane Single Engine" : tds[17].text.strip(),
            "Airplane Multi Engine" : tds[19].text.strip(),
            "Rotor Helicopter" : tds[25].text.strip(),
            "Rotor Gyroplane" : tds[27].text.strip(),
            "Glider" : tds[33].text.strip(),
            "Powered Lift" :tds[41].text.strip(),
            "Instrument Airplane": tds[49].text.strip(),
            "Instrument Helicopter": tds[51].text.strip(),
            "Instrument Powered Lift": tds[53].text.strip(),
            "Ground Instructor - Basic": tds[55].text.strip(),
            "Ground Instructor - Advanced": tds[57].text.strip(),
            "Ground Instructor - Instrument": tds[59].text.strip(),
        }

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Instructor Certificates Ratings'] = self.instructorcertificates_ratings
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class FAAWrittenTests:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")

        FAAWrittenTests = {
            "ATPDate": tds[0].text,
            "ATPCurrent": tds[1].text,
            "FETurbojetDate": tds[2].text,
            "TurbojetCurrent": tds[3].text,
            "FETurbopropDate": tds[4].text,
            "TurbopropCurrent": tds[5].text,
            "FERecipDate": tds[6].text,
            "RecipCurrent": tds[7].text,
        }
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['FAA Written Tests'] = FAAWrittenTests
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class FAAMedicals:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")

        FAAMedicals = {
            "Class": tds[0].text,
            "Issued": tds[1].text,
            "Restrictions": tds[2].text,
        }
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['FAA Medicals'] = FAAMedicals
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class FAAMedicals:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")

        FAAMedicals = {
            "Class": tds[0].text,
            "Issued": tds[1].text,
            "Restrictions": tds[2].text,
        }
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['FAA Medicals'] = FAAMedicals
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class MiscCertificates:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")

        MiscCertificates = {
            "Dispatcher": tds[0].text,
            "DispatcherIssued": tds[1].text,
            "Airframe&Powerplant": tds[2].text,
            "APIssued": tds[3].text,
        }
        
        tbody = tbodys[1]
        tds = tbody.select ("td.answerbox")
        MiscCertificates["FCCPermit"] = tds[0].text
                
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Misc Certificates'] = MiscCertificates
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class FAAActions:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        tds = tbody.select ("td.answerbox")

        FAAActions = {
            "HadAccident": tds[0].text,
            "HadIncident": tds[1].text,
            "BeenVialated": tds[2].text,
        }
        
        tbody = tbodys[1]
        tds = tbody.select ("td.answerbox")
        FAAActions["CRL"] = tds[0].text
        FAAActions["AAT"] = tds[1].text
        FAAActions["PFP"] = tds[2].text
        
        tbody = tbodys[2]
        tds = tbody.select ("td.answerbox")
        FAAActions["Details"] = tds[0].text
        
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['FAA Actions'] = FAAActions
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class AircraftFlown:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        trs = tbody.select ("tr")
        
        AircraftFlown = []
        
        for i in range(len(trs)):
            if i == 0: continue
            tr = trs[i]
            tds = tr.select ("td.answerboxcenter")
            item = {
                "Model": tds[0].text.strip(),
                "PowerClass": tds[1].text,
                "Cat": tds[2].text,
                "PIC": tds[3].text,
                "Instr": tds[4].text,
                "SIC": tds[5].text,
                "Dual": tds[6].text,
                "Other": tds[7].text,
                "FE": tds[8].text,
                "Total": tds[9].text,
                "Typed": tds[10].text,
                "LastFlown": tds[11].text,
            }
            AircraftFlown.append (item)

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Aircraft Flown'] = AircraftFlown
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)


class FlightTimeByConditions:
    def __init__(self, parserObj):
        self.parser = parserObj
        tbodys = self.parser.select ("tbody")

        f= open("temp.json","w")

        f.write(str(tbodys))
        # f.write(str(trs[2]))

        f.close()
        # return
        
        tbody = tbodys[0]
        trs = tbody.select ("tr")
        
        FlightTimeByConditions = {
            "FlightCondition": {},
            "Simulator": {},
            "InstrumentApproaches": {},
            "MilitarySorties": {}
        }
        
        tr = trs[1]
        tds = tr.select ("td.answerboxcenter")
        item = {
            "ANight": tds[0].text,
            "AActualInstrument": tds[1].text,
            "ASimInstrument": tds[2].text,
            "ACrossCountry": tds[3].text,
        }
        tr = trs[3]
        tds = tr.select ("td.answerboxcenter")
        item['RNight'] = tds[0].text
        item['RActualInstrument'] = tds[1].text
        item['RSimInstrument'] = tds[2].text
        item['RCrossCountry'] = tds[3].text
        FlightTimeByConditions['FlightCondition'] = item
        
        tbody = tbodys[1]
        trs = tbody.select ("tr")
        tr = trs[1]
        tds = tr.select ("td.answerboxcenter")
        item = {}
        item = {
            "PIC": tds[0].text,
            "Instructor": tds[1].text,
            "SIC": tds[2].text,
            "Dual": tds[3].text,
        }
        FlightTimeByConditions['Simulator'] = item

        tbody = tbodys[2]
        trs = tbody.select ("tr")
        tr = trs[1]
        tds = tr.select ("td.answerboxcenter")
        item = {}
        item = {
            "Within6": tds[0].text,
            "Within12": tds[1].text,
        }
        FlightTimeByConditions['InstrumentApproaches'] = item
        
        tbody = tbodys[3]
        trs = tbody.select ("tr")
        tr = trs[1]
        tds = tr.select ("td.answerboxcenter")
        item = {}
        item = {
            "PIC": tds[0].text,
            "Instructor": tds[1].text,
            "SIC": tds[2].text,
            "Dual": tds[3].text,
        }
        tr = trs[3]
        tds = tr.select ("td.answerboxcenter")
        item['Turbine'] = tds[0].text
        item['MultiEngine'] = tds[1].text
        FlightTimeByConditions['MilitarySorties'] = item
        
        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Flight Time By Conditions'] = FlightTimeByConditions
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class Addendum:
    def __init__(self, parserObj):
        self.parser = parserObj
        trs = self.parser.select ("tr")
        self.addendum = []
        for tr in trs:
            q = tr.select ("td.questiontext")[0].text
            a = tr.select("td.answerbox")[0].text
            q = re.sub("\s+", " ",q).replace("\n"," ").strip()
            a = re.sub("\s+", " ",a).replace("\n"," ").strip()
            item={
                "question":q,
                "answer":a
            }
            self.addendum.append(item)

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Addendum'] = self.addendum
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class GeneralReferences:
    def __init__(self, parserObj):
        self.parser = parserObj
        trs = self.parser.select ("tr")
        self.general_reference = []
        for tr in trs[1:]:
            tds = tr.select("td")
            
            item={
                "Name":tds[0].text,
                "Employer":tds[1].text,
                "Position":tds[2].text,
                "From":tds[3].text,
                "To":tds[4].text,
                "PhoneNumber":tds[5].text,
                "EmailAddress":tds[6].text
            }
            self.general_reference.append(item)

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['GeneralReferences'] = self.general_reference
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class Disclosure:
    def __init__(self, parserObj):
        self.parser = parserObj
        self.answer = self.parser.select ("td.answerbox")[0].text

        with open('input.json', 'r') as f:
            orig_data = json.load(f)
        
        orig_data['Disclosure Answer'] = self.answer
        
        with open("input.json", "w+") as f:
            json.dump(orig_data, f)

class HTMLParser:
    
    source_html = ""
    personal_information = None
    
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)

    def setSourceHtml (self, source_html):
        self.source_html = source_html
    
    def correctHtml (self):
        fd = open (self.source_html, "r")
        self.source_string = fd.read()
        fd.close()
        self.source_string = self.source_string.replace ("&#39;", "").replace ("&nbsp;", "")
    
    def parseInitialize (self, source_html):
        self.setSourceHtml (source_html)
        if self.source_html == "": return
        self.correctHtml ()
        self.parser = BeautifulSoup (self.source_string, "lxml")
    
    def parse (self):
        self.personal_information = PersonalInformation (self.parser.select ("div#PersonalInformation")[0])
        self.address_history = AddressHistory (self.parser.select ("div#AddressHistory")[0])
        self.education_history = EducationHistory (self.parser.select ("div#EducationHistory")[0])
        self.drivers_record = DriversRecord(self.parser.select("div#DriversRecord")[0])
        self.criminal_record = CriminalRecord(self.parser.select("div#CriminalRecord")[0])
        self.employment_general = EmploymentGeneral (self.parser.select ("div#EmploymentGeneral")[0])
        self.employment_present = EmploymentPresent(self.parser.select("div#EmploymentPresent")[0])
        self.employment_history = EmploymentHistory (self.parser.select ("div#EmploymentHistory")[0])
        self.unemployment_furlough = UnemploymentFurlough(self.parser.select("div#UnemploymentFurlough")[0])
        self.employment_misc = EmploymentMisc(self.parser.select("div#EmploymentMisc")[0])
        self.pilotexperience_general = PilotExperienceGeneral(self.parser.select("div#PilotExperienceGeneral")[0])
        self.pilotcertificates_ratings = PilotCertificatesRatings(self.parser.select("div#PilotCertificatesRatings")[0])
        self.instructorcertificates_ratings = InstructorCertificatesRatings(self.parser.select("div#InstructorCertificatesRatings")[0])

        self.faa_written_tests = FAAWrittenTests (self.parser.select ("div#FAAWrittenTests")[0])
        self.faa_medicals = FAAMedicals (self.parser.select ("div#FAAMedicals")[0])
        self.misc_certificates = MiscCertificates (self.parser.select ("div#MiscCertificates")[0])
        self.faa_actions = FAAActions (self.parser.select ("div#FAAActions")[0])
        self.aircraft_flown = AircraftFlown (self.parser.select ("div#AircraftFlown")[0])
        self.flight_time = FlightTimeByConditions (self.parser.select ("div#FlightTimeByConditions")[0])
        self.addendum = Addendum(self.parser.select ("div#Addendum")[0])
        self.general_references = GeneralReferences(self.parser.select ("div#GeneralReferences")[0])
        self.disclosure = Disclosure(self.parser.select ("div#TransportationSecurityRegulation")[0])

if __name__ == "__main__":
    hp = HTMLParser ()
    hp.parseInitialize ("1.html")
    hp.parse ()