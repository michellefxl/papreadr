from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from actions.actionconstants import *
from actions.utils import log_user_msg


class ShowPaperLog(Action):
    """retrieve user read papers

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_paper_log"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        session_id = tracker.sender_id

        log_user_msg(tracker.latest_message["text"], session_id)

        user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")

        # retrieve paper log (title, url) and present in selectable list
        data = []
        try:
            f_in = open(
                user_paper_log
            )
            data = json.load(f_in)
        except FileNotFoundError:
            print("The file does not exist")

        # bot response
        response_data = []
        dup_paper = []
        for data_line in data['paper_log']:
            if data_line['title'] not in dup_paper:
                dup_paper.append(data_line['title'])
                doc_folder = data_line["folder"]
                venue = json.load(open(doc_folder + "/details.log"))["publisher"]
                year = json.load(open(doc_folder + "/details.log"))["year"]
                paper_data = f"{data_line['title']}, {venue}, {year}"
                response_data.append({"title": paper_data, "payload": data_line['url']})
            else:
                continue

        paper_count = len(response_data)
        if paper_count == 1:
            botResponse = f"You have read {paper_count} paper! Keep it up! 😀"
        elif paper_count == 0:
            botResponse = f"I have not read any papers with you. Let's start reading together! 💪"
        else:
            botResponse = f"You have read {paper_count} papers! Good job! 😉"

        print(response_data)
        # selectable options
        message = {"payload": "quickReplies", "data": response_data}
        dispatcher.utter_message(text=botResponse, json_message=message)

        return []
