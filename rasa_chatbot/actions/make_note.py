from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from pathlib import Path

from actions.actionconstants import *
from actions.utils import write_json

url_file = Path(URL_LOG)


class AddNotes(Action):
    """add notes for paper

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_addnotes"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input
        userMessage = tracker.latest_message["text"]

        # check if valid url
        try:
            # get latest paper folder from history
            data = []
            try:
                f_in = open(
                    URL_LOG,
                )
                data = json.load(f_in)
                doc_folder = data["url_history"][-1]["folder"]
            except FileNotFoundError:
                print("The file does not exist")

            note_file = os.path.join(doc_folder, "notes.log")

            user_note = userMessage.split(":")[-1]

            if user_note != "":
                write_json(user_note + "\n", note_file, "doc_notes")

                botResponse = f"Noted."
            else:
                botResponse = f"Where's the note?"

        except requests.ConnectionError as exception:
            botResponse = f"Please give a valid link."

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
