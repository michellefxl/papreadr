from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import yake
import json
import os

from actions.actionconstants import *
from actions.utils import log_user_msg


def getKeyword(text):
    """retrieve keywords using YAKE

    Args:
        text (string): pdf text

    Returns:
        keywords_str
    """
    lang = "en"
    max_ngram_size = 3
    deduplication_thresh = 0.5
    keyword_n = 10

    custom_kw_extractor = yake.KeywordExtractor(
        lan=lang,
        n=max_ngram_size,
        dedupLim=deduplication_thresh,
        top=keyword_n,
        features=None,
    )
    keywords = custom_kw_extractor.extract_keywords(text)

    doc_keywords = []
    for keyword, score in keywords:
        doc_keywords.append(keyword)

    keywords_list = []
    for k in doc_keywords:
        keywords_list.append({'topic': k})

    return keywords_list


class GetKeyword(Action):
    """retrieve keywords of pdf

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_extractkeyword"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input url
        userMessage = tracker.latest_message["text"]
        session_id = tracker.sender_id

        log_user_msg(userMessage, session_id)

        user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")
        data = []
        cleaned_txt = ""
        try:
            f_in = open(
                user_paper_log,
            )
            data = json.load(f_in)

            if len(data["paper_log"]) > 0:
                doc_folder = data["paper_log"][-1]["folder"]
                doc_text = os.path.join(doc_folder, "doc_text.log")
                with open(doc_text, "r") as file:
                    # First we load existing data into a dict.
                    cleaned_txt = json.load(file)["text"]
                    file.close()

                paper_details = []
                doc_details = os.path.join(doc_folder, "details.log")
                f_in = open(
                    doc_details
                )
                paper_details = json.load(f_in)
                f_in.close()

                if paper_details['keywords'] != "null" and paper_details['keywords'] != []:
                    keywords_str = ""
                    for i in paper_details['keywords']:
                        keywords_str = keywords_str + "\n- " + i['topic']
                    botResponse = f"Keywords from the paper: {keywords_str}"
                else:
                    # get keyword from document
                    keyword_list = getKeyword(cleaned_txt)
                    # update keywords in details.log
                    with open(doc_details, "r") as file:
                        # First we load existing data into a dict
                        file_data = json.load(file)
                        file.close()
                    with open(doc_details, "w") as file:
                        # Change value of keys
                        file_data['keywords'] = keyword_list
                        # convert back to json
                        json.dump(file_data, file, indent=4)
                        file.close()

                    keywords_str = ""
                    for i in keyword_list:
                        keywords_str = keywords_str + "\n- " + i['topic']
                    botResponse = f"YAKE extracted the keywords for you: {keywords_str}"
            else:
                botResponse = ("🤔 I have not read any papers with you. Please add a paper")

            # bot response
            dispatcher.utter_message(text=botResponse)
        except FileNotFoundError:
            print("The file does not exist")

        return []
