import json
import openai
import re
import enchant
import zipcodes
import pycountry
from uszipcode import SearchEngine
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from datetime import datetime, timedelta
import time
openai.api_key = "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"

with open('input.json', 'r') as f:
    data = json.load(f)

report_text = ""
report_file = open("report.txt", "w")

pattern_pinfo_name = r"^[A-za-z]+(\s|,)+[A-za-z]+(\s|,)+[A-za-z]*$"
pattern_pfino_maiden = r"^(\s*N/A\s*) | ([A-za-z]+(\s|,)+[A-za-z]+(\s|,)+[A-za-z]*)$"
pattern_phone_number = r"^\d\d\d-\d\d\d-\d\d\d\d$"
pattern_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
pattern_address = r"^\d+\s+\w+\s+\w+\s+\w+$"
question_pinfo_name = "This is someone's First Name and Last Name.\n" + data['Personal Information']['Name'] + "\n Is this valid format?"
question_pinfo_name = "This is someone's Maiden Name.\n" + data['Personal Information']['Name'] + "\n Is this valid format for common maiden name?"
question_pinfo_passport = "This is " + data['Personal Information']['Country of Issuance'] + "' passport - " + data['Personal Information']['Passport Number'] + " Is this format correct?"

def getAnswerFromAI(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a chatbot"},
                {"role": "user", "content": question},
            ]
    )

    result = ''
    for choice in response.choices:
        result += choice.message.content

    return result

def checkFormat(pattern, str):
    match = re.match(pattern, str)
    if(match == None):
        return False
    else:
        return True
    
def spell_check(text):
    d = enchant.Dict("en_US")
    words = text.split()
    misspelled = [word for word in words if not d.check(word)]
    return misspelled

def is_valid_address(address):
    geolocator = Nominatim(user_agent='review-app')
    try:
        location = geolocator.geocode(address)
        return True if location else False
    except GeocoderTimedOut:
        return False
    
def validate_city_state_zip(city, state, zip_code):
    search = SearchEngine()
    result = search.by_city_and_state(city, state)
    if not result:
        return False
    zip_info = zipcodes.matching(zip_code)
    if not zip_info:
        return False
    zip_info = zip_info[0]
    if zip_info['city'] != city or zip_info['state'] != state:
        return False
    return True

def validate_passport(passport_number):
    pattern = r'^[A-Z]{2}\d{7}$'
    if re.match(pattern, passport_number):
        return True
    else:
        return False
    
def validate_country(country_name):
    try:
        # Attempt to lookup country by name
        country = pycountry.countries.get(name=country_name)
        return True
    except KeyError:
        try:
            # Attempt to lookup country by ISO code
            country = pycountry.countries.get(alpha_2=country_name.upper())
            return True
        except KeyError:
            return False

# validating all fields
result = ''
pinfo = data['Personal Information']
# Name field
if(checkFormat(pattern_pinfo_name, pinfo['Name']) == False):
    # result = getAnswerFromAI(question_pinfo_name)
    print("First Name and Last Name is not correct.")
    # print(result)
    report_text += "First Name and Last Name is not correct."
    # report_text += result
print('\n')
report_text += '\n\n'

# Maiden field
if(checkFormat(pattern_pinfo_name, pinfo['Maiden']) == False and pinfo['Maiden'] != 'N/A'):
    # result = getAnswerFromAI(question_pinfo_name)
    print("Maiden name is not correct.")
    report_text += "Maiden name is not correct."
# print(result + '\n')
# report_text += result
report_text += '\n\n'


# Address field
if(spell_check(pinfo['Address']) == False):
    print("Street Address spelling is not correct\n")
    report_text += "Street Address spelling is not correct\n\n"

if(spell_check(pinfo['City']) == False):
    print("City name spelling is not correct\n")
    report_text += "City name spelling is not correct\n\n"

full_addr = pinfo['Address'] + "," + pinfo['City'] + "," + pinfo['State'] + " " + pinfo['Zip']
if(is_valid_address(full_addr)):
    print("Address is valid\n\n")
