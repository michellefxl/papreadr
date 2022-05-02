from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from pathlib import Path

from actions.actionconstants import *

url_file = Path(URL_LOG)


class GetCitation(Action):
    """retrieve citation from paper details.log

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_bibtex"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input (TODO: besides arxiv)
        userMessage = tracker.latest_message["text"]

        try:
            # get bibtex from history
            data = []
            bibtex = ""
            try:
                f_in = open(
                    URL_LOG,
                )
                data = json.load(f_in)
                doc_folder = data["url_history"][-1]["folder"]
                doc_details = os.path.join(doc_folder, "details.log")
                with open(doc_details, "r") as file:
                    # First we load existing data into a dict.
                    bibtex = json.load(file)["bibtex"]
            except FileNotFoundError:
                print("The file does not exist")

            botResponse = bibtex

        except requests.ConnectionError as exception:
            botResponse = f"Please give a valid link."

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
