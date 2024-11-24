import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker  # Corrected import for Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet  # Import SlotSet to set slot values
import sqlite3
import os
print("Current working directory:", os.getcwd())

class ActionAskForNameAndID(Action):
    def name(self) -> Text:
        return "action_ask_for_name_and_id"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Could you please provide your name and personal ID?")
        return []

class ActionStoreNameAndID(Action):
    def name(self) -> Text:
        return "action_store_name_and_id"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Retrieve the name and personal_id from the tracker
        name = tracker.get_slot("name")
        personal_id = tracker.get_slot("personal_id")
        print(name,personal_id)
        # Check if the name and personal_id are valid
        if name and personal_id:
            dispatcher.utter_message(text=f"Thank you, {name}. Your ID is {personal_id}.")
            
            import os
            current_directory = os.path.dirname(os.path.abspath(__file__))
            print("cuuuuuuuuuuuuuuuuuurrrrr", current_directory)
            db_path = os.path.join(current_directory, 'appointments.db')

            # Connect to the database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Insert the name and personal ID into the 'users' table
            try:
                cursor.execute("INSERT INTO users (name, personal_id) VALUES (?, ?)", (name, personal_id))
                conn.commit()
                dispatcher.utter_message(text="Your details have been saved!")
            except sqlite3.IntegrityError as e:
                dispatcher.utter_message(text=f"Error saving your details: {str(e)}")
            finally:
                conn.close()

            return [SlotSet("name", name), SlotSet("personal_id", personal_id)]
        else:
            dispatcher.utter_message(text="Please provide both your name and personal ID.")
            return []

        # Get the absolute path to the database
        

class ActionSuggestRandomDate(Action):
    def name(self) -> Text:
        return "action_suggest_random_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Suggest a random date from available slots
        import os
        current_directory = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_directory, 'appointments.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM appointments WHERE status = 'available'")
        available_dates = cursor.fetchall()
        conn.close()
        
        if available_dates:
            random_date = random.choice(available_dates)[0]
            print("slotset data",random_date)
            dispatcher.utter_message(text=f"How about {random_date}? Would you like to book it?")
            return [SlotSet("selected_date", random_date)]  # <-- Use SlotSet here to set the selected_date slot
        else:
            dispatcher.utter_message(text="I'm sorry, I couldn't find any available slots.")
            return []

class ActionBookDate(Action):
    def name(self) -> Text:
        return "action_book_date"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        selected_date = tracker.get_slot("selected_date")
        name = tracker.get_slot("name")
        personal_id = tracker.get_slot("personal_id")

        import os
        current_directory = os.path.dirname(os.path.abspath(__file__))
        print("inside_book", selected_date,name)
        db_path = os.path.join(current_directory, 'appointments.db')

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Book the appointment in the database
        # conn = sqlite3.connect('appointments.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = 'booked', name = ?, personal_id = ? WHERE date = ? AND status = 'available'", 
                       (name, personal_id, selected_date))
        print("hello",name)
        conn.commit()
        conn.close()

        dispatcher.utter_message(text="Your appointment has been successfully booked!")
        return []

class ActionAskForSpecificDay(Action):
    def name(self) -> Text:
        return "action_ask_for_specific_day"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="Can you tell me a specific date you're interested in?")
        return []

class ActionProvideAvailableDates(Action):
    def name(self) -> Text:
        return "action_provide_available_dates"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Provide 3 available dates
        conn = sqlite3.connect('appointments.db')
        cursor = conn.cursor()
        cursor.execute("SELECT date FROM appointments WHERE status = 'available' LIMIT 3")
        available_dates = cursor.fetchall()
        conn.close()

        if available_dates:
            dates = [date for date in available_dates]
            dispatcher.utter_message(text=f"Here are some available dates for you: {', '.join(dates)}")
            return [SlotSet("available_dates", dates)]  # <-- Use SlotSet here to set available_dates slot
        else:
            dispatcher.utter_message(text="Sorry, no available dates at the moment.")
            return []
