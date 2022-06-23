from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
import shutil
from datetime import datetime
from actions.actionconstants import *
from actions.utils import write_json, log_user_msg


class SessionId(Action):
    """retrieve user conversation session id

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_session_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        session_id = tracker.sender_id
        added_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        # check if user in log if not create new user
        data = []
        try:
            f_in = open(
                USER_LOG,
            )
            data = json.load(f_in)
        except FileNotFoundError:
            print("The file does not exist")

        no_user = True

        if len(data["user_ids"]) > 0:
            for data_line in data["user_ids"]:
                if data_line["id"] == session_id:
                    no_user = False

            if no_user:
                user_folder = os.path.join(LOG_FOLDER + "/users", session_id)
                shutil.copytree(USER_TEMPLATE_FOLDER, user_folder)
                user_dict = {
                    "id": session_id,
                    "folder": user_folder,
                    "added_date": added_time,
                }
                write_json(user_dict, USER_LOG, jsonkey="user_ids")
        else:
            user_folder = os.path.join(LOG_FOLDER + "/users", session_id)
            shutil.copytree(USER_TEMPLATE_FOLDER, user_folder)
            user_dict = {
                "id": session_id,
                "folder": user_folder,
                "added_date": added_time,
            }
            write_json(user_dict, USER_LOG, jsonkey="user_ids")

        log_user_msg(tracker.latest_message["text"], tracker.sender_id)

        botResponse = f"Your session id is {session_id}"

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
