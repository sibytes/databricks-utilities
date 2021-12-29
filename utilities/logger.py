import logging, os
from opencensus.ext.azure.log_exporter import AzureLogHandler
from logging import LogRecord
import requests
from requests import HTTPError
import datetime
import hashlib
import hmac
import base64
from pythonjsonlogger.jsonlogger import JsonFormatter


class LogAnalyticsHandler(logging.Handler):
    """Custom handler to log to azure analytics workspace.

    Formats the log, message and uses the log analytics end point
    to load a json payload.
    https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api
    """

    _METHOD = "POST"
    _CONTENT_TYPE = "application/json"
    _RESOURCE = "/api/logs"
    _RFC1123_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
    _DOMAIN = "ods.opinsights.azure.com"

    def __init__(
        self,
        workspace_id: str,
        shared_key: str,
        log_type: str,
        api_version: str = "2016-04-01",
    ):
        """
        LogAnalyticsHandler class constructor

        Parameters:
            self: instance of the class
            workspace_id: log analytics workspace id
            shared_key: log analytics shared key
            log_type: The log record that will be created in loganalytics
            api_version: the version of the azure rest api to call to insert the message default=016-04-01
        Returns:
            None
        """

        super().__init__()
        self._workspace_id = workspace_id
        self._shared_key = shared_key
        self._log_type = log_type
        self._api_version = api_version

    def emit(self, record: LogRecord) -> None:
        """
        Save the log record to log analytics
        Parameters:
            self: instance of the class
            record: log record to be saved
        Returns:
            None
        """
        body = self.format(record)
        self._post(self._workspace_id, self._shared_key, body, self._log_type)

    def _build_signature(self, workspace_id, shared_key, date, content_length):
        """Build the API signiture for the header authorisation"""

        x_headers = "x-ms-date:" + date
        string_to_hash = f"{self._METHOD}\n{str(content_length)}\n{self._CONTENT_TYPE}\n{x_headers}\n{self._RESOURCE}"
        bytes_to_hash = bytes(string_to_hash, encoding="utf-8")
        decoded_key = base64.b64decode(shared_key)
        encoded_hash = base64.b64encode(
            hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
        ).decode()
        authorization = f"SharedKey {workspace_id}:{encoded_hash}"

        return authorization

    # Build and send a request to the POST API
    def _post(self, workspace_id, shared_key, body, log_type):
        """Build API call and log to log analytics"""
        rfc1123_date = datetime.datetime.utcnow().strftime(self._RFC1123_FORMAT)
        content_length = len(body)
        signature = self._build_signature(
            workspace_id, shared_key, rfc1123_date, content_length
        )
        uri = f"https://{workspace_id}.{self._DOMAIN}{self._RESOURCE}?api-version={self._api_version}"

        headers = {
            "content-type": self._CONTENT_TYPE,
            "Authorization": signature,
            "Log-Type": log_type,
            "x-ms-date": rfc1123_date,
        }

        response = requests.post(uri, data=body, headers=headers)

        # check that there are no response errors.
        try:
            response.raise_for_status()

        except HTTPError as e:
            # logging calls will be abstracted so indicate to the user
            # that it's this handler that's broken and log using the root handler
            msg = f"Log analytic log provider failed. {e.response.status_code} error at {uri} {e.response.text}"
            logging.error(msg)
            raise Exception(msg)


def get_logger(
    name: str = "sibytesDatabricksUtils3", 
    logging_level: int = logging.INFO
):
    """Get a python canonical logger

    Setups a console handler for the notebook UI.
    Also sets up a App Insights and/or log analytics
    handler if configured in the environment variables.

    """
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    format_string = "%(asctime)s.%(msecs)03d, %(name)s, %(module)s, %(funcName)s, line %(lineno)d, %(levelname)s, %(message)s"
    formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

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

    if os.getenv("LOGANALYTICSID"):
        if not any(l.get_name() == "azure_log_analytics" for l in logger.handlers):

            workspace_id = os.getenv("LOGANALYTICSID")
            shared_key = os.getenv("LOGANALYTICSKEY")

            log_analytics = LogAnalyticsHandler(
                workspace_id, shared_key, name
            )
            log_analytics.setLevel(logging_level)
            formatter = JsonFormatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
            log_analytics.setFormatter(formatter)
            log_analytics.set_name("azure_log_analytics")
            logger.addHandler(log_analytics)

    return logger
