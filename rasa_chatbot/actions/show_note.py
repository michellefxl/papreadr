from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json

from actions.actionconstants import *
from actions.utils import log_user_msg


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

                try:
                    note_f = open(
                        note_file,
                    )
                    note_data = json.load(note_f)
                    doc_notes = note_data["doc_notes"]

                    notes_str = ""
                    if len(doc_notes) > 0:
                        for n in doc_notes:
                            notes_str = notes_str + "\n - " + n

                        botResponse = f"{notes_str}"
                    else:
                        botResponse = f"🤔 There are no notes for this paper"
                except FileNotFoundError:
                    print("The file does not exist")
            else:
                botResponse = "🤔 I have not read any papers with you. Please add a paper"
            # bot response
            dispatcher.utter_message(text=botResponse)     
        except FileNotFoundError:
            print("The file does not exist")

        return []
