import fitz
import json
import os
from pathlib import Path
import re
import requests
import shutil
from difflib import SequenceMatcher
from semanticscholar import SemanticScholar
from datetime import datetime

from actions.actionconstants import LOG_FOLDER, TEMPLATE_FOLDER


def _semanticScho(paper_id):
    """get semanticscholar public api results 

    Args:
        paper_id (string): can be doi, semantic scholar corpus id

    Returns:
        _ss (dict)
    """
    ss = SemanticScholar(timeout=120)
    try:
        _ss = ss.paper(paper_id)
    except:
        _ss = "null"
    return _ss


def _getSSresults(result):
    """get semanticscholar public api results and put into dict

    Args:
        result (dict)

    Returns:
        SS_dict (dict)
    """

    SS_dict = {
        "title": result["title"],
        "pdf": "null",
        "abstract": result["abstract"],
        "arxiv_num": result["arxivId"],
        "author": result["authors"],
        "booktitle": "null",
        "citations": "null",  # arxiv citation bibtex
        "citation": result["citations"],  # cites from the paper
        "paperId": result["paperId"],  # ss ID
        "doi": result["doi"],
        "field": result["fieldsOfStudy"],
        "numCitedBy": result["numCitedBy"],
        "references": result["references"],
        "keywords": result["topics"],
        "url": result["url"],
        "journal": result["venue"],
        "publisher": result["venue"],
        "year": result["year"],
        "bib": "null",
        "read_time": "null",
        "added_date": "null",
    }

    if SS_dict['arxiv_num'] != None:
        SS_dict['pdf'] = "https://arxiv.org/pdf/" + str(SS_dict['arxiv_num']) + ".pdf"
    return SS_dict


def _getArxivresults(result):
    """get arxivcheck results and put into dict

    Args:
        result (string)

    Returns:
        arxiv_dict (dict)
    """

    arxiv_dict = {
        "title": "null",
        "pdf": "null",
        "abstract": "null",
        "arxiv_num": "null",
        "author": "null",
        "booktitle": "null",
        "citation": "null",  # arxiv citation bibtex
        "citations": "null",  # cites from the paper
        "paperId": "null",  # ss ID
        "doi": "null",
        "field": "null",
        "numCitedBy": "null",
        "references": "null",
        "keywords": "null",
        "url": "null",
        "journal": "null",
        "publisher": "null",
        "year": "null",
        "bib": "null",
        "read_time": "null",
        "added_date": "null",
    }

    cite_list = result.split(",")

    for line in cite_list:
        if "title" in line:
            arxiv_dict["title"] = " ".join(_clean_line(line).split())
        if "author" in line:
            arxiv_dict["author"] = _clean_line(line)
        if "journal" in line:
            arxiv_dict["journal"] = _clean_line(line)
        if "url" in line:
            arxiv_dict["url"] = _clean_line(line)
        if "year" in line:
            arxiv_dict["year"] = _clean_line(line)
        if "publisher" in line:
            arxiv_dict["publisher"] = _clean_line(line)
        if "doi" in line:
            arxiv_dict["doi"] = _clean_line(line)
        if "booktitle" in line:
            arxiv_dict["booktitle"] = _clean_line(line)
        if "keywords" in line:
            arxiv_dict["keywords"] = _clean_line(line)

    return arxiv_dict


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


