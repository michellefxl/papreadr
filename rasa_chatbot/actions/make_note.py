from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json

from actions.actionconstants import *
from actions.utils import write_json, log_user_msg


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
        session_id = tracker.sender_id

        log_user_msg(userMessage, session_id)

        user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")
        data = []
        try:
            f_in = open(
                user_paper_log,
            )
            data = json.load(f_in)
            if len(data["paper_log"]) > 0:
                doc_folder = data["paper_log"][-1]["folder"]
                note_file = os.path.join(doc_folder, "notes.log")

                user_note = userMessage.split(":")[-1]

                if user_note != "":
                    write_json(user_note + "\n", note_file, "doc_notes")

                    botResponse = f"Noted."
                else:
                    botResponse = f"Where's the note?"
            else:
                botResponse = "🤔 Which paper are you reading? Please add the paper"
            # bot response
            dispatcher.utter_message(text=botResponse)
        except FileNotFoundError:
            print("The file does not exist")

        return []
