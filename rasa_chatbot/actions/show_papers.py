from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import json
from collections import Counter
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
        pub_list = []
        year_list = []
        field_list = []
        sum_read_time = 0
        for data_line in data['paper_log']:
            if data_line['title'] not in dup_paper:
                dup_paper.append(data_line['title'])
                doc_folder = data_line["folder"]
                venue = json.load(open(doc_folder + "/details.log"))["publisher"]
                year = json.load(open(doc_folder + "/details.log"))["year"]
                paper_data = f"{data_line['title']}, {venue}, {year}"
                response_data.append({"title": paper_data, "payload": data_line['url']})
            
                # additional data for read stats
                if venue == "":
                    pub_list.append("Unknown")
                else:
                    pub_list.append(venue)
                year_list.append(str(year))
                field = json.load(open(doc_folder + "/details.log"))["field"][0]
                if field == "":
                    field_list.append("Unknown")
                else:
                    field_list.append(field)
                read_time = json.load(open(doc_folder + "/details.log"))["read_time"]
                sum_read_time+=read_time            
            else:
                continue

        paper_count = len(response_data)
        if paper_count == 0:
            botResponse = f"I have not read any papers with you. Let's start reading together! 💪"
            dispatcher.utter_message(text=botResponse)
        else:
            # reading stats        
            pub_dict = dict(Counter(pub_list))
            yr_dict = dict(Counter(year_list))
            fld_dict = dict(Counter(field_list))

            str_fld = ""
            for k, v in fld_dict.items():
                str_fld += f"{k} ({str(v)}) "

            str_yr = ""
            for k, v in yr_dict.items():
                str_yr += f"{k} ({str(v)}) "

            str_pub = ""
            for k, v in pub_dict.items():
                str_pub += f"{k} ({str(v)}) "

            print(str_fld)
            print(str_yr)
            print(str_pub)

            if paper_count == 1:
                botResponse = f"You have spent {sum_read_time} minutes on {paper_count} paper! Keep it up! 😀"
            else:
                botResponse = f"You have spent {sum_read_time} minutes on {paper_count} papers! Good job! 😉"

            data_col=[{"title":"Field","description":f"{str_fld}"},{"title":"Year","description":f"{str_yr}"},{"title":"Publisher","description":f"{str_pub}"}]
            colmsg={"payload":"collapsible","data":data_col}
            dispatcher.utter_message(text=botResponse,json_message=colmsg)

            print(response_data)
            # selectable options
            message = {"payload": "quickReplies", "data": response_data}
            dispatcher.utter_message(text="Here are the links to the papers:", json_message=message)


        return []