def preprocess_txt(paper_dict):
    """preprocess document text to remove unnecessary sections and save

    Args:
        URL (string): file url or local path

    Returns:
        cleaned_txt: cleaned pdf txt
        sections: table of contents
    """
    # check if URL doc is preprocessed and saved already
    # if not run preprocessing
    processed_bool = False
    paper_folder = os.path.join(LOG_FOLDER + "/papers", paper_dict['title'])
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
        res = requests.get(paper_dict['pdf'], stream=True)
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
        URL (string): url or file path to pdf

    Returns:
        paper_details_dict (dict): paper details in dictionary
    """

    paper_details_dict = {
        "title": "null",
        "pdf": "null",
        "abstract": "null",
        "arxiv_num": "null",
        "author": "null",
        "booktitle": "null",
        "citation": "null",  # arxiv citation bibtex
        "citations": "null",  # cites from the paper
        "paperId": "null",  # ss ID
        "doi": "null",
        "field": "null",
        "numCitedBy": "null",
        "references": "null",
        "keywords": "null",
        "url": "null",
        "journal": "null",
        "publisher": "null",
        "year": "null",
        "bib": "null",
        "read_time": "null",
        "added_date": "null",
    }

    ar_result = None

    # check if url or local path
    if "http" in URL:
        if "arxiv" in URL:
            if ".pdf" in URL:
                arxiv_num = URL.split("/")[-1].split(".pdf")[0]
                paper_details_dict['pdf'] = URL
            elif "arxiv." in URL:
                arxiv_num = URL.split("/")[-1].split("arxiv.")[1:][0]
            else:
                arxiv_num = URL.split("/")[-1]

            if "v" in arxiv_num:
                arxiv_num = arxiv_num.split("v")[0]

            # Method: use semantic scholar to get paper details
            paperId = "arxiv:" + arxiv_num

            result = _semanticScho(paperId)
            paper_details_dict = _getSSresults(result)

            # Method: use arxivcheck to get paper details
            cmd = "arxivcheck " + arxiv_num
            ar_result = os.popen(cmd).read()

            if not result:
                if "not found" in ar_result:
                    print("No results")
                else:
                    paper_details_dict = _getArxivresults(ar_result)

        elif "semanticscholar" in URL:
            paperId = URL.split("/")[-1]

            result = _semanticScho(paperId)
            paper_details_dict = _getSSresults(result)
        else:
            print("URL no results")

    elif "file:" in URL or "/home" in URL:
        file_path = URL.split("//")[-1]
        paper_details_dict['pdf'] = file_path
        curr_doc = fitz.open(file_path, filetype="pdf")
        if curr_doc.metadata["title"] != "":
            paper_title = curr_doc.metadata["title"]
        else:
            first_page = curr_doc.load_page(0).get_text("blocks")
            _lines = []
            for l in first_page[:3]:
                _lines.append(l[-3].replace("\n", " "))
            for l in _lines:
                if "," not in l:
                    paper_title = l
                else:
                    break
            for l in first_page:
                if "arXiv" in l[-3]:
                    ar = l[-3].split(" ")[0]
                    arxiv_num = ar.split(":")[-1].split("v", 2)[0]

                    paperId = "arxiv:" + arxiv_num

                    result = _semanticScho(paperId)
                    paper_details_dict = _getSSresults(result)
                    break

        if paper_details_dict["title"] == "null":
            cmd = "arxivcheck -t " + paper_title
            ar_result = os.popen(cmd).read()
            arxiv_dict = _getArxivresults(ar_result)

            if " ".join(paper_title.lower().split()) == " ".join(
                arxiv_dict["title"].lower().split()
            ):
                arxiv_num = arxiv_dict["url"].split("/")[-1]
                if "v" in arxiv_num:
                    arxiv_num = arxiv_num.split("v")[0]
                paperId = "arxiv:" + arxiv_num
                result = _semanticScho(paperId)
                if result != "null":
                    paper_details_dict = _getSSresults(result)
                else:
                    paper_details_dict = arxiv_dict
            else:
                print("Incorrect title")
    elif "doi:" in URL.lower():
        doi = URL.split(":")[-1]
        result = _semanticScho(doi)
        print(result['title'])
        if result != "null":
            paper_details_dict = _getSSresults(result)
        else:
            print("Doi not found")
    elif "title:" in URL.lower():
        title= " ".join(URL.split('title:')[-1].split())
        cmd = "arxivcheck -t " + title
        ar_result = os.popen(cmd).read()
        arxiv_dict = _getArxivresults(ar_result)
        print(ar_result)

        if not "not found" in ar_result and URL.lower() == " ".join(
            arxiv_dict["title"].lower().split()
        ):
            arxiv_num = arxiv_dict["url"].split("/")[-1]
            if "v" in arxiv_num:
                arxiv_num = arxiv_num.split("v")[0]
            paperId = "arxiv:" + arxiv_num
            result = _semanticScho(paperId)

            if result != "null":
                paper_details_dict = _getSSresults(result)
            else:
                print("Title search no results")

        elif not "not found":
            paper_details_dict = _getArxivresults(ar_result)

    # get bibtex
    if paper_details_dict["doi"] != None:
        try:
            cmd = "doi2bib " + paper_details_dict["doi"]
            bib = os.popen(cmd).read()
            paper_details_dict["bib"] = bib.replace("\n", "").replace("\t", "")
        except:
            paper_details_dict["bib"] = ar_result.replace("\n", "")
    elif ar_result != None:
        paper_details_dict["bib"] = ar_result.replace("\n", "")

    return paper_details_dict


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


def log_user_msg(text, session_id):
    """log unique user inputs

    Args:
        text (string): user message
        session_id (string): user session id

    Returns:
        None
    """
    user_folder = os.path.join(LOG_FOLDER + "/users", session_id + "/chat.log")
    user_msg = {
        "text": text,
        "input_time": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
    }
    write_json(user_msg, user_folder, jsonkey="chat_history")
    return None