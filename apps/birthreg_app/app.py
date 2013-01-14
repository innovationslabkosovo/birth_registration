#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
import rapidsms
import re, random
from birthreg.models import *
from datetime import datetime
from django.db import connection, transaction
from sys import exit




class App (rapidsms.apps.base.AppBase):

    # Regular expression patterns 
    fullcase_pattern = re.compile(r'^\d{1,3}\s[a-z]{1,25}\s[a-z\.]{1,25}\s([0-9]{4}[mMfF]{1}[1-6]{1}\s)+[a-z\.0-9]{1,30}$',re.IGNORECASE) # match a complete case
    newcase_pattern = re.compile(r'^\d{1,3}\s([a-z\.]{1,25})+', re.IGNORECASE) # pattern to add a new case
    editcase_pattern = re.compile(r'^[0-9]{3}\s[0-9]{4}', re.IGNORECASE) # pattern to edit a case
    village_pattern =  re.compile(r'^[0-9]{0,2}[A-Za-z\.]{2,30}$', re.IGNORECASE) # pattern to match village string
    name_pattern = re.compile(r'[a-z]{1,25}$', re.IGNORECASE) # pattern to match first name string
    surname_pattern = re.compile(r'^[a-z\.]{1,25}$', re.IGNORECASE) # pattern to match last name string
    details_pattern = re.compile(r'^[12]{1}[09]{1}[019]{1}[0-9]{1}[mMfF]{1}[1-6]{1}$', re.IGNORECASE) #pattern to match child details string
    assume_details_pattern = re.compile(r'^[0-9]+[A-Za-z\.-]+[1-9]+$', re.IGNORECASE) # pattern 
    regular_pattern = re.compile(r'([0-9]+)([a-z]+)$', re.IGNORECASE) $ # pattern to match alphanumeric chars
    fullname_patterns = [name_pattern, surname_pattern]

    

    def start (self):
        """Configure your app in the start phase."""
        pass

    def parse (self, message):
        """Parse and annotate messages in the parse phase."""
        pass

    def handle (self, message):
        fullname = ["",""]
        all_errors=[]
        birthDetails = []
        pinError = 0
        number_children = 0
        completeMerge = 0
        countSuccess = 0        
        count = 0
        birthCount = 0
        villageName = ""
        village = ""
        language_attr = {"Shqip":{"name":"Emri i prindit","surname":"Mbiemri i prindit", "child":"Femiu", "village":"Fshati", "field":"fushe","fields":"fusha"},"Srpski":{"name":"Ime roditelja","surname":"Prezime roditelja",  "child":"Deca", "village":"Selo", "field":"polje","fields":"polja"}}
        
        
        #match patterns with received text message
        fullcase_pattern = self.fullcase_pattern.findall(message.text)
        newcase_pattern = self.newcase_pattern.findall(message.text)
        editcase_pattern = self.editcase_pattern.findall(message.text)

        #get date and time
        get_time = datetime.utcnow()

        # get phone number, reporter ID and language of the sender
        phone = message.connection.identity
        reporterModel = Reporter.objects.get(phone_number = phone)
        LanguageModel = Language.objects.get(id = reporterModel.language_id)
        reporterID = reporterModel.id

        #split received message into strings and save in items array
        received_message = message.text       
        received_message = re.sub("\s+"," ", received_message).rstrip()
        items = received_message.split(" ")        

      
        # true if fullcase pattern has matched
        if fullcase_pattern:

            #generate unique case number
            case_no = self.generateRandom()
            
            # check if correct PIN entered 
            pin = items[0]
            if str(reporterID) == str(pin):
                pinError = 1

            #go through items and assign child birth details and village 
            for i, item in enumerate(items[3:len(items)]):
                if self.details_pattern.findall(item):
                    birthDetails.append(item)
                elif self.village_pattern.findall(item):
                    village = item


            # if PIN is wrong add information to temporary table 
            if pinError == 0:
                self.insertCase(TempCase,case_no,items[1],items[2],village,len(birthDetails),get_time,"0") 
                self.setBirthDetails(TempCaseDetails,case_no, birthDetails)
                message.respond(LanguageModel.new_pin_error.format(str(case_no)))

            # if PIN is correct add information to case table.
            else:
                self.insertCase(Case,case_no,items[1],items[2],village,len(birthDetails),get_time,reporterID)
                self.setBirthDetails(CaseDetails,case_no, birthDetails)                   
                message.respond(LanguageModel.new_success.format(items[2],str(case_no).capitalize()))

        # true if newcase pattern has matched
        elif newcase_pattern:

            #generate unique case number
            case_no = self.generateRandom()        

            #loop through each item in the message
            for i, item in enumerate(items[0:len(items)]):
               
                # check if correct PIN entered 
                if i == 0:
                    pin = item
                    if str(reporterID) == str(pin):
                        pinError = 1
                    continue

                # check if first and last name patterns are correct
                if i<3:
                    #separate/join mother maiden and last name 
                    if self.checkNames(item, self.fullname_patterns[i-1]):
                        fullname[i-1] = item
                        continue
                    else:
                        all_errors.append("name"+str(i))
                        continue

                # check if birth details pattern is matched
                if self.details_pattern.findall(item):
                    birthDetails.append(item)
                    birthCount +=1
                    continue

               # check for birth details error assumption
                elif self.assume_details_pattern.findall(item):                   
                    all_errors.append(language_attr[LanguageModel.language_name]["child"]+str(birthCount))                    
                    continue
                
                # 
                elif self.village_pattern.findall(item):                    
                    try :
                        if (completeMerge == 1 and self.village_pattern.findall(item)):

                            items = self.remove_values_from_list(items,item)
                            continue
                            
                        try:
                            secondItem=items[i+1]                           
                        except IndexError:
                            secondItem = " "
                            
                        try:                            
                            thirdItem=items[i+2]
                        except IndexError:                          
                            thirdItem = " "

                        count = self.multipleVillages(item,secondItem,thirdItem,self.village_pattern)                
                            
                        if count > 1:

                            villageName = items[i]
                            for k in range(2,count+1):
                                villageName += "."+items[i+1]
                                del(items[i])
                                completeMerge = 1
                                countSuccess += 1
                        else:
                            if self.village_pattern.findall(item):
                                villageName = item  
                            
                                
                           # allfields.append(villageName)
                    except  (TypeError,IndexError ):
                            continue
            
            if villageName == "":
                all_errors.append(language_attr[LanguageModel.language_name]["village"])

            if (birthCount == 0):
                message.respond(LanguageModel.new_birthdetails_error)
                return 0

            if (len(all_errors)>2):
                message.respond(LanguageModel.new_three_error)
                return 0

            elif (len(all_errors)>0):
                send_errors = ""
                fusha = language_attr[LanguageModel.language_name]["fields"]
                for errors in all_errors:
                    if errors == "name1":
                        errors = language_attr[LanguageModel.language_name]["name"]
                        
                    if errors == "name2":
                        errors = language_attr[LanguageModel.language_name]["surname"]

                    send_errors += "\n "+errors

                if len(all_errors) == 1:
                    fusha = language_attr[LanguageModel.language_name]["field"]

                self.insertCase(TempCase,case_no, fullname[0],fullname[1],villageName,len(birthDetails),get_time,reporterID)
                self.setBirthDetails(TempCaseDetails,case_no, birthDetails)    

                message.respond(LanguageModel.new_field_error.format(str(len(all_errors)),fusha,str(case_no),send_errors))

            else :

                if pinError == 0:

                    self.insertCase(TempCase,case_no, fullname[0],fullname[1],villageName,len(birthDetails),get_time,"0")
                    self.setBirthDetails(TempCaseDetails,case_no, birthDetails)    

                    message.respond(LanguageModel.edit_pin_error.format(str(case_no)))
                else:
               
                    self.insertCase(Case,case_no, fullname[0],fullname[1],villageName,len(birthDetails),get_time,reporterID)                
                    self.setBirthDetails(CaseDetails,case_no, birthDetails)   
                       
                    message.respond(LanguageModel.new_success.format(fullname[1].capitalize(), str(case_no)))
            
        elif editcase_pattern:
            pin = items[0]
            case_no = items[1]
         
            if str(pin) == str(reporterID):
              
                if TempCase.objects.filter(id = case_no).count():
                    current_case = TempCase.objects.get(id=case_no)
                 #   current_case = chooseCase[activeCase].objects.get(id=case_no)

                    if len(items) == 2:
                        if  current_case.reporter_id == 0:                            

                            current_case.reporter_id = pin
                            current_case.save()
                            self.TempToCase("birthreg_case","birthreg_tempcase","id", case_no)

                            if TempCaseDetails.objects.filter(case = case_no).count():
                                self.TempToCase("birthreg_casedetails","birthreg_tempcasedetails","case_id", case_no)

                            message.respond(LanguageModel.edit_success.format(str(case_no)))

                        else:
                            message.respond(LanguageModel.edit_general_error)
                    else:
                        
                        for i, item in enumerate(items[2:len(items)]):

                            if self.fullcase_pattern.findall(item):
                                birthDetails.append(item)
                                continue

                            editItem = item.split("=")

                            if editItem[0] == "e" or editItem[0] == "E":
                                if self.name_pattern.findall(editItem[1]):
                                    current_case.parent_name = editItem[1]
                                else:
                                    all_errors.append(language_attr[LanguageModel.language_name]["name"])
                              
                            elif editItem[0] == "m" or editItem[0] == "M":
                                if self.surname_pattern.findall(editItem[1]):
                                    current_case.parent_surname = editItem[1]
                                else:
                                    all_errors.append(language_attr[LanguageModel.language_name]["surname"])
                              
                            elif editItem[0] == "f" or editItem[0] == "F":
                                if self.village_pattern.findall(editItem[1]):
                                    current_case.village = editItem[1]
                                else:
                                    all_errors.append(language_attr[LanguageModel.language_name]["village"])
                              

                        if len(all_errors) > 0:
                            message.respond(LanguageModel.edit_field_error.format(str(case_no)))
                            return 0

