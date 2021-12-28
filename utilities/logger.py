import logging, os
from opencensus.ext.azure.log_exporter import AzureLogHandler

def get_logger(name:str, logging_level:int = logging.INFO):

  logger = logging.getLogger(name)
  logger.setLevel(logging_level)
  logger.handlers = []

  formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s', 
    datefmt='%y-%m-%d %H:%M')
  
  console = logging.StreamHandler()
  console.setLevel(logging_level)
  console.setFormatter(formatter)
  
  logger.addHandler(console)

  # if an app connection insight string is set
  # then add an azure logger.
  if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
      azure = AzureLogHandler()
      azure.setLevel(logging_level)
      azure.setFormatter(formatter)
      logger.addHandler(azure)
      
  return logger

