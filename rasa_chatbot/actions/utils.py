import fitz
import json
import os
from pathlib import Path
import re
import requests
import shutil
from difflib import SequenceMatcher

from actions.actionconstants import LOG_FOLDER, TEMPLATE_FOLDER


def _get_toc(txt):
    """get table of contents from pdf text

    Args:
        txt (string): pdf text

    Returns:
        sections
    """
    splits = txt.split("\n")

    # find sections
    sections = []
    for idx in range(len(splits)):
        if len(splits[idx]) > 0:
            if (
                splits[idx][0].isupper()
                and splits[idx - 1].replace(".", "", 1).isdigit()
            ):
                if float(splits[idx - 1]) < 10:
                    sections.append([splits[idx - 1], splits[idx]])
    remove_idx = []
    for idx in range(len(sections)):
        if idx > 0:
            if (
                float(sections[idx][0]) < float(sections[idx - 1][0])
                or float(sections[idx][0]) > 10
            ):
                remove_idx.append(idx)
            else:
                if len(sections[idx][0].rsplit(".")[-1]) == 2:
                    if float(sections[idx][0].rsplit(".")[-1]) > 10:
                        remove_idx.append(idx)

    indices = sorted(remove_idx, reverse=True)
    for idx in indices:
        if idx < len(sections):
            sections.pop(idx)
    return sections


def _clean_line(line):
    """clean citation lines to remove '\n'

    Args:
        line (string)

    Returns:
        cleaned_line (string)
    """
    if "\n" in line:
        line = line.replace("\n", "")
        cleaned_line = re.findall(r"{(.*?)}", line)[0]
    else:
        cleaned_line = ""
    return cleaned_line


def preprocess_txt(URL):
    """preprocess document text to remove unnecessary sections and save

    Args:
        URL (_type_): _description_

    Returns:
        cleaned_txt: _description_
        sections: _description_
    """
    # check if URL doc is preprocessed and saved already
    # if not run preprocessing
    processed_bool = False
    paper_folder = os.path.join(LOG_FOLDER, URL.split("/")[-1].split(".pdf")[0])
    paper_text = os.path.join(paper_folder, "doc_text.log")
    if os.path.exists(paper_folder):
        if Path(paper_text).is_file():
            with open(paper_text, "r") as file:
                # First we load existing data into a dict.
                read_data = json.load(file)
            try:
                cleaned_txt = read_data["text"]
                doc_sections = read_data["chapters"]
                processed_bool = True
            except:
                print("Empty file")
    else:
        shutil.copytree(TEMPLATE_FOLDER, paper_folder)

    if not processed_bool:
        res = requests.get(URL, stream=True)
        doc = fitz.open(stream=res.content, filetype="pdf")

        opt = "text"
        all_txt = ""
        for page_index in range(len(doc)):
            all_txt += doc.load_page(page_index).get_text(opt)

        # Table of contents and get main sections
        doc_toc = doc.get_toc()
        if doc_toc == []:
            doc_toc = _get_toc(all_txt)
            doc_sections = []
            for chap in doc_toc:
                if "." in chap[0]:
                    if chap[0].split(".")[-1] != "":
                        if not int(chap[0].split(".")[-1]) > 0:
                            doc_sections.append(chap)
                else:
                    doc_sections.append(chap)
        else:
            # get_toc to sections
            doc_sections = []
            for chap in doc_toc:
                splits = chap[1].split(" ", 1)
                doc_sections.append([splits[0], splits[-1]])

        # clean document
        # remove acknowledgements, references, tables
        try:
            split_txt = re.split("(" + "Acknowledgements" + ")", all_txt)
            top_txt = split_txt[0]
        except:
            split_txt = re.split("(" + "References" + ")", all_txt)
            top_txt = split_txt[0]

        # remove table and other non important texts
        split_txt = top_txt.split("\n")

        cleaned_txt = ""
        for line in split_txt:
            if len(line.split(" ")) > 2:
                line = line + "\n"
                cleaned_txt += line

        new_data = dict({"chapters": doc_sections, "text": cleaned_txt})
        update_json(new_data, paper_text)

    return cleaned_txt, doc_sections


def get_details(URL):
    """reads pdf metadata or citation to retrieve doc details

    Args:
        URL (string): url to pdf

    Returns:
        title, author, journal, url, year, publisher, doi, booktitle, keywords
    """
    title = "null"
    author = "null"
    journal = "null"
    url = "null"
    year = "null"
    publisher = "null"
    doi = "null"
    booktitle = "null"
    keywords = "null"
    citation = "null"
    arxiv_num = "null"

    res = requests.get(URL, stream=True)
    curr_doc = fitz.open(stream=res.content, filetype="pdf")

    if curr_doc.metadata["title"] != "":
        title = curr_doc.metadata["title"]
    else:
        print(URL)
        if ".pdf" in URL:
            arxiv_num = URL.split("/")[-1].split(".pdf")[0]
        elif "arXiv." in URL:
            arxiv_num = URL.split("/")[-1].split("arXiv.")[1:][0]
        else:
            arxiv_num = URL.split("/")[-1]
        cmd = "arxivcheck " + arxiv_num
        result = os.popen(cmd).read()

        cite_list = result.split(",")
        # save reformatted details in details.log

        for line in cite_list:
            if "title" in line:
                title = _clean_line(line)
            if "author" in line:
                author = _clean_line(line)
            if "journal" in line:
                journal = _clean_line(line)
            if "url" in line:
                url = _clean_line(line)
            if "year" in line:
                year = _clean_line(line)
            if "publisher" in line:
                publisher = _clean_line(line)
            if "doi" in line:
                doi = _clean_line(line)
            if "booktitle" in line:
                booktitle = _clean_line(line)
            if "keywords" in line:
                keywords = _clean_line(line)

        citation = result.replace("\n", "")

    return (
        title,
        author,
        journal,
        url,
        year,
        publisher,
        doi,
        booktitle,
        keywords,
        citation,
        arxiv_num,
    )


def write_json(new_data, filename, jsonkey="url_history"):
    """append to log (JSON format)

    Args:
        new_data (json): new json data
        filename (string): file to save new data
    """
    with open(filename, "r+") as file:
        # First we load existing data into a dict
        file_data = json.load(file)
        # Join new_data with file_data
        file_data[jsonkey].append(new_data)
        # Sets file's current position at offset
        file.seek(0)
        # convert back to json
        json.dump(file_data, file, indent=4)


def update_json(new_data, filename):
    """update log (JSON format)

    Args:
        new_data (json): new json data
        filename (string): file to save new data
    """
    with open(filename, "r+") as file:
        # First we load existing data into a dict
        file_data = json.load(file)
        # Change value of keys
        file_data.update(new_data)
        # Sets file's current position at offset
        file.seek(0)
        # convert back to json
        json.dump(file_data, file, indent=4)


def get_read_time(text):
    """estimate time needed to read text (250 WPM)

    Args:
        text (string): cleaned text from document

    Returns:
        est_time: estimated reading time
    """
    WPM = 250.0
    text_list = text.split()
    est_time = round(len(text_list) / WPM)
    return est_time


def similar(a, b):
    """check for similar answers

    Args:
        a (string): answer 1
        b (string): answer 2

    Returns:
        degree of similarity
    """
    return SequenceMatcher(None, a, b).ratio()
