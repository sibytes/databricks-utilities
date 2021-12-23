import logging
import os

class AppConfig:

  def __init__(self, dbutils, spark) -> None:
      self.dbutils = dbutils
      self.spark = spark


  def _get_env(self, variable:str): 

      var = os.getenv(variable)

      if var:
        return var

      else:
          msg = f"Environment variable '{variable}' not found"
          logging.error(msg)

          raise Exception(msg)    


  def get_oauth_refresh_url(self):

      return f"https://login.microsoftonline.com/{self.get_azure_ad_id()}/oauth2/token"  


  def get_storage_account(self):

      return self._get_env("STORAGEACCOUNT")


  def get_environment(self):

      return self._get_env("ENVIRONMENT")


  def get_azure_ad_id(self):

      return self._get_env("AZUREADID")


  def get_automation_scope(self):

      return self._get_env("AUTOMATIONSCOPE")


  def get_dataLake_storage_type(self): 

      return self._get_env("STORAGE") 


  def get_resource_group(self): 

      return self._get_env("RESOURCEGROUP") 


  def get_subscription_id(self): 

      return self._get_env("SUBSCRIPTIONID") 


  def _get_dbutils_secret(self, key:str): 

      secret = self.dbutils.secrets.get(
          scope = self.get_automation_scope(), 
          key = self._get_env(key))

      return secret


  def get_service_principal_id(self):

      return self._get_dbutils_secret("DATAPLATFORMAPPID")


  def get_service_credential(self):

      return self._get_dbutils_secret("DATAPLATFORMSECRET")   


  def help(self, as_html=False):

      if as_html:
        return f"""
        <p>Configuration:</p>
        <table>
        <tr><th align='left'>Function          </th><th align='left'> Value               </td></tr>
        <tr><td>get_environment()              </td><td> {self.get_environment()}              </td></tr>
        <tr><td>get_storage_account()          </td><td> {self.get_storage_account()}          </td></tr>
        <tr><td>get_dataLake_storage_type()    </td><td> {self.get_dataLake_storage_type()}       </td></tr>
        <tr><td>get_automation_scope()         </td><td> {self.get_automation_scope()}           </td></tr>
        <tr><td>get_resource_group()           </td><td> {self.get_resource_group()}             </td></tr>
        <tr><td>get_azure_ad_id()              </td><td> {self.get_azure_ad_id()}              </td></tr>
        <tr><td>get_subscription_id()          </td><td> {self.get_subscription_id()}            </td></tr>
        <tr><td>get_oauth_refresh_url()        </td><td> {self.get_oauth_refresh_url()}        </td></tr>
        <tr><td>get_service_principal_id()     </td><td> {self.get_service_principal_id()}        </td></tr>
        <tr><td>get_service_credential()       </td><td> {self.get_service_credential()}         </td></tr>
        </table>
        """
      else:
          print(f"""
  Configuration:
  --------------------------------------------------------
  get_environment()           : {self.get_environment()} 
  get_storage_account()       : {self.get_storage_account()}        
  get_dataLake_storage_type() : {self.get_dataLake_storage_type()}     
  get_automation_scope()      : {self.get_automation_scope()}        
  get_resource_group()        : {self.get_resource_group()}          
  get_azure_ad_id()           : {self.get_azure_ad_id()}            
  get_subscription_id()       : {self.get_subscription_id()}          
  get_oauth_refresh_url()     : {self.get_oauth_refresh_url()}      
  get_service_principal_id()  : {self.get_service_principal_id()}       
  get_service_credential()    : [REDACTED]  
          """)


  def connect_storage(self):

      _gen1 = "dfs.adls.oauth2"
      _gen2 = "fs.azure.account"

      _storageType = self.get_dataLake_storage_type()

      if _storageType == "AzureDataLakeGen1":

        self.spark.conf.set(f"{_gen1}.access.token.provider.type", "ClientCredential")
        self.spark.conf.set(f"{_gen1}.client.id", self.get_service_principal_id())
        self.spark.conf.set(f"{_gen1}.credential", self.get_service_credential())
        self.spark.conf.set(f"{_gen1}.refresh.url", self.get_oauth_refresh_url())    

      elif _storageType == "AzureDataLakeGen2":

        self.spark.conf.set(f"{_gen2}.auth.type", "OAuth")
        self.spark.conf.set(f"{_gen2}.oauth.provider.type", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
        self.spark.conf.set(f"{_gen2}.oauth2.client.id", self.get_service_principal_id())
        self.spark.conf.set(f"{_gen2}.oauth2.client.secret", self.get_service_credential())
        self.spark.conf.set(f"{_gen2}.oauth2.client.endpoint", self.get_oauth_refresh_url())

      else:

          logging.error(f"Unknown storage type {_storageType} in enviornment variable DATALAKESTORAGE")
          raise Exception(f"Unknown storage type {_storageType} in enviornment variable DATALAKESTORAGE")   


      logging.info(f"""
        |Connected:
        |-----------------------------------------------
        | environment = {self.get_environment()}
        | storage account = {self.get_storage_account()} 
      """)
