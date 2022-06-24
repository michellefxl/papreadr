# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


from email.mime import image
from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import json
import os
import shutil
from datetime import datetime

from actions.actionconstants import URL_LOG, LOG_FOLDER, TEMPLATE_FOLDER
from actions.utils import (
    update_json,
    write_json,
    get_read_time,
    preprocess_txt,
    get_details,
    log_user_msg
)


class SetDoc(Action):
    """add paper through url/ load local pdf
        - extract paper details and save
        - extract paper text, preprocess and save

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_setdoc"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input url, (can be url, file path, doi or title)
        userMessage = tracker.latest_message["text"]
        session_id = tracker.sender_id

        log_user_msg(userMessage, session_id)

        referesh_pdf_viewer = False
        try:
            pdf_link = userMessage
            added_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            paper_details_dict = get_details(pdf_link)
            paper_details_dict['added_date'] = added_time

            # check if url exists in user's paper log
            user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")
            data_user = []
            try:
                f_in = open(
                    user_paper_log,
                )
                data_user = json.load(f_in)
            except FileNotFoundError:
                print("The file does not exist")

            user_read_bool = False
            for data_line in data_user["paper_log"]:
                if paper_details_dict['title'] == data_line["title"]:
                    user_read_bool = True

            # check if url exists in all papers log
            data = []
            try:
                f_in = open(
                    URL_LOG,
                )
                data = json.load(f_in)
            except FileNotFoundError:
                print("The file does not exist")

            read_bool = False   # check if file exists
            for data_line in data["url_history"]:
                if paper_details_dict['title'] == data_line["title"]:
                    read_bool = True
                    doc_folder = data_line["folder"]
                    est_read_time = json.load(open(doc_folder+'/details.log'))["read_time"]
                    break

            dispatcher.utter_message(text="I'm chewing on the paper...")
            # if not read, get paper details, preprocess, get est read time, 
            if not read_bool:
                # preprocess and save text and chapters
                if paper_details_dict['pdf'] != "null":
                    cleaned_txt, doc_sections = preprocess_txt(paper_details_dict)

                    # estimate reading time (250 WPM)
                    paper_details_dict['read_time'] = get_read_time(cleaned_txt)

                    # save paper details
                    doc_folder = os.path.join(LOG_FOLDER + "/papers", paper_details_dict['title'])
                    doc_details = os.path.join(doc_folder, "details.log")

                    # save data to file
                    try:
                        # check if folder exists and update paper details/ url history
                        if os.path.exists(doc_folder):
                            update_json(paper_details_dict, doc_details)
                        else:
                            shutil.copytree(TEMPLATE_FOLDER, doc_folder)
                            update_json(paper_details_dict, doc_details)
                    except FileNotFoundError:
                        print("The file does not exist")

                    paper_data = f"{paper_details_dict['title']}, {paper_details_dict['publisher']}, {paper_details_dict['year']}"
                    botResponse = f"So you are reading \"{paper_data}\""
                    botResponse2 = f"It'll take an average person (250 WPM) {paper_details_dict['read_time']} minutes to finish this paper. I bet you can read faster than that! 🤓"
                    save_bool = True
                    referesh_pdf_viewer = True
                else: 
                    save_bool = False
                    referesh_pdf_viewer = False
                    botResponse = f"Please give a valid pdf link"
                    botResponse2 = f"Preferrably an arxiv pdf link"
            else:
                # double check if paper txt is processed
                doc_text = json.load(open(os.path.join(doc_folder, "doc_text.log")))
                if not doc_text:
                    _, _ = preprocess_txt(paper_details_dict)

                paper_data = f"{paper_details_dict['title']}, {paper_details_dict['publisher']}, {paper_details_dict['year']}"
                if user_read_bool:
                    add_date = datetime.strptime(data_line['added_date'], "%Y-%m-%d_%H:%M:%S").strftime("%A, %m/%d/%Y, %H:%M:%S")
                    botResponse = f"Oh, so you are reading \"{paper_data}\" again! You added this paper on {add_date}"
                else: 
                    botResponse = f"So you are reading \"{paper_data}\""
                botResponse2 = f"It'll take an average person (250 WPM) {est_read_time} minutes to finish this paper 🤓"

                save_bool = True
                referesh_pdf_viewer = True

            if save_bool:
                # write dict of most recent pdf in url_history even when the same pdf is read
                url_history = dict(
                        {
                            "title": paper_details_dict['title'],
                            "url": paper_details_dict['pdf'],
                            "folder": doc_folder,
                            "added_date": added_time,
                        }
                    )
                
                write_json(url_history, user_paper_log, jsonkey="paper_log")
                write_json(url_history, URL_LOG)
        except requests.ConnectionError as exception:
            referesh_pdf_viewer = False
            botResponse = f"Please give a valid link."
            botResponse2 = "..."

        # bot response
        dispatcher.utter_message(text=botResponse)
        dispatcher.utter_message(text=botResponse2)

        if referesh_pdf_viewer:
            message = {"payload": "pdfLink", "data": paper_details_dict["pdf"]}
            dispatcher.utter_message(text="", json_message=message)

        return []
