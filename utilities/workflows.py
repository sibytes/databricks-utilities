from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from dataclasses import dataclass
from typing import List
import json
import logging

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
  
    print(f"Executing notebook {notebook.path}")
    
    try:
        
        return dbutils.notebook.run(notebook.path, notebook.timeout, notebook.get_parameters())
    
    except Exception as e:
        
        if notebook.retry < 1:
            failed = json.dumps({
                "status" : "failed",
                "error" : str(e),
                "notebook" : notebook.path})
            logging.error(failed)
            raise Exception(failed)
        
        logging.info(f"Retrying notebook {notebook.path}")
        notebook.retry -= 1
  
  
def try_future(future:Future):
    try:
        return json.loads(future.result())
    except Exception as e:
        logging.error(str(e))
        return json.loads(str(e))
  
  
# Parallel execute a list of notebooks in parallel
def execute_notebooks(notebooks:List[Notebook], maxParallel:int, dbutils):
  
    logging.info(f"Executing {len(notebooks)} in with maxParallel of {maxParallel}")
    with ThreadPoolExecutor(max_workers=maxParallel) as executor:

        results = [executor.submit(execute_notebook, notebook, dbutils)
                for notebook in notebooks 
                if notebook.enabled]
    
        # the individual notebooks handle their errors and pass back a packaged result
        # we will still need to handle the fact that the notebook execution call may fail
        # or a programmer missed the handling of an error in the notebook task
        # that's what tryFuture(future:Future) does    
        return [try_future(r) for r in as_completed(results)]

  
