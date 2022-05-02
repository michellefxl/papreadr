from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from pathlib import Path

from actions.actionconstants import *

url_file = Path(URL_LOG)


class GetNotes(Action):
    """show saved notes of paper

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_getnotes"

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
            # get url from history
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

            try:
                note_f = open(
                    note_file,
                )
                note_data = json.load(note_f)
                doc_notes = note_data["doc_notes"]

                notes_str = ""
                for n in doc_notes:
                    notes_str = notes_str + "\n - " + n

                botResponse = f"{notes_str}"
            except FileNotFoundError:
                print("The file does not exist")
                botResponse = f"No notes."

        except requests.ConnectionError as exception:
            botResponse = f"Please give a valid link."

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
