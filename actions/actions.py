# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import datetime as dt
import numpy as np 
import pandas as pd
from pyowm import OWM #weather API
import random

import scholarly

key_weather = "9f6f77317e172b4aed01498eefd4ee96"
df = pd.read_excel("Data_Teachers.xlsx")
df.rename(columns={"Unnamed: 3": "Building", "NOMBRE": "Professor", "GRUPO ": "Department", "DESPACHO": "Room"}, inplace=True)
df['Building'] = df['Building'].fillna("Unknown")
df.dropna(axis=0, inplace=True)

#Subtract professors for possible slot values later
#Part 1 DF Creation
out=df['Professor'].str.split(', ',expand=True)
df['Professor_First_Name']=out[1]
#df['Professor_Last_Name']=out[0].str.split(' ').str[0]
df['Professor_Last_Name'] = out[0]
df['Professor_First_Last_Name'] = df['Professor_First_Name'] +" "+ df['Professor_Last_Name']
df['Professor_Last_First_Name'] = df['Professor_Last_Name'] +" "+ df['Professor_First_Name']
df

#Part 2 DF to list
professors = []
professors = np.append(professors, df['Professor_First_Name'].values)
professors = np.append(professors, df['Professor_Last_Name'].values)
professors = np.append(professors, df['Professor_First_Last_Name'].values)
professors = np.append(professors, df['Professor_Last_First_Name'].values)
professors_list = list(professors)
professors_list = [x for x in professors_list if str(x) != 'nan']
for i in range(len(professors_list)):
    professors_list[i] = str(professors_list[i]).lower()
professors_list[:5]

possible_rooms = str(df.Room.unique())
df['Room_with_Dot'] = (df.Room.astype(str).str[:2]+ '.'+ df.Room.astype(str).str[-2:])
possible_rooms = np.append(possible_rooms, df['Room_with_Dot'].values)

departments = df.Department.unique()
out=df['Department'].str.split(': ',expand=True)
df['Department_Full']=out[1]
#df['Professor_Last_Name']=out[0].str.split(' ').str[0]
df['Department_Short'] = out[0]
departments = np.append(departments, df['Department_Full'].values)
departments = np.append(departments, df['Department_Short'].values)

Buildings = df.Building.unique()



class ProfessorCollaboratorsAction(Action):
    def name(self) -> Text:
        return "action_professor_collaborators"


    def get_professor_info(name):
            # look up professor by name
            professor = df.loc[df['Name'] == name]

            if professor.empty:
                # professor not found
                return {'error': 'Professor not found'}

            # extract information
            department = professor['Department'].iloc[0]
            office = professor['Office'].iloc[0]
            # add more fields as needed

            # return information as a dictionary
            return {'department': department, 'office': office}


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        df = pd.read_csv('Data_Teachers.csv')
              

        # Get the professor's name from the user input
       
        prof =  tracker.get_slot("professor")
        if not prof:
            message =f"I did not get the professor correctly. I have information about the following proffesors: {df['Professor_First_Last_Name'].values}."
       
        a = np.array((2))

        (b,c) = self.get_professor_info(prof)
        print("Hey, department is",b,"and office is", c)


        # Find the professor in the dataframe
        professor = df.loc[df['Name'] == prof]
        
        if len(professor) == 0:
            # If professor not found in the dataframe, return an error message
            dispatcher.utter_message(text=f"Sorry, I could not find any professor with the name {prof}.")
        else:
            # Retrieve the collaborators of the professor from Google Scholar
            search_query = scholarly.search_author(prof)
            author = next(search_query).fill()
            collaborators = [c.name for c in author.coauthors]
            
            # Find other professors in the dataframe and compare their collaborators with the selected professor's collaborators
            other_professors = df.loc[df['Name'] != prof]
            common_collaborators = set(collaborators)
            for index, row in other_professors.iterrows():
                search_query = scholarly.search_author(row['Name'])
                author = next(search_query).fill()
                other_collaborators = [c.name for c in author.coauthors]
                common_collaborators = common_collaborators.intersection(other_collaborators)
            
            # If there are common collaborators, return their names
            if len(common_collaborators) > 0:
                message = f"The common collaborators of {prof} with other professors are: "
                message += ', '.join(list(common_collaborators))
                dispatcher.utter_message(text=message)
            else:
                # If there are no common collaborators, return a message saying so
                dispatcher.utter_message(text=f"There are no common collaborators of {prof} with other professors.")
        
        return []


class ActionHelloWorld(Action):

        def name(self) -> Text:
            return "action_hello_world"

        def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

                dispatcher.utter_message(text="Hello World!")

                return []
        
class ActionHelloWorld(Action):
#
        def name(self) -> Text:
            return "action_give_time"
#
        def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
                dispatcher.utter_message(text=f"{dt.datetime.now()}")
#
                return []
        
class ActionHelloWorld(Action):
#
        def name(self) -> Text:
            return "action_department_professor"
#
        def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                prof =  tracker.get_slot("professor")
                if not prof:
                      message =f"I did not get the professor correctly. I have information about the following proffesors: {df['Professor_First_Last_Name'].values}."
                cols = ['Professor','Professor_First_Name','Professor_First_Last_Name','Professor_Last_First_Name','Professor_Last_Name']
                test_df = df.loc[(df[cols]==prof.upper()).any(axis="columns")]
                if len(test_df) ==1:
                    department = test_df['Department']
                    message = f"Professor {test_df['Professor_First_Last_Name']} is in the {department} department."
                else:
                    message = f"Sorry, but I could not find the department of {prof}. I only have then information of the department of the following professors: {df['Professor_First_Last_Name'].values}."      
                dispatcher.utter_message(text=message)
#
                return []
        
class ActionHelloWorld(Action):

     def name(self) -> Text:
         return "action_ask_weather"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                location =  tracker.get_slot("location")
                location = "Barcelona"
                owm = OWM(key_weather)
                mgr =owm.weather_manager()
                observation = mgr.weather_at_place(location)
                w = observation.weather
                mess1= f"Weather of {location} is:"
                mess2= f"Temperature is {w.temperature('celsius')['temp']}"
                mess3= f"wind speed is: {w.wind()['speed']}Km/h"
                mess4= f"Humidity in {location} is: {w.humidity}%"
                mess5= f"Overall Weather status is: {w.detailed_status}."

                message = mess1 + '\n' + mess2 + '\n' +  mess3 + '\n' + mess4 + '\n' + mess5
                dispatcher.utter_message(text=message)

                return []
     
class ActionHelloWorld(Action):
#
        def name(self) -> Text:
            return "action_fun_fact"
#
        def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
                fun_facts = ["Niels his father is a farmer!"]
                fun_fact = random.choice(fun_facts)
                dispatcher.utter_message(text=f"{fun_fact}")
#
                return []