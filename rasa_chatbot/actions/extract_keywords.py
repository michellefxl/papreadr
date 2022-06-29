from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import yake
import json
import os

from actions.actionconstants import *
from actions.utils import update_json, log_user_msg


def getKeyword(text):
    """retrieve keywords using YAKE

    Args:
        text (string): pdf text

    Returns:
        keywords_str
    """
    lang = "en"
    max_ngram_size = 3
    deduplication_thresh = 0.9
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

    keywords_str = ""
    for k in doc_keywords:
        keywords_str = keywords_str + "\n" + "- " + k

    return keywords_str


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
                doc_details = os.path.join(doc_folder, "details.log")
                doc_text = os.path.join(doc_folder, "doc_text.log")
                with open(doc_text, "r") as file:
                    # First we load existing data into a dict.
                    cleaned_txt = json.load(file)["text"]
                # get keyword from document
                keywords = getKeyword(cleaned_txt)
                keyword_dict = dict({"keywords": keywords})
                update_json(keyword_dict, doc_details)
                
                botResponse = f"YAKE extracted the keywords for you: {keywords}"
            else:
                botResponse = "🤔 I have not read any papers with you. Please add a paper"
            # bot response
            dispatcher.utter_message(text=botResponse)
        except FileNotFoundError:
            print("The file does not exist")

        return []
