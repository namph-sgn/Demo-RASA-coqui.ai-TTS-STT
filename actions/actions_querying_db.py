# from typing import Any, Text, Dict, List
# import collections

# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher

# from pymongo import MongoClient
# from pprint import pprint
# import random
# # from fuzzywuzzy import process


# # class ValidateOrderForm(Action):

# #     def name(self) -> Text:
# #         return "validate_order_form"

# #     def validate_chosen_jewelry_name(self,
# #                                      slot_value: Any,
# #                                      dispatcher: CollectingDispatcher,
# #                                      tracker: Tracker,
# #                                      domain: Dict[Text, Any]) -> Dict[Text, Any]:
# #         """validate_jewelry_name Validate gotten jewelry name"""

# #         if slot_value.lower() not in JEWELRY_NAME:
# #             dispatcher.uttermessage(
# #                 text="Xin lỗi, bên shop không có sản phẩm nào với tên như vậy.")
# #             return {"chosen_jewelry_name": None}
# #         dispatcher.utter_message("OK, chúng tôi đã nhận được yêu cầu")
# #         return {"chosen_jewelry_name": slot_value}


# class ActionOrderJewelry(Action):

#     def name(self) -> Text:
#         return "action_order_jewelry"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         client, dbconn = DBQueryingMethods.connect_local_db(database='jewelry')
#         chosen_jewelry_name = tracker.get_slot("chosen_jewelry_name")
#         customer_name = tracker.get_slot("customer_name")
#         query_result = DBQueryingMethods.query_by_slot_and_value(
#             dbconn, slot="name", slot_value=chosen_jewelry_name, collection="name_and_price")
#         if len(query_result) == 1:
#             product = {
#                 'customer_name': customer_name,
#                 'jewelry_id': query_result[0]['_id']
#             }
#             result = dbconn["order"].insert_one(product)
#             dispatcher.utter_message(
#                 text="Đơn hàng đã được đặt, cảm ơn anh/chị đã mua ở cửa hàng chúng tôi.")
#         else:
#             dispatcher.utter_message(
#                 text="Không có sản phẩm anh chị đặt. Xin hãy chọn sản phẩm khác")
#         return []


# class ActionQueryJewelryByType(Action):

#     def name(self) -> Text:
#         return "query_jewelry_by_type"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         client, dbconn = DBQueryingMethods.connect_local_db(database='jewelry')
#         category = tracker.get_slot("jewelry_category")
#         name = tracker.get_slot("jewelry_name")
#         if name:
#             get_query_result = DBQueryingMethods.query_by_slot_and_value(
#                 dbconn, slot="name", slot_value=name, collection="name_and_price")
#         elif category:
#             get_query_result = DBQueryingMethods.query_by_slot_and_value(
#                 dbconn, slot="category", slot_value=category, collection="name_and_price")
#         if len(get_query_result) > 0:
#             chosen_result = random.choice(get_query_result)
#             dispatcher.utter_message(text="Anh/Chị thấy sản phẩm {} với giá {} này phù hợp không ạ?".format(
#                 chosen_result['name'], chosen_result['price']))
#         else:
#             dispatcher.utter_message(
#                 text="Xin lỗi anh chị, không có sản phẩm anh chị cần")
#         return []

# class DBQueryingMethods:
#     def connect_local_db(database='jewelry_database'):
#         """connect_local_db Connect to local mongodb database and return client with a specified database

#         Use pymongo to connect to local database at port 27017. Return client and db connection

#         Args:
#             database (str, optional): name of one database. Defaults to 'default'.
#         """
#         client = MongoClient("localhost:27017")
#         db = client[database]
#     #     Check if database is connected and can be queried
#         try:
#             serverStatusResult = db.command("serverStatus")
#             # pprint(serverStatusResult)
#         except Exception as e:
#             print(e)
#         return client, db

#     def query_by_slot_and_value(dbconn, collection="name_and_price", slot="category", slot_value="Vòng tay"):
#         """select_all Query all document in mongo collection with database connection

#         Get the cursor for all document in mongo database. Choose database by passing different database connection to conn

#         Args:
#             conn (MongoConnection): Database connection
#         """
#         query_dict = dict()
#         query_dict[slot] = {"$regex": f"({slot_value})"}
#         # query_dict = {
#         #     slot: {
#         #         "$regex": f"({pizza_name})"
#         #     }
#         # }
#         print(query_dict)
#         for document in dbconn[collection].find(query_dict):
#             print(document)
#         result_list = list(dbconn[collection].find(query_dict))
#         return result_list

#     def rows_info_as_text(rows):
#         """
#         Return one of the rows (randomly selcted) passed in
#         as a human-readable text. If there are no rows, returns
#         text to that effect.
#         """
#         if len(list(rows)) < 1:
#             return "There are no resources matching your query."
#         else:
#             for row in random.sample(rows, 1):
#                 return f"Try the {(row[4]).lower()} {row[0]} by {row[1]}. You can find it at {row[2]}."
