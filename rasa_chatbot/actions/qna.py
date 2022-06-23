from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


from transformers import pipeline
import json
import os

from actions.actionconstants import *
from actions.utils import write_json, similar

def getAnswer(context, question):
    """get answer from model

    Args:
        context (string): pdf text
        question (string): user input

    Returns:
        checked_ans: list of answers with similar answers removed
    """
    qna_model = pipeline("question-answering", model=QNA_HF_MODEL, device=0)
    model_ans = qna_model(
        question=question, context=context, top_k=TOP_K_ANS, max_answer_len=MAX_ANS_LEN
    )

    top_ans = []
    for ans in model_ans:
        if "\n" in ans["answer"]:
            top_ans.append(ans["answer"].replace("\n", ""))
        else:
            top_ans.append(ans["answer"])

    checked_ans = [top_ans[0]]
    for i in top_ans:
        if similar(top_ans[0], i) < 0.7:
            checked_ans.append(i)

    return checked_ans


class AnswerQuestion(Action):
    """retrieve answer given question

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_answer_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input url
        userMessage = tracker.latest_message["text"]
        question = userMessage
        session_id = tracker.sender_id

        try:
            user_paper_log = os.path.join(LOG_FOLDER + "/users", session_id + "/paper.log")
            data = []
            cleaned_txt = ""
            try:
                f_in = open(
                    user_paper_log,
                )
                data = json.load(f_in)
                doc_folder = data["paper_log"][-1]["folder"]
                doc_text = os.path.join(doc_folder, "doc_text.log")
                with open(doc_text, "r") as file:
                    # First we load existing data into a dict.
                    cleaned_txt = json.load(file)["text"]
            except FileNotFoundError:
                print("The file does not exist")

            # TODO: add more features
            # get answer from elsewhere
            # extract section
            # get list of past documents

            # get answer from document
            answer = getAnswer(cleaned_txt, question)

            answer_str = ""
            for a in answer:
                answer_str = answer_str + "\n" + "- " + a

            qna_file = os.path.join(doc_folder, "qna.log")
            new_data = dict({"question": question, "answer": answer})
            write_json(new_data, qna_file, "doc_qna")

            if answer_str != "":
                botResponse = f"Just a heads up, ROBERTA might be wrong. \nBut anyway ROBERTA says the answers are: {answer_str}"
            else:
                botResponse = f"Sorry, I can't retrieve the answer."
        except:
            botResponse = f"Sorry, I can't retrieve the answer."

        # bot response
        dispatcher.utter_message(text=botResponse)

        return []
