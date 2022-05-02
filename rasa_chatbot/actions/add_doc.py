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

from datetime import datetime
from pathlib import Path
from datetime import datetime
import json
import os
import shutil

from actions.actionconstants import URL_LOG, LOG_FOLDER, TEMPLATE_FOLDER
from actions.utils import (
    update_json,
    write_json,
    get_read_time,
    preprocess_txt,
    get_details,
)

URL_LOG = Path(URL_LOG)


class SetDoc(Action):
    """add paper through url
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

        # get user input url
        userMessage = tracker.latest_message["text"]

        try:
            # check if valid url
            # SKIPPED this because of bottleneck
            # response = requests.get(userMessage)

            # user input pdf link
            doc_url = userMessage

            added_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

            # check if url exists
            data = []
            try:
                f_in = open(
                    URL_LOG,
                )
                data = json.load(f_in)
            except FileNotFoundError:
                print("The file does not exist")

            read_bool = False
            for data_line in data["url_history"]:
                if doc_url == data_line["url"]:
                    read_bool = True
                    doc_title = data_line["title"]

            # preprocess and save text and chapters
            cleaned_txt, doc_sections = preprocess_txt(doc_url)

            # estimate reading time (250 WPM)
            est_read_time = get_read_time(cleaned_txt)

            if not read_bool:
                (
                    doc_title,
                    doc_author,
                    doc_journal,
                    url,
                    doc_year,
                    doc_publisher,
                    doc_doi,
                    doc_booktitle,
                    doc_keywords,
                    bibtex,
                    arxiv_num,
                ) = get_details(doc_url)

                botResponse = f"So you are reading {doc_title}."
                botResponse2 = f"It'll take an average person (250 WPM) {est_read_time} minutes to finish this paper. I bet you can read faster than that!"
            else:
                botResponse = f"Oh, so you are reading {doc_title} again."
                botResponse2 = f"It'll take an average person (250 WPM) {est_read_time} minutes to finish this paper. Are you sure about reading it again?"

            # check if same title doc exists with different urls
            saved_bool = False
            for data_line in data["url_history"]:
                if doc_title == data_line["title"]:
                    saved_bool = True

            if not saved_bool:
                doc_folder = os.path.join(LOG_FOLDER, arxiv_num)
                doc_details = os.path.join(doc_folder, "details.log")

                # save data to file
                collected_data = dict(
                    {
                        "title": doc_title,
                        "url": doc_url,
                        "doi": doc_doi,
                        "year": doc_year,
                        "author": doc_author,
                        "publisher": doc_publisher,
                        "journal": doc_journal,
                        "booktitle": doc_booktitle,
                        "keywords": doc_keywords,
                        "read_time": est_read_time,
                        "bibtex": bibtex,
                        "added_date": added_time,
                    }
                )

                url_history = dict(
                    {
                        "title": doc_title,
                        "url": doc_url,
                        "folder": doc_folder,
                        "added_date": added_time,
                    }
                )

                try:
                    # check if folder exists and update paper details/ url history
                    if os.path.exists(doc_folder):
                        update_json(collected_data, doc_details)
                    else:
                        shutil.copytree(TEMPLATE_FOLDER, doc_folder)
                        update_json(collected_data, doc_details)
                    if URL_LOG.is_file():
                        write_json(url_history, URL_LOG)
                except FileNotFoundError:
                    print("The file does not exist")

        except requests.ConnectionError as exception:
            botResponse = f"Please give a valid link."
            botResponse2 = "..."

        # bot response
        dispatcher.utter_message(text=botResponse)
        dispatcher.utter_message(text=botResponse2)

        return []
