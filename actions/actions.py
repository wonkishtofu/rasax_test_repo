# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
import time
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
import re

# How does custom action work?
# when the action, action_search_link is aclled, it will map the intent of the message to the list
#of intents in links_template. using pandas, the name of the intent will be map to the corresponding link
#and returned as a message. 
#which part of the dictionary to look for the right intent name depends on whether it is just a normal story or
#following a rule from rule policy. The format of the dictionary is prepared in nlu rule templates.txt

class Action_FOM(Action):
    def name(self) -> Text:
        return "action_find_fom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        #condition to read fom expression
        entity_name= tracker.latest_message['entities'][0]["value"]
        template=pd.read_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/FOM.csv")
        #template["log"]=entity_name
        #template.to_csv("/Users/User/Desktop/learning/Rasa/test/actions/logs.csv")

        try: 
            filtered_template=template[template["FOM_no"].str.contains(entity_name, regex=False)]
            #print(entity_name)
            message_1=filtered_template["utterance_1"].values[0]
            dispatcher.utter_message(text= f"{message_1}")
        except:
            dispatcher.utter_message(text="Sorry, there's something wrong with the way i understood it, please seek other information avenure for this specific question!")
        return []
    
class Action_check_items(Action):
    def name(self) -> Text:
        return "action_check_item"
    #to better manage the differenct messages to be send out for different cost
    def total_cost_message(self, cost):     
        Standard_message_1= "Before starting the procedures mentioned below, check if there are existing Demand Aggreagation(DA contracts) that can be used.\n"
        Standard_message_2= "if we are using DA contract check if it is a Period Contract (PC) or Framework Agreement(FA). If it is a PC, no quotes are required as price and scope are already defined in the PC.\n"
        Standard_message_3="However, we will still need to seek approval of expenditure paper and procument approach in accordance with FOM 401.\n" 
        Standard_message_4="If it is a FA, we will need to do a Request for Quotation(RFQ), gain approvals for expenditure paper and procurment approach in accordance to FOM 401 and invite suppliers to subimit quotes for consideration.\n"
        Standard_message_5="Upon evaluation, seek QAA or TAA's approval for the recommendation report in accordance with FOM 510.\n" 
        Standard_message=Standard_message_1+Standard_message_2+Standard_message_3+Standard_message_4+Standard_message_5
        SVP_messages_1="Since it is below $6000, it can be procured through Small Value Purchase(SVP). SVP is for ad-hoc purchases not exceeding $6000.\n"
        SVP_messages_2="For SVP, it is not mandated to obtain 3 quotes, however, we are stil required to consider reasonableness of the price quoted!\n"
        SVP_messages_3="Assessment may be based on verbal or written quotes, recent purchases, suppliers' published rates, or any other source of reliable information (e.g. flyers, Internet,\ newspapers).\n" 
        SVP_messages_4= "We can also use GeBIZ Mall or call quotations through GeBIZ. Remember to seek Department Director's approval of the SVP form!"
        additional_SVP_messages=SVP_messages_1+SVP_messages_2+SVP_messages_3+SVP_messages_4
        ITQ_messages_1="Since it is between $6000 to $90,000, we should procure it using Invitation To Quote (ITQ). It is a tender approach where all suppliers can participate.\n"
        ITQ_messages_2="Competitions can be limited (via limited quotation/tender or direct contracting) if certain conditions are met. Please check IM on procurement: \n"
        ITQ_messages_3="S4 R3.5, S4 R3.6, S4 R12.1 or S4 R12.2. \n Also note to seek approval of the expenditure paper and procurement approach in accordance with FOM 401 \n."
        ITQ_messages_4=" We must also seek the Quotation Approving Authority (QAA's) approval of the quotation report in accordance with FOM 510 after quotation evaluaton before purchase."
        additional_ITQ_messages=Standard_message+ITQ_messages_1+ITQ_messages_2+ITQ_messages_3+ITQ_messages_4
        ITT_messages_1="Since it is between above $90,000, we should procure it using Invitation To Tender (ITT). It is a tender approach where all suppliers can participate.\n"
        ITT_messages_2="Competitions can be limited (via limited quotation/tender or direct contracting) if certain conditions are met. Please check IM on procurement: \n"
        ITT_messages_3="S4 R3.5, S4 R3.6, S4 R12.1 or S4 R12.2. \n Also note to seek approval of the expenditure paper and procurement approach in accordance with FOM 401 \n."
        ITT_messages_4= " We must also seek the Tender Approving Authority (TAA's) approval of the Tender recommendation report in accordance with FOM 510 after tender evaluation before purchase."
        additional_ITT_messages= Standard_message+ITT_messages_1+ITT_messages_2+ITT_messages_3+ITT_messages_4
        if cost<6000:
            return additional_SVP_messages
        elif cost>90000:
            return additional_ITT_messages
        else:
            return additional_ITQ_messages
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #condition on intents
        intent_name=tracker.latest_message["intent"]["name"]
        special_items=pd.read_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/item_list.csv")
        #see if randomly put item is a special item dispatch the appropriate message
        cost_list=[]
        #additional messages to follow guide
