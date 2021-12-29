import logging, os
from opencensus.ext.azure.log_exporter import AzureLogHandler

def get_logger(name:str, logging_level:int = logging.INFO):

  logger = logging.getLogger(name)
  logger.setLevel(logging_level)

  formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s', 
    datefmt='%y-%m-%d %H:%M')
  
  if not any(l.get_name() == "console" for l in logger.handlers):
    console = logging.StreamHandler()
    console.setLevel(logging_level)
    console.setFormatter(formatter)
    console.set_name("console")
    logger.addHandler(console)

  # if an app connection insight string is set
  # then add an azure logger.
  if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
      if not any(l.get_name() == "azure_app_insights" for l in logger.handlers):
          azure = AzureLogHandler()
          azure.setLevel(logging_level)
          azure.setFormatter(formatter)
          azure.set_name("azure_app_insights")
          logger.addHandler(azure)
      
  return logger

# TODO: Log analytics rest handler.
# https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api

# import json
# import requests
# import datetime
# import hashlib
# import hmac
# import base64

# # Update the customer ID to your Log Analytics workspace ID
# customer_id = 'xxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'

# # For the shared key, use either the primary or the secondary Connected Sources client authentication key   
# shared_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# # The log type is the name of the event that is being submitted
# log_type = 'WebMonitorTest'

# # An example JSON web monitor object
# json_data = [{
#    "slot_ID": 12345,
#     "ID": "5cdad72f-c848-4df0-8aaa-ffe033e75d57",
#     "availability_Value": 100,
#     "performance_Value": 6.954,
#     "measurement_Name": "last_one_hour",
#     "duration": 3600,
#     "warning_Threshold": 0,
#     "critical_Threshold": 0,
#     "IsActive": "true"
# },
# {   
#     "slot_ID": 67890,
#     "ID": "b6bee458-fb65-492e-996d-61c4d7fbb942",
#     "availability_Value": 100,
#     "performance_Value": 3.379,
#     "measurement_Name": "last_one_hour",
#     "duration": 3600,
#     "warning_Threshold": 0,
#     "critical_Threshold": 0,
#     "IsActive": "false"
# }]
# body = json.dumps(json_data)

# #####################
# ######Functions######  
# #####################

# # Build the API signature
# def build_signature(customer_id, shared_key, date, content_length, method, content_type, resource):
#     x_headers = 'x-ms-date:' + date
#     string_to_hash = method + "\n" + str(content_length) + "\n" + content_type + "\n" + x_headers + "\n" + resource
#     bytes_to_hash = bytes(string_to_hash, encoding="utf-8")  
#     decoded_key = base64.b64decode(shared_key)
#     encoded_hash = base64.b64encode(hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()).decode()
#     authorization = "SharedKey {}:{}".format(customer_id,encoded_hash)
#     return authorization

# # Build and send a request to the POST API
# def post_data(customer_id, shared_key, body, log_type):
#     method = 'POST'
#     content_type = 'application/json'
#     resource = '/api/logs'
#     rfc1123date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
#     content_length = len(body)
#     signature = build_signature(customer_id, shared_key, rfc1123date, content_length, method, content_type, resource)
#     uri = 'https://' + customer_id + '.ods.opinsights.azure.com' + resource + '?api-version=2016-04-01'

#     headers = {
#         'content-type': content_type,
#         'Authorization': signature,
#         'Log-Type': log_type,
#         'x-ms-date': rfc1123date
#     }

#     response = requests.post(uri,data=body, headers=headers)
#     if (response.status_code >= 200 and response.status_code <= 299):
#         print('Accepted')
#     else:
#         print("Response code: {}".format(response.status_code))

# post_data(customer_id, shared_key, body, log_type)