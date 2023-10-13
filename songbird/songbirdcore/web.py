from typing import Optional, List, Dict
import logging
from requests_html import HTMLSession
import requests

logger = logging.getLogger(__name__)


class SimpleSession:
    def __init__(
        self,
        name: str,
        root_url: str,
        credentials: Optional[dict] = {},
        headers: Optional[dict] = {},
    ):
        self.name = name
        self.root_url = root_url
        self.credentials = {}
        self.headers = headers
        if headers is None:
            self.headers = {  # default header is generic old mac
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15"
            }
        self.current_url = ""

        # initialize a session for this class.. to be used for all requests
        self.s = HTMLSession()

    def get_form_inputs(
        self, form_url: str, payload={}, log_calls: Optional[bool] = True
    ):
        """Get the inputs for a form on a webpage

        Args:
            form_url (str): the url for the form
            user_input_on (bool, optional): _description_. Defaults to True.
            payload (dict, optional): _description_. Defaults to {}.
        """
        # initialize form_inputs to be empty each request
        form_inputs = {}
        try:
            form_response = self.s.get(form_url, headers=self.headers)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error submitting request to: {form_url}", e)
            return None
        if log_calls:
            logger.info(f"Loaded web page: {form_response.url}!")
        # incase you want to parse through the login page.. see below comment
        inputs = form_response.html.find("input")

        # adds the csrf middleware tokens to login details.. usually stored
        # in <name> and <value> html tags
        for inputfield in inputs:
            key = inputfield.attrs["name"]
            form_inputs.update({key: ""})

        # remove None type attributes
        try:
            form_inputs.pop(None)
        except KeyError:
            logger.debug("No nonetype attributes to be removed.")

        form_inputs.update(payload)
        if log_calls:
            logger.info(f"Auto filled the web form with inputs: {form_inputs}")
        return form_inputs

    def enter_search_form(
        self,
        search_url: str,
        form_url: Optional[str] = None,
        payload: Optional[dict] = None,
        render_timeout: Optional[int] = 10,
        render_wait: Optional[int] = 0.2,
        render_sleep: Optional[int] = 1,
        log_calls: Optional[bool] = True,
    ):
        """
        Enter into a search form for a website
        Args:
            form_url (Optional[str]): the url for the html form. If not passed, uses the root_url for the class.
            search_url (str): the url to perform the search against
            payload (Optional[dict]): optionally include a payload for the request

        Returns:
            requests.Response: the rendered html response
        """
        if form_url is None:
            form_url = self.root_url

        form_inputs = self.get_form_inputs(form_url, payload, log_calls)

        if form_inputs is None:
            return None
        try:
            response = self.s.get(search_url, params=form_inputs, headers=self.headers)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            logger.error(f"Error submitting request to: {search_url}", e)
            return None

        logger.debug("Rendering html for : " + response.url)
        response.html.render(
            timeout=render_timeout, wait=render_wait, sleep=render_sleep
        )
        logger.debug("Rendering complete for : " + response.url)
        return response

    def close(self):
        self.s.close()