else:
    print(full_addr)
    print("Address is invalid\n")
    report_text += full_addr
    report_text += "\nAddress is invalid\n\n"

# Country of Issuance and Country of Legal Residence
if(validate_country(pinfo['Country of Issuance']) == False):
    print(pinfo['Country of Issuance'])
    print("Above country name is incorrect.\n")
    report_text += pinfo['Country of Issuance']
    report_text += "Above country name is incorrect.\n\n"

if(validate_country(pinfo['Country of Legal Residence']) == False):
    print(pinfo['Country of Legal Residence'])
    print("Above country name is incorrect.\n")
    report_text += pinfo['Country of Legal Residence']
    report_text += "Above country name is incorrect.\n\n"

# Passport Number
if(validate_passport(pinfo['Passport Number']) == False):
    print(pinfo['Passport Number'],"\n")
    print("Above passport number is incorret. Please input again.")
    result = getAnswerFromAI(question_pinfo_passport)
    print(result + "\n")
    report_text += pinfo['Passport Number']
    report_text += "\nAbove passport number is incorret. Please input again."
    report_text += result
    report_text += '\n\n'

#Aliases
if(validate_country(pinfo['Aliases']) == False and pinfo['Aliases'] != "N/A"):
    print(pinfo['Aliases'])
    print("Above Aliases is incorrect.\n")
    report_text += pinfo['Aliases']
    report_text += "Above Aliases is incorrect.\n\n"

#Home Phone
if(checkFormat(pattern_phone_number, pinfo['Home Phone']) == False):
    print("Phone number format is not correct, Please input again.\n")
    report_text += "Phone number format is not correct, Please input again.\n\n"

#Email
if(checkFormat(pattern_email, pinfo['Email Address']) == False):
    print("Email Addresss is not correct. Please input it again.\n")
    report_text += "Email Addresss is not correct. Please input it again.\n\n"

# Address History
addr_history = data['Address History']
# Permanent
permanent = addr_history['Permanent']

if(checkFormat(pattern_address, permanent['Address']) == False):
    print("Permanent address format is incorrect. Please have a look on that and fix if it's possible.\n")
    report_text += "Permanent address format is incorrect. Please have a look on that and fix if it's possible.\n\n"

if(is_valid_address(permanent['Address']) == False):
    print("Permanent address you input is invalid. Please try again to input it.\n")
    report_text += "Permanent address you input is invalid. Please try again to input it.\n\n"

if(validate_city_state_zip(permanent['City'], permanent['State'], permanent['Zip']) == False):
    print("Permanent City, State and Zips are not matched. Please have a look on them.\n")
    report_text += "Permanent City, State and Zips are not matched. Please have a look on them.\n\n"

# History
history = addr_history['History']
total_days = timedelta(days = 0)
for item in history:
    if(is_valid_address(item['Address']) == False or spell_check(item['Address']) == False):
        print(item)
        print("Above Street Address is not correct.\n")
        report_text += str(item)
        report_text += "Above Street Address is not correct.\n\n"

    if(validate_city_state_zip(item['City'], item['State'], item['Zip']) == False):
        print(item)
        print("Above City, State and Zips are not matched. Please have a look on them.\n")
        report_text += str(item)
        report_text += "Above City, State and Zips are not matched. Please have a look on them.\n\n"

    if(item['To'] != 'Present'):
        to_date = datetime.strptime(item['To'], '%m/%d/%Y')
    else:
        to_date = datetime.today()

    from_date = datetime.strptime(item['From'], '%m/%d/%Y')

    total_days += to_date - from_date

to_date = datetime.today()
from_date = datetime.strptime(history[len(history) - 1]['From'], '%m/%d/%Y')
if total_days.days != (to_date-from_date).days:
    print("There is overlaps or gaps in Address History. Please take a look on it and fix it.")
    report_text += "There is overlaps or gaps in Address History. Please take a look on it and fix it."

# Education History
print("Processing Education History...")
educaton_history = data["Education History"]
edu_summary = educaton_history["Summary"]
edu_history = educaton_history["History"]
edu_achievements = educaton_history["Achievements"]

