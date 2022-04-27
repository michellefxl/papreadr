# Papr Readr Bot

### Versions:
22.April 2022 - V1 [Demo paper submitted to CUI 2022](https://github.com/michellefxl/paprreadrbot/files/8554340/Papr_Readr_Bot__CUI_2022_Demo_Track_.pdf)

<p align="center">
<img src="https://user-images.githubusercontent.com/100949943/165084052-214ae06c-66c0-438d-aa18-71c21b562688.png" width="auto" height="500" alt="web_ui"/>
</p>
<p align="center"><em>Figure: Web application V1</em></p>

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

### Folder structure:
```
|
├── actions                 # custom actions
│   ├── add_doc.py          
│   ├── cite.py              
│   ├── extract_figs.py            
│   ├── extract_keywords.py            
│   ├── help.py            
│   ├── make_note.py            
│   ├── show_note.py           
│   ├── qna.py           
│   ├── summarize.py            
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

### Current main skills:
1. Summarization
2. Question answering
3. Figure extraction (saved locally)
4. Keywords extraction
5. Citation generation
6. Make/ show notes for specific papers (instead of notes, reviews?)
7. Help function (shows list of selectable options) [not implemented on Telegram yet]

### Additional skills:
- estimate time needed to read a paper based on average reading speed (250 WPM)
- show amount of content reduced after summarization 

### TB implemented:
1. Translation 
2. Style transfer
3. ASR + TTS
4. Web search (open browser in new page)
5. Knowledge graph generation (connectedpapers)
6. Section extraction/ summarization
7. Multimodal interaction: use camera + hand pose estimation to locate region of interest on paper

<p align="left">
<img src="https://user-images.githubusercontent.com/100949943/165086750-9518a167-b719-49a5-8a10-98b219a529f9.png" width="auto" height="600" />
</p>
<p align="left"><em>Figure: Telegram chatbot @papreadr_bot</em></p>
