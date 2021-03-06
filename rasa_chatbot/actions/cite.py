from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json

from actions.actionconstants import *
from actions.utils import log_user_msg


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
        session_id = tracker.sender_id

        log_user_msg(userMessage, session_id)

        user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")
        data = []
        bibtex = ""
        try:
            f_in = open(
                user_paper_log,
            )
            data = json.load(f_in)
            f_in.close()
            if len(data["paper_log"]) > 0:
                doc_folder = data["paper_log"][-1]["folder"]
                doc_details = os.path.join(doc_folder, "details.log")
                with open(doc_details, "r") as file:
                    # First we load existing data into a dict.
                    bibtex = json.load(file)["bib"]
                    file.close()
                botResponse = bibtex
            else:
                botResponse = "🤔 I have not read any papers with you. Please add the paper you want to cite"
            # bot response
            dispatcher.utter_message(text=botResponse)
        except FileNotFoundError:
            print("The file does not exist")

        return []
