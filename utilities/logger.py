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

