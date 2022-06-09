#!/usr/bin/env python3

import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM


SUM_MODEL_PATH = "facebook/bart-large-cnn"
QNA_MODEL_PATH = "deepset/tinyroberta-squad2"
SCITLDR_MODEL_PATH = "allenai/scitldr"

try:
    os.mkdir("facebook")
except:
    print("Folder already created")

if not os.path.isdir("facebook/bart-large-cnn"):
    print(f'Downloading model...')
    summary_model = pipeline("summarization", model="facebook/bart-large-cnn")
    summary_model.save_pretrained(SUM_MODEL_PATH)
    print(f'Model saved at {SUM_MODEL_PATH}')
else:
    print(f'Model already saved at {SUM_MODEL_PATH}')


try:
    os.mkdir("deepset")
except:
    print("Folder already created")


if not os.path.isdir("deepset/roberta-base-squad2"):
    print(f'Downloading model...')
    qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")
    qa_model.save_pretrained(QNA_MODEL_PATH)
    print(f'Model saved at {QNA_MODEL_PATH}')
else:
    print(f'Model already saved at {QNA_MODEL_PATH}')
    
try:
    os.mkdir("allenai")
except:
    print("Folder already created")


if not os.path.isdir("allenai/scitldr"):
    print(f'Downloading model...')
    tokenizer = AutoTokenizer.from_pretrained("lrakotoson/scitldr-catts-xsum-ao")
    model = AutoModelForSeq2SeqLM.from_pretrained("lrakotoson/scitldr-catts-xsum-ao")
    model.save_pretrained(QNA_MODEL_PATH)
    tokenizer.save_pretrained(QNA_MODEL_PATH)
    print(f'Model saved at {SCITLDR_MODEL_PATH}')
else:
    print(f'Model already saved at {SCITLDR_MODEL_PATH}')
