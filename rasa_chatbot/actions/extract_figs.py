from typing import Any, Text, Dict, List
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import fitz
import requests
import io
import os
from pathlib import Path
from PIL import Image
import json

from actions.actionconstants import URL_LOG

URL_LOG = Path(URL_LOG)


def getFigs(URL, fig_folder):
    """extract figures from pdf and save

    Args:
        URL (string): pdf url
        fig_folder (string): path to figures folder
    """
    # open the file
    res = requests.get(URL, stream=True)
    doc = fitz.open(stream=res.content, filetype="pdf")

    try:
        os.mkdir(fig_folder)
    except:
        pass

    # iterate over PDF pages
    for page_index in range(len(doc)):

        # get the page itself
        page = doc[page_index]
        image_list = page.get_images()

        # printing number of images found in this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print("[!] No images found on page", page_index)

        for image_index, img in enumerate(page.get_images(), start=1):

            # get the XREF of the image
            xref = img[0]

            # extract the image bytes
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # plt.imshow(image_bytes)
            pix = fitz.Pixmap(doc, xref)

            if pix.n < 5:
                pix.save(f"{fig_folder}/{xref}.png")
            else:
                pix1 = fitz.open(fitz.csRGB, pix)
                pix1.save(f"{fig_folder}/{xref}.png")

                pix1 = None
            pix = None

            # # get the image extension
            # image_ext = base_image["ext"]


class ExtractFigs(Action):
    def name(self) -> Text:
        return "action_extractfigs"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # get user input url
        userMessage = tracker.latest_message["text"]

        # check if valid url
        try:
            # get url from history
            data = []
            try:
                f_in = open(
                    URL_LOG,
                )
                data = json.load(f_in)
                doc_url = data["url_history"][-1]["url"]
                doc_folder = data["url_history"][-1]["folder"]
                fig_folder = os.path.join(doc_folder, "figures")
            except FileNotFoundError:
                print("The file does not exist")

            # get figures from document
            getFigs(doc_url, fig_folder)

        except:
            botResponse = f"Sorry, I can't do it."

        if len(os.listdir(fig_folder)) > 0:
            botResponse = f"I have extracted and saved the figures for you:"
            # bot response
            dispatcher.utter_message(text=botResponse)

            img_paths = [os.path.join(fig_folder, x) for x in os.listdir(fig_folder)]
            for imgp in img_paths:
                print(imgp)
                dispatcher.utter_message(image=imgp)
        else:
            botResponse = f"Oops, no figures extracted."
            dispatcher.utter_message(text=botResponse)

        return []
