To running this Rasa, you need:

---------------------------
Install requiments (recomment using python 3.7.15):
* > conda create -n env python=3.7.15
* > cd AntBot-Rasa
* > pip install -r requirements.txt
----------------------
Install models:
* [ziplink](https://drive.google.com/drive/folders/1do-OoHGCNz63VBuYcEUdcdodtfry0nqH): Dowload and unzip the models.
* Drop 2 folder (models, model_coqui) into the path AntBot-Rasa/.
----------------------------
Prepare 2 command line:
* commandline 1: rasa run actions
* commandline 2: rasa run --enable-api --credentials ./credentials.yml --debug
----------------------------
Test rasa demo which Postman: 
* Rasa response is default:

  1.**utter_greet**: Hello! I am RASA, can i help you?

  2.**utter_goodbye**: Goodbye, see you later.

  3.**utter_i_am_a_bot**: I am a bot created by RASA and developed by AntBuddy.

  4.**utter_thank**: You are welcome.
-----------------------------
**If you want rasa train with a new data, you need to connect with mongoDB** *(line 54, channel/custom_connector.py)*:
* Get data from file excel(nlu, story) -> save in mongoDB -> Get data from mongoDB. 
* Use URL: [http://localhost:5005/webhooks/myio/update_flow](http://localhost:5005/webhooks/myio/update_flow) then Post 2 excel file (include: nlu, story). After that, the new data (nlu, story) and domain file will in folder data. You need to move domain.yml outside and replace an old domain file. Train with new data to get new model.
[![post-file.png](https://i.postimg.cc/j2k8VTNv/post-file.png)](https://postimg.cc/JHZ3J9pB)
-----------------------------------

* If you want to check bot response: Use URL: [http://localhost:5005/webhooks/myio/coqui](http://localhost:5005/webhooks/myio/coqui) 
  
1. Post with audio file (must be .wav): The bot will respond with sound.
  [![post-audio.png](https://i.postimg.cc/DzyXtMQY/post-audio.png)](https://postimg.cc/182XFMjp)
-------------------------
  2. Post with message: if in message have "to tts" bot will respond with sound.
  [![Screenshot-2022-12-02-154535.png](https://i.postimg.cc/kgVrfnzj/Screenshot-2022-12-02-154535.png)](https://postimg.cc/4YTF3TJt)
-------------------------
  3. Post with message: if in message have no "to tts" bot will send the response as an audio file.
  [![Capture.png](https://i.postimg.cc/RhxCxw8V/Capture.png)](https://postimg.cc/YG8B1LMJ)
