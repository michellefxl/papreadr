from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class GetHelp(Action):
    """show help options

    Args:
        Action
    """

    def name(self) -> Text:
        return "action_help"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # Web_ui selectable options
        botResponse = "Here are some cool things I can do! Just press the button and I'll do the magic."

        # bot response
        data = [
            {"title": "add pdf", "payload": "/setdoc"},
            {"title": "scitldr", "payload": "/scitldr"},
            {"title": "summary", "payload": "/summarize_doc"},
            {"title": "show figures", "payload": "/getfigs"},
            {"title": "show keywords", "payload": "/getkeywords"},
            {"title": "cite bibtex", "payload": "/getcite"},
            {"title": "make note", "payload": "/makenote"},
            {"title": "see note", "payload": "/seenote"},
        ]
        message = {"payload": "quickReplies", "data": data}
        dispatcher.utter_message(text=botResponse, json_message=message)

        # Telegram help
        # botResponse = "- add doc \n- scitldr \n- summarize \n- answer questions \n- get figures \n- get keywords \n- get citation \n- take notes \n- show notes"
        # dispatcher.utter_message(text=botResponse)

        return []
