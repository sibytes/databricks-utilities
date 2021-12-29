from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass
from typing import List
import json
from . import get_logger

logger = get_logger()

# used to carry notebook data
@dataclass
class Notebook:
    path: str
    timeout: int
    parameters: dict = None
    retry: int = 0
    enabled:bool = True
        
    # add the notebook name to parameters using the path and return
    def get_parameters(self):
        """Add the notebook path to parameters
        
        """
        
        if not self.parameters:
            self.parameters = dict()
        
        params = self.parameters
        params["notebook"] = self.path
        
        return params

# execute a notebook using databricks workflows
def execute_notebook(notebook:Notebook, dbutils):
    """Execute a notebookd using databricks workflows
    
    """
    msg = {
      "_message": f"Executing notebook {notebook.path}",
      "status": "executing",
      "notebook": notebook.path
    }
    logger.info(msg["_message"], extra=msg)
    
    try:
        result = dbutils.notebook.run(notebook.path, notebook.timeout, notebook.get_parameters())
        msg = {
          "_message": f"Succeeded notebook {notebook.path}",
          "status": "succeeded",
          "notebook": notebook.path
        }
        logger.info(msg["_message"], extra=msg)
        return result
    
    except Exception as e:
        
        if notebook.retry < 1:
            msg = {
                "_message" : f"notebook {notebook.path} failed.",
                "status": "failed",
                "error" : str(e),
                "notebook" : notebook.path}
            logger.error(msg["_message"], extra=msg)
            raise Exception(msg["_message"])
            
        msg = {
          "_message": f"Retrying notebook {notebook.path}",
          "status": "executing",
          "notebook": notebook.path
        }
        logger.info(msg["_message"], extra=msg)
        notebook.retry -= 1
  
  
def try_future(future:Future):
    try:
        return json.loads(future.result())
    except Exception as e:
        msg = {
            "_message" : f"notebook failed. {str(e)}",
            "status": "failed",
            "error" : str(e),
            "notebook" : ""
        }
        logger.error(msg["_message"], extra=msg)
        return msg
  
  
# Parallel execute a list of notebooks in parallel
def execute_notebooks(notebooks:List[Notebook], maxParallel:int, dbutils):

    msg = {
      "_message": f"Executing {len(notebooks)} with maxParallel of {maxParallel}",
      "notebooks": len(notebooks),
      "maxParallel": maxParallel
    }
    logger.info(msg["_message"], extra=msg)
    with ThreadPoolExecutor(max_workers=maxParallel) as executor:

        results = [executor.submit(execute_notebook, notebook, dbutils)
                for notebook in notebooks 
                if notebook.enabled]
    
        # the individual notebooks handle their errors and pass back a packaged result
        # we will still need to handle the fact that the notebook execution call may fail
        # or a programmer missed the handling of an error in the notebook task
        # that's what tryFuture(future:Future) does
        results_list = [try_future(r) for r in as_completed(results)]
        msg = {
            "message": f"Finished executing {len(notebooks)} with maxParallel of {maxParallel}",
            "notebooks": len(notebooks),
            "maxParallel": maxParallel,
            "results": results_list
        }
        logger.info(msg)
        return results_list

  
