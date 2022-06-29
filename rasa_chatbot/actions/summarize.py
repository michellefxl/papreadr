from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import nltk
from lexrank import LexRank
from lexrank.mappings.stopwords import STOPWORDS
from transformers import pipeline

import json
import os

from actions.actionconstants import *
from actions.utils import update_json, log_user_msg


def getSummary(cleaned_txt):
    """extractive and abstractive summarization

    Args:
        cleaned_txt (string): cleaned document text (see preprocess_text function)

    Returns:
        summary
    """
    # tokenize
    tokens = nltk.sent_tokenize(cleaned_txt)

    # extractive summarization
    lxr = LexRank(cleaned_txt, stopwords=STOPWORDS["en"])
    ex_sum = lxr.get_summary(tokens, summary_size=SUM_SIZE_1, threshold=0.1)
    ex_sum = " ".join(ex_sum)
    if len(ex_sum) > 3000:
        ex_sum = lxr.get_summary(tokens, summary_size=SUM_SIZE_2, threshold=0.1)
        ex_sum = " ".join(ex_sum)

    # abstractive summarization
    sum_model = pipeline("summarization", model=SUM_HF_MODEL, device=0)
    ab_sum = sum_model(
        ex_sum, max_length=MAX_LENGTH, min_length=MIN_LENGTH, do_sample=False
    )
    return ab_sum[0]["summary_text"]


class SummarizeDoc(Action):
    """summarize pdf

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_summarize"

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
            # take latest document url
            if len(data["paper_log"]) > 0:
                title = data["paper_log"][-1]["title"]
                doc_folder = data["paper_log"][-1]["folder"]
                doc_details = os.path.join(doc_folder, "details.log")

                # check if summary exists
                read_bool = False
                data_sum = []
                try:
                    f_in = open(
                        doc_details,
                    )
                    try:
                        data_sum = json.load(f_in)
                        summary = data_sum["summary"]
                        read_bool = True
                    except:
                        print("No summary")
                except FileNotFoundError:
                    print("The file does not exist")

                if not read_bool:
                    # get document summary
                    doc_text = os.path.join(doc_folder, "doc_text.log")
                    with open(doc_text, "r") as file:
                        # First we load existing data into a dict.
                        cleaned_txt = json.load(file)["text"]

                    # decide on summary of doc or summary of section
                    summary = getSummary(cleaned_txt)
                    title = data["paper_log"][-1]["title"]
                    summary_dic = dict({"summary": summary})
                    update_json(summary_dic, doc_details)

                    sum_ratio = round(
                        (
                            (len(cleaned_txt.split()) - len(summary.split()))
                            / len(cleaned_txt.split())
                        )
                        * 100
                    )

                    sum_word_count = len(summary.split())
                    
                    # botResponse = f"The summary from BART is {sum_ratio}% shorter than the original document."
                    # botResponse2 = f"Summary of {title}: {summary}"
                    botResponse = f"Here's a {sum_word_count} words summary of {title} from BART!"
                    botResponse2 = f"{summary}"
                else:
                    botResponse = (
                        f"Here's the summary of {title} that I remembered from BART:"
                    )
                    botResponse2 = f"{summary}"    
                # bot response
                dispatcher.utter_message(text=botResponse)
                dispatcher.utter_message(text=botResponse2)     
            else:
                botResponse = "🤔 Which paper are you reading? Please add the paper for me to summarize"
                dispatcher.utter_message(text=botResponse)
        except FileNotFoundError:
            print("The file does not exist")

        return []
