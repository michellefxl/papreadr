# Papr Readr Bot
<img align="left" src="https://user-images.githubusercontent.com/100949943/174551969-848d7407-f618-4352-b1b5-9444947e5be2.png" height="150" alt="My Image">

### Hi, I am Papr Readr Bot!
Reading research papers can be a tedious and lonely task. We present Papr Readr Bot, a (chat)bot which aims to assist researchers in reading papers more effectively and with less cognitive effort by providing paper summaries, answering questions about the paper, extracting figures from the paper, taking notes, and generate citation. Papr Readr Bot demonstrates and provides hands-on experiences of various deep learning-based skills that can be integrated in useful and social conversational assistants for reading related contexts.


### Setup
1. Install packages in conda env (environment.yml, requirements.txt)
2. cd to huggingface folder and run the following script to download the models:
- [Summarization model](https://huggingface.co/facebook/bart-large-cnn) 
- [QnA model](https://huggingface.co/deepset/tinyroberta-squad2)
- [SCITLDR](https://huggingface.co/lrakotoson/scitldr-catts-xsum-ao)
```
python download_models.py
```


### Versions:
22.April 2022 - V1 [Demo paper submitted to CUI 2022](https://github.com/michellefxl/paprreadrbot/files/8554340/Papr_Readr_Bot__CUI_2022_Demo_Track_.pdf)
<p align="center">
<img src="https://user-images.githubusercontent.com/100949943/165084052-214ae06c-66c0-438d-aa18-71c21b562688.png" width="auto" height="500" alt="web_ui"/>
</p>
<p align="center"><em>Figure: Web application V1</em></p>
9.June 2022 - V2 Updated UI
<p align="center">
<img src="https://user-images.githubusercontent.com/100949943/172862973-a26fd005-4a87-422d-99a9-fe3cea65d776.png" width="auto" height="auto" alt="web_ui"/>
</p>
<p align="center"><em>Figure: Web application V2 in dark mode</em></p>

### To train rasa model:
```
rasa train
```

### To run rasa:
1. run rasa model, set TF_FORCE_GPU_ALLOW_GROWTH to True to prevent, rasa nlu modules that uses gpu to take up entire gpu:
```
TF_FORCE_GPU_ALLOW_GROWTH=true rasa run -m models --enable-api --cors "*" --debug
```
2. run rasa custom actions: 
```
rasa run actions --cors "*" --debug
```
### To access rasa through Telegram:
1. before running rasa model, run:
```
ngrok http 5005
```
2. replace webhook_url in rasa's credentials.yml with the last forwarding url that ends with '.io' and add '/webhooks/telegram/webhook'
example in credentials.yml: webhook_url: "https://NGROK_URL.io/webhooks/telegram/webhook"
3. keep ngrok running and run the rasa model

### Run web application:
1. after starting the rasa action and model, click on index.html in the ui folder to open the web application

### Main folder structure:
```
.
|
├── chat_history            # logs input url and paper details (new folder will be created inside for each paper)
├── huggingface             # folder to save downloaded huggingface models
├── papreadr_ui             # web application with pdf viewer and chat widget
├── rasa_chatbot            # rasa chatbot
├── requirements.txt        # exported pip package list
├── environment.yml         # exported conda env package list 
└── README.md
```

### Rasa chatbot folder structure:
```
.
|
├── actions                 # custom actions
│   ├── actionconstants.py  # constants: paths and model params
│   ├── utils.py            # functions
│   ├── add_doc.py         
│   ├── cite.py              
│   ├── extract_figs.py            
│   ├── extract_keywords.py            
│   ├── help.py            
│   ├── make_note.py            
│   ├── show_note.py           
│   ├── qna.py           
│   ├── summarize.py   
│   ├── scitldr.py  
│   └── ...   
├── data
│   ├── nlu.yml             # set examples for intents
│   ├── rules.yml           # fixed rules that should be followed
│   └── stories.yml         # flow/ paths for intents and actions
├── models                  # trained models
├── nlpmodels
├── tests
├── config.yml              # model training config
├── credentials.yml         # set credentials for platform access: Telegram 
├── domain.yml              # declare intents, actions, utterances
└── endpoints.yml
```

### Web application folder structure:
```
.
|
├── static                 # js, assets and templates
│   ├── css                     
│   ├── img  
│   └── js 
│       ├── components 
│       ├── lib 
│       ├── constants.js 
│       └── script.js 
├── index.html              # web application
├── Papr_Readr_Bot__CUI_2022_Demo_Track_.pdf    # project paper
├── LICENSE                 
└── README.md               
```

### Current main skills:
1. Summarization
2. Question answering
3. Figure extraction (saved locally)
4. Keywords extraction
5. Citation generation
6. Make/ show notes for specific papers (instead of notes, reviews?)
7. Help function (shows list of selectable options)
8. Scitldr, summarize abstract to one sentence
9. Paper detail extraction through semantic scholar public api and arxivcheck

### Additional skills:
- estimate time needed to read a paper based on average reading speed (250 WPM)
- show word count after summarization 

<p align="left">
<img src="https://user-images.githubusercontent.com/100949943/165086750-9518a167-b719-49a5-8a10-98b219a529f9.png" width="auto" height="600" />
</p>
<p align="left"><em>Figure: Telegram chatbot @papreadr_bot</em></p>
