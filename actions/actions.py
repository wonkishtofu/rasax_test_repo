# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd

# How does custom action work?
# when the action, action_search_link is aclled, it will map the intent of the message to the list
#of intents in links_template. using pandas, the name of the intent will be map to the corresponding link
#and returned as a message. 
#which part of the dictionary to look for the right intent name depends on whether it is just a normal story or
#following a rule from rule policy. The format of the dictionary is prepared in nlu rule templates.txt

class Action_multiple_utterance(Action):
    def name(self) -> Text:
        return "action_multiple_utterance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #condition to read from different parts if is normal story or if it is the faq rule
        if "faqm/" in tracker.latest_message['response_selector']["default"]["ranking"][0]["intent_response_key"]:
            intent_name=tracker.latest_message['response_selector']["default"]["response"]["intent_response_key"]
        else:
            intent_name=tracker.latest_message["intent"].get("name")
        template=pd.read_csv("'https://raw.githubusercontent.com/wonkishtofu/rasax_test_repo/tree/master/actions/multiple_utterance.csv")
        #template["log"]=intent_name
        #template.to_csv("/Users/User/Desktop/learning/Rasa/test/actions/logs.csv")
        filtered_template=template[template["intent name"]==intent_name]
        message_1=filtered_template["utterance_1"].values[0]
        message_2=filtered_template["utterance_2"].values[0]
        message_3=filtered_template["utterance_3"].values[0]
        try: #condition for replies if there are not links for the given intent".
            dispatcher.utter_message(text= f"{message_1}")
            dispatcher.utter_message(text= f"{message_2}")
            dispatcher.utter_message(text= f"{message_3}")
        except:
            dispatcher.utter_message(text="Sorry, there's something wrong with the way i understood it, please seek other information avenure for this specific question!")
        return []
