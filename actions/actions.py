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
import json

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

WHAT_PRE_PHRASES = ["what's the meaning to ", "what's the meaning of ", "what's the meaning ", "what's it mean to ", "what's ", "whats the meaning of ", "whats the meaning to ", "whats the meaning ", "whats it mean to ", "whats it mean ", "whats ", "what does it mean to ", "what does it mean ", "what it means to ", "what it means ", "what does a ", "what does ", "what do ", "what is ", "what " "definition of ", "definition ", "define ", "i do not know what ", "i don't know what ", "i dont know what ", "idk what ", "meaning "]
WHAT_POST_PHRASES = [" is", " are", " definition", " means", " does", " do"]
WHAT_SUB_PHRASES = ["that", "this", "it"]

HOW_PRE_PHRASES = ["i do not know how to ", "i do not know how ", "i don't know how to ", "i don't know how ", "i dont know how to ", "i dont know how ", "idk how to ", "idk how ", "how do i ", "how to ", "how "]
HOW_POST_PHRASES = [" works"," work"]
HOW_SUB_PHRASES = ["does that", "does this", "does it", "do that", "do this", "do it", "that", "this", "it"]

QUERY_URL = "google.com/search?q="

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
        if step > len(instructions) + 1:
            msg = "This is the last step, no steps beyond!"
            dispatcher.utter_message(text=msg)
            return []
        try:
            msg = "Step {}: {}\n".format(step + 1, instructions[step])
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
        if step - 1 < 0:
            msg = "This is the first step, no steps before!"
            dispatcher.utter_message(text=msg)
            return []
        try:
            msg = "Step {}: {}\n".format(step - 1, instructions[step - 2])
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
        
        msg = ""
        question = " ".join(tracker.latest_message["text"].lower().split())
        if question[-1] == "?":
            question = question[:-1]
        is_parsed = False
        subs = None

        for p in HOW_PRE_PHRASES:
            if question[:len(p)] == p:
                question = question[len(p):]
                is_parsed = True
                break
        for p in HOW_POST_PHRASES:
            if question[-len(p):] == p:
                question = question[:-len(p)]
                is_parsed = True
                break
        for p in HOW_SUB_PHRASES:
            i = question.find(p)
            if i > -1:
                instr = tracker.get_slot("instr_dict")[str(tracker.get_slot("step_number"))]
                subs = instr["action"]
                if len(subs) == 1:
                    question = question[:i] + subs[0] + question[i + len(subs[0]):]
                    subs = None
                break
        
        if subs is None:
            q = "+".join(question.split())
            msg = "Here's a link that might help:\n\t{}{}\n".format(QUERY_URL + ("how+to+" if is_parsed else ""), q)
        elif len(subs) == 0:
            msg = "I didn't undestand your question. Try asking about a specific ingredient/tool/cooking action you're curious about."
        else:
            msg = "Could you be more specific? Try asking a question like:\n"
            for sub in subs:
                msg += "\tHow to {}?\n".format(sub)

        dispatcher.utter_message(text=msg)
        return []
        
class ActionAnswerWhatIsQuery(Action):

    def name(self) -> Text:
        return "action_answer_what_is_query"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        msg = ""
        question = " ".join(tracker.latest_message["text"].lower().split())
        if question[-1] == "?":
            question = question[:-1]
        is_parsed = False
        subs = None

        for p in WHAT_PRE_PHRASES:
            if question[:len(p)] == p:
                question = question[len(p):]
                is_parsed = True
                break
        for p in WHAT_POST_PHRASES:
            if question[-len(p):] == p:
                question = question[:-len(p)]
                is_parsed = True
                break
        for p in WHAT_SUB_PHRASES:
            i = question.find(p)
            if i > -1:
                instr = tracker.get_slot("instr_dict")[str(tracker.get_slot("step_number"))]
                subs = instr["ingredients"]
                subs.extend(instr["tools"])
                subs.extend(instr["action"])
                if len(subs) == 1:
                    question = question[:i] + subs[0] + question[i + len(subs[0]):]
                    subs = None
                break
        
        if subs is None:
            q = "+".join(question.split())
            msg = "Gotcha. I found a link that might help:\n\t{}{}\n".format(QUERY_URL + ("what+is+" if is_parsed else ""), q)
        elif len(subs) == 0:
            msg = "I didn't undestand your question. Try asking about a specific ingredient/tool/cooking action you're curious about."
        else:
            msg = "Could you be more specific? Try asking a question like:\n"
            for sub in subs:
                msg += "\tWhat is {}?\n".format(sub)

        dispatcher.utter_message(text=msg)
        return []

class ActionGoToStep(Action):
    def name(self) -> Text:
        return "action_go_to_step"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:       
        step = int(tracker.get_slot("step_count"))
        instructions = tracker.get_slot("instructions")
        print(instructions[step - 1])
        #msg_text = f"Step {step}" + instructions[step - 1] + " "
        #print(msg_text)
        print(step)
        try:
            msg = f"Step {step}: {instructions[step - 1]}" 
            dispatcher.utter_message(text=msg)
            return []
        except:
            pass

class ActionTransformIngredient(Action):
    def name(self) -> Text:
        return "action_transform_ingredient"
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text,Any]]: 
        # Get transformation entity
        ingredient = str(tracker.get_slot("transformation"))
        ingredients = tracker.get_slot("ingredients")
        print(ingredient)
        # Load sub dict 
        f = open("subs.json")
        sub_dict = json.load(f)
        f.close()

        flag = False
        # Look for ingr in ingredients
        for ingr_str in ingredients:
            if ingredient in ingr_str:
                flag = True
        if flag == False:
            msg = "Sorry, but I don't think this recipe calls for that ingredient"
            dispatcher.utter_message(text=msg)
            return [SlotSet("transformation", "")]
        elif flag == True:            
            # Check if we have a substitution for the ingredient
            if ingredient in sub_dict.keys():
                amount = sub_dict[ingredient]["amount"]
                substitution = sub_dict[ingredient]["substitution"]
                msg = "We've found a substitution"
                dispatcher.utter_message(text=msg)
                msg = "You can use: \n\t " + substitution + "\nfor \n\t" + amount + "\n of \n\t" + ingredient
                dispatcher.utter_message(text=msg)
                return [SlotSet("transformation", "")]
            else:
                msg = "Sorry, but we don't have a substitution for " + ingredient
                dispatcher.utter_message(text=msg)
                return [SlotSet("transformation", "")]

# Etc, Etc 

"""
    title = tracker.get_slot("title")
    ingredients = tracker.get_slot("ingredients")
    instructions = tracker.get_slot("instructions")
    ingr_dict = tracker.get_slot("ingr_dict")
    instr_dict = tracker.get_slot("instr_dict")
"""