total_days = timedelta(days = 0)
for item in edu_history:
    # print("\n\n",item,"\n\n")
    if item['type'].find("University")>=0 or item['type'].find("College")>=0:
        from_date = datetime.strptime(item['From'], '%m/%d/%Y')
        to_date = datetime.strptime(item['To'], '%m/%d/%Y')
        delta = to_date - from_date
        total_days+=delta
if total_days.days < int(edu_summary["YearOfCollege"])*365:
    print("Total years calculated of College and high education is not correct\n\n")
    report_text +="Total years calculated of College and high education is not correct\n\n"
if spell_check(edu_summary['Degree']) == False:
    print("Degree spelling is not correct\n\n")
    report_text += "Degree spelling is not correct\n\n"
if not edu_summary["FluentInEnglish"] in ["Yes", "No"]:
    print("Fluent In English field is not vaild")
    report_text+="Fluent In English field is not vaild\n\n"
if edu_summary["OtherLanguages"].strip()=="":
    print("Other Languages field should be N/A if you don't know other languages\n\n")
    report_text+="Other Languages field should be N/A if you don't know other languages\n\n"
if edu_summary["OtherLanguages"].find("English"):
    print("If you know only English, Other Langauges field should be set as N/A\n\n")
    report_text+=("If you know only English, Other Langauges field should be set as N/A\n\n")
highschool_count=0
for item in edu_history:
    text=""
    

    if not spell_check(item["School"]):
        text+= "School spelling is not correct\n"
    if not spell_check(item["Program"]):
        text+= "Program spelling is not correct\n"
    full_addr = item['Address'] + "," + item['City'] + "," + item['State']
    if not is_valid_address(full_addr):
        text+="Address is not valid\n"
    if item["Graduate"] in ["Yes, No"]:
        text+="Graduate field should be Yes or No\n"
    if item['type'].find("High School")==-1:
        if item["GPA"].strip()=="":
            text+="GPA field shoulb be actual number like 3.5 or N/A\n"
        elif item["GPA"]!="N/A":
            try:
                float(item["GPA"])
            except ValueError:
                text+="GPA field shoulb be actual number like 3.5 or N/A\n"
    if item['type'].find("High School")>=0:
        highschool_count+=1
        if item['Program'].strip()!="High School Diploma":
           text+="We recommend to set Program field of High School as High School Diploma\n"
        if item['Graduate'].strip()!="Yes":
            text+="Graduate field should be Yes\n"
        try:
            float(item["GPA"])
        except ValueError:
            text+="GPA field shoulb be actual number like 3.5\n"
    
    if text:
        print(item)
        print(text+"\n")
        report_text+=str(item)+"\n"+text+"\n"
if highschool_count==0:
    print("All applications must have High School\n\n")
    report_text+="All applications must have High School\n\n"

# Drivers record
print("Processing Drivers record...")

drivers_record = data["Drivers Record"]
dr_summary = drivers_record["Summary"]
dr_violations = drivers_record["Violations"]

if dr_summary["License"]=="":
    report_text+="Drivers License is blank\n"
if dr_summary["State"] =="":
    report_text+="Drivers State is blank\n"
from_date = datetime.today()
to_date = datetime.strptime(dr_summary["Expires"], '%m/%d/%Y')
total_days = timedelta(days = 0)
total_days += to_date - from_date
if total_days.days<90:
    report_text+="Caution! Driver License will be expired within 90 days\n\n"