#check the buy item and item cost converstaion flow.
        pax=0
        cost=0
        try:
            if intent_name != "open_buy_item":
                for dic in tracker.latest_message['entities']:
                    if dic["entity"]=="items":
                        item=dic["value"]
                        if dic["value"] in special_items["special_items"].tolist():
                            dispatcher.utter_message(text= f"{item} is a special item.please follow the template provided: ")
                    elif dic["entity"] =="cost":
                        if pax==0:
                            to_append=float(re.findall(r'\d+', dic["value"])[0])
                            pax+=1
                        cost_list.append(to_append)
                    elif dic["entity"] =="pax":
                        if cost==0:
                            to_append=float(re.findall(r'\d+', dic["value"])[0])
                            cost+=1
                        cost_list.append(to_append)
                        #just condition on the length of the list to see what message to dispatch.
                if intent_name=="check_item":
                    dispatcher.utter_message(text= f"No, {item} is not a special item, please follow the guidelines accordingly base on possible existing DA contracts and the total cost that will be incurred")
                    
                    #base on item cost, give the correct instructions
                elif intent_name=="item_cost":
                    total_cost=cost_list[0]
                    additional_msg=self.total_cost_message(total_cost)
                    dispatcher.utter_message(text= f"The total cost is {total_cost}. "+additional_msg)
                elif intent_name=="all_information":
                    total_cost=cost_list[0]*cost_list[1]
                    additional_msg=self.total_cost_message(total_cost)
                    dispatcher.utter_message(text= f"The total cost is {total_cost}. "+additional_msg)    
        except: 
            dispatcher.utter_message(text= "Sorry i did not understand the question, try asking it again in another way.") 
        #for open_buy_item where i need buttons to control conversation flow
                    
        return []
class Action_check_items_obi(Action):
    def name(self) -> Text:
        return "action_check_item_obi"
    #to better manage the differenct messages to be send out for different cost
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #condition on intents
        intent_name=tracker.latest_message["intent"]["name"]
        special_items=pd.read_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/item_list.csv")
        #see if randomly put item is a special item dispatch the appropriate message
        #check the buy item and item cost converstaion flow.
        if intent_name=="open_buy_item":
            for dic in tracker.latest_message['entities']:
                if dic["entity"]=="items":
                    item=dic["value"]
                    if dic["value"] in special_items["special_items"].tolist():
                        buttons=[{"title":"That was helpful!", "payload":"helpful"},{"title":"That was unhelpful!", "payload":"unhelpful"}]
                        dispatcher.utter_message(text= f"{item} is a special item that uses a special procedure. Please... Was that helpful?",buttons=buttons)
                    else:
                        dispatcher.utter_message(text= "How much does it cost in total?") 
        else:
           dispatcher.utter_message(text= "Sorry did not understand what you were saying, could you try saying it in another way?")  
                    
        return []
    
class Action_check_department(Action):
    def name(self) -> Text:
        return "action_check_department"
    #to better manage the differenct messages to be send out for different cost
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #condition on intents
        intent_name=tracker.latest_message["intent"]["name"]
        df_departments=pd.read_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/departments.csv")
        #see if randomly put item is a special item dispatch the appropriate message
        #check the buy item and item cost conversation flow.
        if intent_name=="contact_officer_1":
            df_filtered=df_departments[df_departments["department"]==tracker.latest_message['entities'][0]["value"]]
            officer_name=df_filtered["officer_name"].values[0]
            officer_email=df_filtered["officer_email"].values[0]
            dispatcher.utter_message(text=f"please contact {officer_name} at {officer_email} with the questions. thanks!")
        else:
            dispatcher.utter_message(text="Sorry, i did not understand what you say, please be more specific.")
                    
        return []
# class Action_multiple_utterance(Action):
    # def name(self) -> Text:
        # return "action_multiple_utterance"

    # def run(self, dispatcher: CollectingDispatcher,
            # tracker: Tracker,
            # domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # #condition to read from different parts if is normal story or if it is the faq rule
        # if "faqm/" in tracker.latest_message['response_selector']["default"]["ranking"][0]["intent_response_key"]:
            # intent_name=tracker.latest_message['response_selector']["default"]["response"]["intent_response_key"]
        # else:
            # intent_name=tracker.latest_message["intent"].get("name")
        # template=pd.read_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/multiple_utterance.csv")
        # #template["log"]=intent_name
        # #template.to_csv("/Users/User/Desktop/learning/Rasa/Consolidated/actions/logs.csv")
        # filtered_template=template[template["intent"]==intent_name]
        # message_1=filtered_template["utterance_1"].values[0]
        # try: #condition for replies if there are not links for the given intent".
            # dispatcher.utter_message(text= f"{message_1}")
        # except:
            # dispatcher.utter_message(text= "Something went wrong")
        # return []

