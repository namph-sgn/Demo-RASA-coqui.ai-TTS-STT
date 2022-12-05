# # This files contains your custom actions which can be used to run
# # custom Python code.
# #
# # See this guide on how to implement these action:
# # https://rasa.com/docs/rasa/custom-actions


# # This is a simple example for a custom action which utters "Hello World!"
# #!/usr/bin/python

# # -*- coding: utf8 -*-

# from typing import Any, Text, Dict, List
# #


# import datetime as dt
# # import sys
# # sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
# # sys.stdin = codecs.getreader('utf_8')(sys.stdin)


# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
# class ActionGreetWithName(Action):

#     def name(self) -> Text:
#         return "action_greet_with_name"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         customer_name = tracker.get_slot("customer_name")
#         dispatcher.utter_message(text="Xin chào {}!".format(customer_name))
#         dispatcher.utter_message(text="Chúc bạn ngày mới vui vẻ!")
#         dispatcher.utter_message(image="https://i.imgur.com/nGF1K8f.jpg")

#         return []