for item in dr_violations:
    err = False
    r_text = ""
    if spell_check(item["Violation"]) == False:
        err =True
        r_text += "Violation spelling is not correct\n"
    if (datetime.strptime(item["Date"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
        err=True
        r_text+="violation date is not past date\n"
    if spell_check(item["City"]) == False:
        err =True
        r_text += "City spelling is not correct\n"
    if spell_check(item["County"]) == False:
        err =True
        r_text += "County spelling is not correct\n"
    if spell_check(item["Disposition"]) == False:
        err =True
        r_text += "Disposition spelling is not correct\n"
    if err:
        report_text +=str(item)+"\n"+r_text+"\n"

end_line ="-------------------------------------------------------\n\n"

# Employment Present
print("Processing Employment Present...")

report_text+= "Employment Present\n\n"
employment_present = data["Employment Present"]
if (datetime.strptime(employment_present["From"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
    report_text+=" From date is not past date\n"
if employment_present["To"].strip() != "Present":
    report_text += " To date is not Present\n"
if spell_check(employment_present["Company"]) == False:
    report_text += " Company spelling is not correct\n"
full_addr = employment_present['Address'] + "," + employment_present['City'] + "," + employment_present['State'] + " " + employment_present['Zip']
if not is_valid_address(full_addr):
    report_text += " Address is not valid\n"
if employment_present["Position"]=="":
    report_text+=" Position is blank\n"
if employment_present["Position"]=="Pilot":
    report_text+=" Position: Please identify Seat position by first officer or captain\n"
if spell_check(employment_present["Duties"]) == False:
    report_text += " Duties spelling is not correct\n"
if employment_present["Duties"][-1]!=".":
    report_text += " Duties was cut off\n"
if len(employment_present["Duties"])<400:
    report_text += "We recommend you to write more than 500 characters for  Duties\n"
if employment_present["AC Flown"]=="":
    report_text += " AC Flown is blank, Please fill with N/A\n"
if employment_present["Hours per Month"] in ["","0"]:
    report_text += " Hours per Month is not valid, if it's not specified, fill with N/A\n"
if employment_present["Supervisor"]=="":
    report_text += " Supervisor is blank, fill with N/A\n"
if(checkFormat(pattern_phone_number, employment_present['Phone']) == False):
    report_text += "Phone number format is not correct, Please input again.\n\n"
if not spell_check(employment_present["Reason for Leaving"]):
    report_text += "Reason for Leaving spelling is not correct\n"
if employment_present["Reason for Leaving"]=="":
    report_text += "Reason for Leaving is blank, please fill the filed"

report_text+= end_line

# Unemployment / Furlough
print("Processing Unemployment / Furlough...")

report_text+= "Unemployment / Furlough\n\n"
unemployment_furlough = data["UnemploymentFurlough"]
emfu_history = unemployment_furlough["History"]
emfu_details = unemployment_furlough["Details"]

for item in emfu_history:
    n=1
    d_from = item["From"]
    d_type = item["Type"]
    d_desc = item["Description"]
    if d_type == "":
        report_text += f"The {n}th Type is blank, please insert correct type\n"
    if spell_check(d_desc)==False:
        report_text += f"The {n}th Description spelling is not correct\n"
    n=n+1

if emfu_details in ["N/A",""]:
    if len(emfu_history)!=0:
        report_text+="Unemployment Details can be N/A only if there is no unemployment\n"
    else:
        report_text += f"Please remove {emfu_details} Unemployment Details and insert summary of all periods unemployments\n"
report_text += end_line

# Employment Misc
print("Processing Employment Misc...")

report_text+= "Employment Misc\n\n"
employment_misc = data["Employment Misc"]
if "" in list(employment_misc.values()):
    report_text += "All items should not be blank and if blank, insert N/A please\n"
for key in employment_misc.keys():
    if not spell_check(employment_misc[key]):
        report_text += f"{key} value spelling is not correct\n"
report_text += end_line

# Pilot Experience General
print("Processing Pilot Experience General...")

report_text += "Pilot Experience General\n\n"
pilot_experience_general = data["Pilot Experience General"]
err =False
for value in pilot_experience_general.values():
    if not value in ["Yes", "No"]:
        err = True
if err:
    report_text += "All items should not be blank and if blank, insert N/A please\n"

report_text += end_line

# Pilot Certificates Ratings
print("Processing Pilot Certificates Ratings...")

report_text += "Pilot Certificates Ratings\n\n"
pilot_certificates_ratings = data["Pilot Certificates Ratings"]
if "" in list(pilot_certificates_ratings.values()):
    report_text += "No blanks allowed for entire sections\n"

if not pilot_certificates_ratings["Cert. Number"].isdigit():
    report_text += "Cert Number allows only numbers\n"
if (datetime.strptime(pilot_certificates_ratings["Issue Date"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
    report_text += "Issue Date is not past\n"
if not pilot_certificates_ratings["Flight Engineer Cert. Number"] in ["","N/A"]:
    report_text += "Flight Engineer Cert. Number should not be blank\n"
if pilot_certificates_ratings["Flight Engineer Issue Date"] != "":
    report_text += "Flight Engineer Issue Date should be blank\n"
if pilot_certificates_ratings["Flight Engineer FE Turbojet"] == "":
    report_text += "Flight Engineer FE Turbojet is blank, Please insert No in that case\n"
if pilot_certificates_ratings["Flight Engineer FE Reciprocating"] == "":
    report_text += "Flight Engineer FE Reciprocating is blank, Please insert No in that case\n"
if pilot_certificates_ratings["Flight Engineer FE Turboprop"] == "":
    report_text += "Flight Engineer FE Turboprop is blank, Please insert No in that case\n"
if pilot_certificates_ratings["Airplane SEL"]=="No" or not pilot_certificates_ratings["Airplane SEL"] in ["Yes, No"]:
    report_text += "Caution! Please check Airplane SEL information is correct. It should be Yes or No\n"
if pilot_certificates_ratings["Airplane MEL"]=="No" or not pilot_certificates_ratings["Airplane MEL"] in ["Yes, No"]:
    report_text += "Caution! Please check Airplane MEL information is correct. It should be Yes or No\n"
if not pilot_certificates_ratings["Airplane SES"] in ["Yes, No"]:
    report_text += "Airplane SES information should be Yes or No\n"
if not pilot_certificates_ratings["Airplane MES"] in ["Yes, No"]:
    report_text += "Airplane MES information should be Yes or No\n"

if pilot_certificates_ratings["Rotor Helicopter"]=="" or not pilot_certificates_ratings["Rotor Helicopter"] in ["Yes, No"]:
    report_text += "Rotor Helicopter information should be Yes or No\n"
if pilot_certificates_ratings["Rotor Gyroplane"]=="" or not pilot_certificates_ratings["Rotor Gyroplane"] in ["Yes, No"]:
    report_text += "Rotor Gyroplane information should be Yes or No\n"
if pilot_certificates_ratings["Airship"]=="" or not pilot_certificates_ratings["Airship"] in ["Yes, No"]:
    report_text += "Airship information should be Yes or No\n"
if pilot_certificates_ratings["Balloon"]=="" or not pilot_certificates_ratings["Balloon"] in ["Yes, No"]:
    report_text += "Balloon information should be Yes or No\n"
if pilot_certificates_ratings["Powered Lift"]=="" or not pilot_certificates_ratings["Powered Lift"] in ["Yes, No"]:
    report_text += "Powered Lift information should be Yes or No\n"
if pilot_certificates_ratings["Glider"]=="" or not pilot_certificates_ratings["Glider"] in ["Yes, No"]:
    report_text += "Glider information should be Yes or No\n"

if not pilot_certificates_ratings["Turbojet Typed"] in ["Yes, No"]:
    report_text += "Turbojet Typed information should be Yes or No\n"

if not pilot_certificates_ratings["B-737 Typed"] in ["Yes, No"]:
    report_text += "B-737 Typed information should be Yes or No\n"

if not pilot_certificates_ratings["Large Aircraft Typed"] in ["Yes, No"]:
    report_text += "Large Aircraft Typed information should be Yes or No\n"

if not pilot_certificates_ratings["Instrument Airplane"] in ["Yes, No"]:
    report_text += "Instrument Airplane information should be Yes or No\n"

if not pilot_certificates_ratings["Instrument Airplane"] in ["Yes, No"]:
    report_text += "Instrument Airplane information should be Yes or No\n"

if pilot_certificates_ratings["Instrument Airplane"] == "No":
    report_text += "Caution! Please make sure Instrument Airplane answer is correct\n"

if not pilot_certificates_ratings["Instrument Helicopter"] in ["Yes, No"]:
    report_text += "Instrument Helicopter information should be Yes or No\n"

if not pilot_certificates_ratings["Instrument Helicopter"] in ["Yes, No"]:
    report_text += "Instrument Helicopter information should be Yes or No\n"

if not pilot_certificates_ratings["Instrument Powered Lift"] in ["Yes, No"]:
    report_text += "Instrument Powered Lift information should be Yes or No\n"

report_text += end_line

# Instructor Certificates Ratings
print("Processing Instructor Certificates Ratings...")

report_text += "Instructor Certificates Ratings\n\n"
pilot_certificates_ratings = data["Instructor Certificates Ratings"]


if pilot_certificates_ratings["Flight Instructor"]=="":
    report_text += "Flight Instructor should be N/A if blank\n"
elif not pilot_certificates_ratings["Flight Instructor"]=="N/A" and not pilot_certificates_ratings["Flight Instructor"].isdigit():
    report_text += "Flight Instructor should be nubers only\n"
if pilot_certificates_ratings["Flight Instructor Issue Date"]!="":
    if (datetime.strptime(pilot_certificates_ratings["Flight Instructor Issue Date"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
        report_text += "Flight Instrutor Issue Date is not correct\n"

if pilot_certificates_ratings["Ground School"]=="":
    report_text += "Ground School should be N/A if blank\n"
elif not pilot_certificates_ratings["Ground School"]=="N/A" and not pilot_certificates_ratings["Ground School"].isdigit():
    report_text += "Ground School should be nubers only\n"

if pilot_certificates_ratings["Ground School Issue Date"]!="":
    if (datetime.strptime(pilot_certificates_ratings["Ground School Issue Date"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
        report_text += "Ground School Issue Date is not correct\n"
for key in pilot_certificates_ratings.keys():
    if "Flight Instructor" in key or "Ground School" in key:
        continue
    if pilot_certificates_ratings[key] == "":
        report_text += f"{key} value is blank, please insert the field\n"
    elif not pilot_certificates_ratings[key] in ["Yes", "No"]:
        report_text += f"{key} value is not valid, it should be Yes/No\n"

report_text += end_line

# FAA Written Tests
print("Processing FAA Written Tests...")
report_text += "FAA Written Tests\n\n"
FAA_Written_Tests = data["FAA Written Tests"]
if (datetime.strptime(FAA_Written_Tests["ATPDate"], '%m/%d/%Y')-datetime.now()).total_seconds()>0:
    report_text += "ATP Date is not correct\n"
for key in FAA_Written_Tests.keys():
    # print(key)
    if "Current" in key:
        if not FAA_Written_Tests[key] in ["Yes", "No"]:
            report_text += f"{key} value should be Yes or No, please insert correct answer\n"
report_text += end_line


# FAA Medicals
print("Processing FAA Medicals...")
report_text += "FAA Medicals\n\n"
FAA_Medicals = data["FAA Medicals"]
if FAA_Medicals["Class"]=="":
    report_text += "Make sure Class information is accurate. If you do not hold a First Class Medical we highly recommend obtaining it before publishing your application\n"
total_days = timedelta(days = 0)
total_days += datetime.strptime(FAA_Medicals["Issued"], '%m/%d/%Y')-datetime.now()
if total_days.days < 0:
    report_text += "Issued Date was expired\n"
elif total_days.days() < 90:
    report_text += "Your medical will be expired within the next 90 days\n"
if FAA_Medicals["Restrictions"] == "":
    report_text += "If you do not have any restriction plan insert None and if you have any restriction place restriction that are on your medical in Restrictions section\n"

report_text += end_line

# Misc Certificates
print("Processing Misc Certificates...")
report_text += "Misc Certificates\n\n"
Misc_Certificates = data["Misc Certificates"]
if not Misc_Certificates["Dispatcher"] in ["Yes", "No"]:
    report_text += "Dispatcher should be Yes or No\n"
if not Misc_Certificates["Airframe&Powerplant"] in ["Yes", "No"]:
    report_text += "Airframe & Powerplant should be Yes or No\n"
if not Misc_Certificates["FCCPermit"] in ["Yes", "No"]:
    report_text += "FCCPermit should be Yes or No\n"
report_text += end_line

# FAA Actions
print("Processing FAA Actions...")
report_text += "FAA Actions\n\n"
FAA_Actions = data["FAA Actions"]
for key in FAA_Actions.keys():
    if key != "Details":
        if not FAA_Actions[key] in ["Yes", "No"]:
            report_text += f"{key} section should be Yes or No\n"
if FAA_Actions["Details"] == "" or FAA_Actions["Details"] == "N/A":
    if "Yes" in FAA_Actions.values():
        report_text +="Details should be provided\n"
    else:
        if FAA_Actions["Details"] == "":
            report_text +="Details should be N/A if blank\n"

report_text += end_line


# Aircraft Flown
print("Processing Aircraft Flown...")
report_text += "Aircraft Flown\n\n"
Aircraft_Flown = data["Aircraft Flown"]
for item in Aircraft_Flown:
    model = item["Model"]
    lastflown = item["LastFlown"]
    total_days = timedelta(days = 0)
    total_days += datetime.now()-datetime.strptime(lastflown, '%m/%Y')
    if total_days.days>90:
        report_text +=f"Caution for {model}! Please make sure your last flown date is correct. The information you provided is indicating that you have not flown within the last 90days\n\n"
report_text += end_line

# Addendum
print("Processing Addendum...")
report_text += "Addendum\n\n"
Addendum = data["Addendum"]
for item in Addendum:

    question = item["question"]
    answer = item["answer"]
    if "flight time have you logged in" in question or "If yes" in question:
        if answer=="":
            report_text += f"{question}\nYou have to insert explanation for this question\n\n"
    else:
        if not answer in ["Yes", "No"]:
            report_text += f"{question}\nAnswer to this question should be Yes or No\n\n"
        else:
            if "convicted of any felony" in question and answer=="No":
                report_text+=f"{question}\nPlease make sure answer for this question is correct. This goes beyond the previous ten years period. This only applies to convictions\n\n"
            if "ever failed ANY checkrides" in question and answer == "No":
                report_text += f"{question}\nPlease make sure answer for this question is accurate. This includes any Part 61/141 stage checks, UPT stage checks/check rides or failures to include Form 8 Checkrides\n\n"
            if "I acknowledge that I have" in question and answer == "No":
                report_text += f"{question}\nPlease make sure answer for this question is correct\n\n"
report_text += end_line


# GeneralReferences
print("Processing GeneralReferences...")
report_text += "GeneralReferences\n\n"
GeneralReferences = data["GeneralReferences"]
if len(GeneralReferences)<3:
    report_text +="You must include 3 entries at a minimum"
span_days = []
span_10_years = False

for item in GeneralReferences:
    from_date = item["From"]
    to_date = item["To"]
    phone_number = item["PhoneNumber"]
    email_address = item["EmailAddress"]
    total_days = timedelta(days = 0)
    if "Present" in to_date:
        total_days += datetime.now()-datetime.strptime(from_date, '%m/%d/%Y')
    else:
        total_days += datetime.strptime(to_date, '%m/%d/%Y')-datetime.strptime(from_date, '%m/%d/%Y')
    span_days.append(total_days.days)
    if total_days.days>3650:
        span_10_years = True
    if checkFormat(pattern_phone_number, phone_number) == False:
        report_text +=f"Phone number {phone_number} is not correct format. Please insert write format e.g. 601-209-5505\n"
    if checkFormat(pattern_email, email_address) == False:
        report_text +=f"Email address {email_address} is not correct format. Please insert write format e.g. 601-209-5505\n"
if span_10_years:
    report_text +="Caution! You need at least one reference that has known you for at least 10 years\n"
report_text += end_line

# Transportation Security Regulation Disclosure
print("Processing Transportation Security Regulation Disclosure...")
report_text += "Transportation Security Regulation Disclosure\n\n"
Disclosure_Answer = data["Disclosure Answer"]
if Disclosure_Answer == "Yes":
    report_text += "Caution! Please check that your Yes answer is correct"
report_text += end_line


report_file.write(report_text)
report_file.close()