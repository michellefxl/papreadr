# collections of constants


LOG_FOLDER = "../chat_history"

URL_LOG = LOG_FOLDER + "/" + "url.log"
# URL_LOG = LOG_FOLDER + "/" + "url_history.txt"

CHAT_LOG = LOG_FOLDER + "/" + "chat.log"
QNA_LOG = LOG_FOLDER + "/" + "qna.log"
SUM_LOG = LOG_FOLDER + "/" + "summary.log"

# extractive summarization, number of sentences
SUM_SIZE_1 = 20
SUM_SIZE_2 = 15  # if extracted summary from first round has more than 3000 words

SUM_HF_MODEL = "../huggingface/facebook/bart-large-cnn"
# abstractive summarization, number of words
MAX_LENGTH = 130
MIN_LENGTH = 30

QNA_HF_MODEL = "../huggingface/deepset/tinyroberta-squad2"

# set model parameters
TOP_K_ANS = 3
MAX_ANS_LEN = 30

TEMPLATE_FOLDER = LOG_FOLDER + "/" + "Template_folder"

# scitldr model
SCITLDR_MODEL = "../huggingface/allenai/scitldr"
