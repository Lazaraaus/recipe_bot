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
# Get entity values from messages using tracker.lastest_message['entities']
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
        # Create List for Events
        #events = []
        # Extract url from slots 
        website_url = str(tracker.get_slot('recipe_url'))
        print(website_url)
        
        # Utter Getting Recipe Message
        msg = "Attempting to retrieve and parse the following recipe " + website_url + "\n"
        dispatcher.utter_message(text=msg)
        # Scrape Url For Recipe
        try:
            # Get Recipe Info
            title, ingredients, instructions = scrape(website_url)
            # Set slots
            # events.append(SlotSet("title", title))
            # events.append(SlotSet("ingredients", ingredients))
            # events.append(SlotSet("instructions", instructions))
            # Parse Recipe
            ingr_dict = parseIngredients(ingredients)
            ingrs_list = get_ingredients_from_ingrs_dict(ingr_dict)
            instr_dict = parseInstructions(instructions, ingrs_list)
            # Set Slots
            # events.append(SlotSet("ingr_dict", ingr_dict))
            # events.append(SlotSet("instr_dict", instr_dict))
            # events.append(SlotSet("step_number", 1))

            # Utter Success Message
            msg = title + " retrieved and parsed.\n" + "What would you like to do next?"
            print(instructions)
            dispatcher.utter_message(text=msg)
            # Return SlotSet Events
            return [SlotSet("instructions", instructions), SlotSet("ingredients", ingredients), SlotSet("title", title), SlotSet("ingr_dict", ingr_dict), SlotSet("instr_dict", instr_dict)] 
        except:
            # Utter Failure Message
            msg = "Url failed, please check and try again"
            dispatcher.utter_message(text=msg)
            return []


# Some class for Displaying All Steps
class ActionDisplayAllSteps(Action):

    def name(self) -> Text:
        return "action_display_all_steps"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        instructions = tracker.get_slot("instructions")
        print(instructions)
        # ARE WE DOING TRNASFORMATIONS? IF NOT THIS SEEMS SO TRIVIAL ALMOST

        msg = ""
        for i, instr in enumerate(instructions):
            msg += "Step {}: {}\n".format(i + 1, instr)
        dispatcher.utter_message(text=msg)
        return []

# Some class for Display Next Step
class ActionDisplayIngredients(Action):

    def name(self) -> Text:
        return "action_display_ingredients"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        ingredients = tracker.get_slot("ingredients")
        print(ingredients)

        msg = ""
        for ingr in ingredients:
            msg += "- {}\n".format(ingr)
        dispatcher.utter_message(text=msg)
        return []

class ActionDisplayCurrentStep(Action):

    def name(self) -> Text:
        return "action_display_current_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        step = tracker.get_slot("step_number")
        instructions = tracker.get_slot("instructions")
        ingr_dict = tracker.get_slot("ingr_dict")
        instr_dict = tracker.get_slot("instr_dict")
        print(ingr_dict)
        print(instr_dict)
        print(step)
        print(instructions)
        msg = "Step {}: {}\n".format(step, instructions[step - 1])
        dispatcher.utter_message(text=msg)
        return []

# MACEY NOTE: These should have some way to tell a person when they're at the beginning/end of the list

class ActionDisplayNextStep(Action):

    def name(self) -> Text:
        return "action_display_next_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        step = tracker.get_slot("step_number")
        instructions = tracker.get_slot("instructions")

        try:
            msg = "Step {}: {}\n".format(step, instructions[step])
            dispatcher.utter_message(text=msg)
            if step < len(instructions): 
                return [SlotSet("step_number", step + 1)]
        except:
            pass

class ActionDisplayPreviousStep(Action):

    def name(self) -> Text:
        return "action_display_previous_step"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        step = tracker.get_slot("step_number")
        instructions = tracker.get_slot("instructions")

        try:
            msg = "Step {}: {}\n".format(step, instructions[step - 2])
            dispatcher.utter_message(text=msg)
            if step > 1:
                return [SlotSet("step_number", step - 1)]
        except:
            pass


class ActionAnswerHowToQuery(Action):

    def name(self) -> Text:
        return "action_answer_how_to_query"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        print("how")
        
        question = " ".join(tracker.latest_message["text"].lower().split())
        pre_phrases = ["how do i ", "i do not know how to ", "i don't know how to ", "i dont know how to ", "idk how to ", "how to ",
        "i do not know how ", "i don't know how ", "i dont know how ", "idk how ", "how "]
        sub_phrases = ["do that", "do this", "do it", "that", "this", "it"]
        post_phrases = [" work", " works"]
        is_parsed = False

        for p in pre_phrases:
            if question[:len(p)] == p:
                question = question[len(p):]
                is_parsed = True
                break
        for p in post_phrases:
            if question[-len(p):] == p:
                question = question[:-len(p)]
                is_parsed = True
                break
        for p in sub_phrases:
            if p in question:
                break
        
        q = "+".join(question.split())
        url = "google.com/search?q="
        if is_parsed:
            url += "how+to+"
        msg = "Here's a link that might help:\n\t{}{}\n".format(url, q)
        print(tracker.get_slot("instr_dict"))
        print(tracker.get_slot("ingr_dict"))

        dispatcher.utter_message(text=msg)
        return []
        
class ActionAnswerWhatIsQuery(Action):

    def name(self) -> Text:
        return "action_answer_what_is_query"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        print("what")
        
        question = " ".join(tracker.latest_message["text"].lower().split())
        pre_phrases = ["what is ", "what's ", "whats ", "define ", "definition ", "definition of ", "what do ", "what does ", "what does a ", "what does it mean ",
        "what does it mean to ", "whats it mean to ", "whats it mean ", "what's it mean to ", "whats it mean to ", "what's the meaning ", "whats the meaning ",
        "what's the meaning of ", "whats the meaning of ", "what's the meaning to ", "whats the meaning to ", "meaning ", "what it means ", "what it means to "
        "i do not know what ", "i don't know what ", "i dont know what ", "idk what "]
        post_phrases = [" is", " are", " definition", " means", " do", " does"]
        sub_phrases = ["that", "this", "it"]
        is_parsed = False

        for p in pre_phrases:
            if question[:len(p)] == p:
                question = question[len(p):]
                is_parsed = True
                break
        for p in post_phrases:
            if question[-len(p):] == p:
                question = question[:-len(p)]
                is_parsed = True
                break
        for p in sub_phrases:
            if p in question:
                break
        
        q = "+".join(question.split())
        url = "google.com/search?q="
        if is_parsed:
            url += "what+is+"
        msg = "Here's a link that might help:\n\t{}{}\n".format(url, q)
        print(tracker.get_slot("instr_dict"))
        print(tracker.get_slot("ingr_dict"))

        dispatcher.utter_message(text=msg)
        return []

class ActionGoToStep(Action):
    def name(self) -> Text:
        return "action_go_to_step"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:       
        step = tracker.get_slot("step_number")
        instructions = tracker.get_slot("instructions")
        print(step)
        try:
            msg = "Step {}: {}\n".format(step, instructions[step - 1])
            dispatcher.utter_message(text=msg)
            if step > 1:    
                return [SlotSet("step_number", step - 1)]
        except:
            pass
# Etc, Etc 

"""
    title = tracker.get_slot("title")
    ingredients = tracker.get_slot("ingredients")
    instructions = tracker.get_slot("instructions")
    ingr_dict = tracker.get_slot("ingr_dict")
    instr_dict = tracker.get_slot("instr_dict")
"""