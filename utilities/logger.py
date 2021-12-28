import logging


def get_logger(name:str):

  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', datefmt='%y-%m-%d %H:%M')
  console.setFormatter(formatter)


  logger = logging.getLogger(name)
  logger.setLevel(logging.INFO)
  logger.addHandler(console)
  
  return logger