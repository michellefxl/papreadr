from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from actions.actionconstants import *
from actions.utils import log_user_msg


class ShowReferences(Action):
    """retrieve paper references

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_paper_ref"

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
            # take latest document url
            doc_folder = data["paper_log"][-1]["folder"]
        except FileNotFoundError:
            print("The file does not exist")

        # check if references list exists
        ref_bool = False
        paper_details = []
        try:
            f_in = open(
                os.path.join(doc_folder, "details.log")
            )
            try:
                paper_details = json.load(f_in)
                if paper_details['references'] != "null":
                    ref_bool = True
            except:
                print("No abstract")
        except FileNotFoundError:
            print("The file does not exist")

        if ref_bool:
            # bot response
            response_data = []
            for data_line in paper_details['references']:
                paper_data = f"{data_line['title']}, {data_line['venue']}, {data_line['year']}"
                response_data.append({"title": paper_data, "payload": data_line['url']})

            print(response_data)
            ref_cnt = len(paper_details['references'])
            botResponse = f"This paper has {ref_cnt} references! 😀"

            # selectable options
            message = {"payload": "quickReplies", "data": response_data}
            dispatcher.utter_message(text=botResponse, json_message=message)
        else:
            dispatcher.utter_message(text=f"Sorry I can't retrieve the references 😔")

        return []