#                        for item in current_case:
                        if current_case.parent_name == "" or current_case.parent_surname == "" or current_case.village == "":
                            message.respond(LanguageModel.edit_missingfield_error)
                            return 0

                        current_case.save()
                        self.TempToCase("birthreg_case","birthreg_tempcase","id", case_no)

                        if TempCaseDetails.objects.filter(case = case_no).count():
                            self.TempToCase("birthreg_casedetails","birthreg_tempcasedetails","case_id", case_no)

                        if len(birthDetails) > 0:
                            self.setBirthDetails(CaseDetails,case_no, birthDetails)

                        message.respond(LanguageModel.edit_success(str(case_no))) 


                else: 
                    message.respond(LanguageModel.edit_case_error)
                   
            else:
                message.respond(LanguageModel.edit_pin_error)



        else:
            message.respond(LanguageModel.new_general_error)




    def cleanup (self, message):
        """Perform any clean up after all handlers have run in the
           cleanup phase."""
        pass
    def outgoing (self, message):
        """Handle outgoing message notifications."""
        pass

    def stop (self):
        """Perform global app cleanup when the application is stopped."""
        pass

    # Generate case number; check if exists in DB
    def generateRandom(self):
        rand = random.randrange(1000,9999)
        while (Case.objects.filter(id=rand).exists()):
            rand = random.randrange(1000,9999)
        return rand

    def checkNames(self,item, pattern):
        if pattern.findall(item):
            return True
        
    # Return number of strings consisting the village
    def multipleVillages(self,first, second, third ,regex):
        if (regex.findall(first) and regex.findall(second)):
            if regex.findall(third):
                return 3
            else:
                return 2
        else:
            return 1

     # Remove item from list (array)
    def remove_values_from_list(self,the_list, val):
        return [value for value in the_list if value != val ]

    # Insert case to DB.
    def insertCase(self, tb_name, case_no, first_name, last_name, village,  no_children, datetime, reporter_id):
        last_name = re.sub("\.","-",last_name)
        village = re.sub("\."," ",village)
        tb_name(
                    id = case_no,
                    parent_name = first_name.capitalize(),
                    parent_surname = last_name.capitalize(),
                    village = village.capitalize(),
                    number_children = no_children,
                    datetime = datetime,
                    reporter_id = reporter_id).save() 

    # Insert case details for a specific case to DB. 
    def insertCaseDetails(self, tb_name, case_no, birth_year, gender, place):
        tb_name(
                    case_id = case_no,
                    birth_year = birth_year,
                    gender = gender.capitalize(),
                    birthplace_id = place,
                    ).save()
    
    # Copy cases from temporary to actual case table
    def TempToCase(self, source, destination, case_id, case_no):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO "+source+" SELECT * FROM "+destination+" where "+destination+"."+case_id+" = "+case_no )
        cursor.execute("DELETE FROM "+destination+" where "+destination+"."+case_id+" = "+case_no )
        transaction.commit_unless_managed()
      
    # Set child details by spliting details string (2005m2) 
    def setBirthDetails(self, table,case_no, details):
        for row in details:
            year = row[0:4]
            gender = row[4]
            place_id = row[5]
            self.insertCaseDetails(table,case_no,year,gender,place_id)
        

    



#        message.respond('hello world')
