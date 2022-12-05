# import logging
# import requests
# import json
# import pathlib
# import ruamel.yaml
# from typing import Dict, Text, Any

# logger = logging.getLogger(__name__)

# here = pathlib.Path(__file__).parent.absolute()

# json_headers = {
#     "Content-Type": "application/x-www-form-urlencoded",
#     "Accept": "application/json",
# }


# class AuthenticateAPI(object):
#     """class to get credential from keycloak API"""

#     def __init__(self):
#         snow_instance = 0
#         # snow_config = (
#         #     ruamel.yaml.safe_load(open(f"{here}/snow_credentials.yml", "r"))
#         #     or {}
#         # )
#         # self.snow_user = snow_config.get("snow_user")
#         # self.snow_pw = snow_config.get("snow_pw")
#         # self.snow_instance = snow_config.get("snow_instance")
#         # self.localmode = snow_config.get("localmode", True)
#         # self.base_api_url = "https://{}/api/now".format(self.snow_instance)

#     def handle_request(
#         self, request_method=requests.get, request_args={}
#     ) -> Dict[Text, Any]:
#         result = dict()
#         try:
#             response = request_method(**request_args)
#             result["status_code"] = response.status_code
#             if response.status_code >= 200 < 300:
#                 result["content"] = response.json()
#             else:
#                 error = (
#                     f"Keycloak error: {response.status_code}: "
#                     f'{response.json().get("error",{}).get("message")}'
#                 )
#                 logger.debug(error)
#                 result["error"] = error
#         except requests.exceptions.Timeout:
#             error = "Could not connect to Keycloak (Timeout)"
#             logger.debug(error)
#             result["error"] = error
#         return result

#     def send_authentication_request(
#         self
#     ) -> Dict[Text, Any]:
#         request_api = "http://localhost:8080/auth/realms/rasa_realm/protocol/openid-connect/token"
#         with open("/mnt/4ba37af6-51fd-47bc-8321-8c500c229114/Antbuddy/rasa/tutorial/rasa_tutorial/subscribe_email/actions/keycloak_value.json") as json_file:
#             data = json.load(json_file)
#         request_args = {
#                 "url": request_api,
#                 # "auth": (self.snow_user, self.snow_pw),
#                 "headers": json_headers,
#                 "data": data,
#             }
#         result = self.handle_request(requests.post, request_args)
#         return result