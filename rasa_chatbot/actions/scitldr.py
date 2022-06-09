from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from pathlib import Path
import json
import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from actions.actionconstants import *
from actions.utils import update_json

url_file = Path(URL_LOG)


def getScitldr(abstract):
    """summarize abstract to one sentence with scitldr

    Args:
        abstract (string)

    Returns:
        one line summary of abstract
    """

    tokenizer_test = AutoTokenizer.from_pretrained(SCITLDR_MODEL)
    model_test = AutoModelForSeq2SeqLM.from_pretrained(SCITLDR_MODEL)

    batch = tokenizer_test(abstract, return_tensors="pt")
    generated_ids = model_test.generate(batch["input_ids"])
    scitldr = tokenizer_test.batch_decode(generated_ids, skip_special_tokens=True)

    return scitldr[0]


class Scitldr(Action):
    """summarize abstract to one sentence

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_scitldr"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get text from history
        data = []
        try:
            f_in = open(
                URL_LOG,
            )
            data = json.load(f_in)
            # take latest document url
            doc_folder = data["url_history"][-1]["folder"]
        except FileNotFoundError:
            print("The file does not exist")

        doc_details = os.path.join(doc_folder, "details.log")

        # check if summary exists
        ab_bool = False
        data_sum = []
        try:
            f_in = open(
                doc_details,
            )
            try:
                data_sum = json.load(f_in)
                abstract = data_sum["abstract"]
                if abstract != "null":
                    ab_bool = True
            except:
                print("No abstract")
        except FileNotFoundError:
            print("The file does not exist")

        if ab_bool:
            # get scitldr
            scitldr = getScitldr(abstract)

            botResponse = f"{scitldr}"
        else:
            botResponse = f"Beep beep, please check if there's an available abstract for the paper in my folder"

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
