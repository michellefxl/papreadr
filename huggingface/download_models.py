#!/usr/bin/env python3

import os
from transformers import pipeline


SUM_MODEL_PATH = "facebook/bart-large-cnn"
QNA_MODEL_PATH = "deepset/tinyroberta-squad2"

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


if not os.path.isdir("facebook/bart-large-cnn"):
    print(f'Downloading model...')
    qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")
    qa_model.save_pretrained(QNA_MODEL_PATH)
    print(f'Model saved at {QNA_MODEL_PATH}')
else:
    print(f'Model already saved at {QNA_MODEL_PATH}')
