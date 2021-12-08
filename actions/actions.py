# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


#This is a simple example for a custom action which utters "Hello World!"
from scrape import scrape
from parse import parseIngredients, parseInstructions
from parser import get_ingredients_from_ingrs_dict
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

############################
#       Important Bits     #
############################
# utter messages w/ dispatcher.utter_message()
# Get slot values w/ tracker.current_slot_values()
# Set a slot w/ SlotSet()
# Get entity values from messages using tracker.lastest_message['entities]
# Realized we can store the current step as an int in a slot, starts at 0
# We can change the slot every time we advance or recede. 
# I think I need to split the query action into two distinct queries: What something is and how to perform some action
# Honestly if we had time I'd suggest writing a class to manage a recipe and importing it here. Let that keep track of
# the state. 

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


# Some Class for geting recipes
class ActionGetRecipe(Action):
    # name func
    def name(self) -> Text:
        return "action_get_recipe"
    # run func 
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:

        # Extract url from slots 
        website_url = str(tracker.get_slot('website_url'))
        
        # Utter Getting Recipe Message
        msg = "Attempting to retrieve and parse recipe\n"
        dispatcher.utter_message(text=msg)
        # Scrape Url For Recipe
        try:
            # Get Recipe Info
            title, ingredients, instructions = scrape(website_url)
            # Set slots
            SlotSet("title", title)
            SlotSet("ingredients", ingredients)
            SlotSet("instructions", instructions)
            # Parse Recipe
            ingr_dict = parseIngredients(ingredients)
            ingrs_list = get_ingredients_from_ingrs_dict(ingr_dict)
            instr_dict = parseInstructions(instructions, ingrs_list)
            # Set Slots
            SlotSet("ingr_dict", ingr_dict)
            SlotSet("instr_dict", instr_dict)

            # Utter Success Message
            msg = title + " retrieved and parsed.\n" + "What would you like to do next?"
            dispatcher.utter_message(text=msg)
            return [] 
        except:
            # Utter Failure Message
            msg = "Url failed, please check and try again"
            dispatcher.utter_message(text=msg)
            return []


# Some class for Displaying All Steps

# Some class for Display Next Step

# Etc, Etc 