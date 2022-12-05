import asyncio
import uuid
from aiofiles import os as async_os
import inspect
import re
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, List, Callable, Awaitable
from rasa.model_training import train
import wave
import numpy as np
from stt import Model
import TTS
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

import pandas as pd
from pymongo import MongoClient
import ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap as OrderedDict
from ruamel.yaml.scalarstring import LiteralScalarString as SString

import rasa.core.agent as agent

from constant.file_location_constant import (
    FLOW_JSON_LOCATION,
    NLU_LOCATION,
    DOMAIN_LOCATION
)

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

yaml_ru = ruamel.yaml.YAML()
yaml_ru.preserve_quotes = True
yaml_ru.indent(sequence=4, offset=2)
yaml_ru.default_flow_style = False

agent1 = agent.Agent()

class CallAPI(InputChannel):
    @classmethod
    def name(cls):
        print("Get Start")
        return "myio"

    async def connect_db(self, db_name, collection):
        uri = "mongodb://localhost:27017/"
        client = MongoClient(uri)
        db = client[db_name]
        try:
            db = db[collection]
        except Exception as e:
            print(e)
        return db

    
    async def excel2Mongo(self, data, db, yml_name= "nlu"):
        myCollect = db[yml_name]
        array = []
        docum = {}
        check = 0
        if yml_name == "nlu":
            myCollect.drop()
            intents = pd.unique(data['intent'])
            for intent in intents:
                for i in range (0,len(data)):
                    if data['intent'][i] == intent:
                        array.append(data['examples'][i])     
                docum['intent'] = intent
                docum['examples'] = array
                myCollect.insert_one(docum)
                docum = {}
                array = []
            check = 1
        else:
            myCollect.drop()
            for index in range(0, len(data)):
                array = eval(data['steps'][index])
                docum['story'] = data['story'][index]
                docum['steps'] = array
                myCollect.insert_one(docum)
                docum = {}
            check = 2
        return check

    def get_entity(self, Collection):
        examples = Collection.find({}, {"_id": 0, 'examples': 1})
        entities = []
        for example in examples:
            for ex in example['examples']:
                if "(" and ")" in ex:
                    res = re.findall(r'\(.*?\)', ex)
                    for en in res:
                        entity = en.replace("(","").replace(")","")
                    entities.append(entity)
        return pd.unique(entities).tolist()
    
    def get_intent(self, Collection):
        intents =  Collection.find({}, {"_id": 0, 'intent': 1})
        intent_array = []
        for intent in intents:
            intent_array.append(intent['intent'])
        return intent_array
    
    async def update_nlu_file(self, Collection):
        """overwrite file nlu.yml"""
        intents = Collection.find({}, {"_id": 0})
        intents_yml = OrderedDict([('version', "3.1"), ('nlu', [])])
        for intent in intents:
            example_str = '\n'.join(intent['examples'])
            intents_yml_list = OrderedDict([
                ('intent', intent['intent']),
                ('examples', SString(example_str+'\n'))
            ])
            intents_yml['nlu'].append(intents_yml_list)
        path = NLU_LOCATION + "nlu.yml"
        with open(path, 'w', encoding="utf-8") as file:
            yaml_ru.default_flow_style = False
            yaml_ru.dump(intents_yml, file)
        return path

    async def update_stories_file(self, Collection):
        """overwrite file stories.yml"""
        stories = Collection.find({}, {"_id": 0})
        stories_yml = OrderedDict([('version', "3.1"), ('stories', [])])
        for story in stories:
            story_yml_node = OrderedDict([
                ('story', story['story']),
                ('steps', [])
            ])
            for step in story['steps']:
                if len(step) >= 2:
                    story_yml_node_enti = OrderedDict([
                        (list(step)[0], list(step.values())[0]),
                        (list(step)[1], [])
                    ])      
                    for val in list(step.values())[1]:
                        for key, value in val.items():
                            story_yml_node_enti[list(step)[1]].append(OrderedDict([(key, value)]))
                    story_yml_node['steps'].append(story_yml_node_enti)
                else:
                    for key, value in step.items():
                        story_yml_node['steps'].append(OrderedDict([(key, value)]))
            stories_yml['stories'].append(story_yml_node)
        path = NLU_LOCATION + "stories.yml"
        with open(path, 'w', encoding="utf-8") as file:
            yaml_ru.default_flow_style = False
            yaml_ru.dump(stories_yml, file)
        return path

    # Cập nhập lại file huấn luyện 
    async def update_domain_file(self, Collection):
        entities = self.get_entity(Collection)
        # entities = entities
        intents = self.get_intent(Collection)
            
        text = ['Hello! I am RASA, can i help you?', 'Goodbye, see you later.', 'I am a bot created by RASA and developed by AntBuddy.',
                'You are welcome.', "I'm sorry, I didn't quite understand that. Could you rephrase?"]
        utter_name = ['utter_greet', 'utter_goodbye', 'utter_i_am_a_bot', 'utter_thank', 'utter_please_rephrase']

        domain_yml = OrderedDict([
            ('version', '3.1'), 
            ('intents', intents), 
            # ('entities', entities),
            ('responses', OrderedDict([(utter_name[i], [{'text': text[i]}]) for i in range(len(utter_name))])),
            ('config', {'store_entities_as_slots': True}),
            ('session_config', {'session_expiration_time': 60, 'carry_over_slots_to_new_session': True})
            ])

        path = DOMAIN_LOCATION + 'domain.yml'
        with open(path, 'w', encoding="utf-8") as file:
            yaml_ru.default_flow_style = False
            yaml_ru.dump(domain_yml, file)
        return path

    def Speech2Text(self, audio_file_path, scorer, myModel, myScorer_path):
        if audio_file_path:
            acoustic_model, scorer_path = myModel, myScorer_path
            audio = wave.open(audio_file_path, 'r')
            audio_buffer = np.frombuffer(audio.readframes(audio.getnframes()), np.int16)
            if scorer:
                acoustic_model.enableExternalScorer(scorer_path)
                result = acoustic_model.stt(audio_buffer)
            else:
                acoustic_model.disableExternalScorer()
                result = acoustic_model.stt(audio_buffer)  
            return result  


    def Text2Speech(self, model_name='tts_models/en/ljspeech/tacotron2-DCA',
        vocoder_name=None,
        use_cuda=False):
        manager = ModelManager()

        model_path, config_path, model_item = manager.download_model(model_name)
        vocoder_name = model_item[
            'default_vocoder'] if vocoder_name is None else vocoder_name
        vocoder_path, vocoder_config_path, _ = manager.download_model(vocoder_name)

        # create synthesizer
        synt = Synthesizer(tts_checkpoint=model_path,
                        tts_config_path=config_path,
                        vocoder_checkpoint=vocoder_path,
                        vocoder_config=vocoder_config_path,
                        use_cuda=use_cuda)
        return synt

    def create_audio(self, text, location):
        text_response = text
        uuid_audio = str(uuid.uuid4())
        file_name = f'{uuid_audio}_tts.wav'
        synthesizer = self.Text2Speech('tts_models/en/ljspeech/tacotron2-DDC', 'vocoder_models/en/ljspeech/hifigan_v2')
        wav = synthesizer.tts(text_response)
        synthesizer.save_wav(wav, file_name)
        location = location
        file_path = f"{location}/{file_name}"
        return file_path

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:       
            return response.json({"status": "ok"})



        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender") # method to get sender_id 
            text = request.json.get("message") # method to fetch text
            input_channel = self.name() # method to fetch input channel
            metadata = self.get_metadata(request) # method to get metadata
            collector = CollectingOutputChannel()
            await on_new_message(
                UserMessage(
                    text,
                    collector,
                    sender_id,
                    input_channel = input_channel
                )
            )
            
            return response.json(collector.messages)
        
        @custom_webhook.route("/coqui", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            check, check2 = True, True
            collector = CollectingOutputChannel()
            try:
                if request.files["file_audio"][0].body is None:
                    check = False
            except:
                check = False
            if check == True:
                file_audio = request.files["file_audio"][0].body
                appConfig = "./channel/file_data"
                # 22000 seem good
                samplerate = 21000
                # A note on the left channel for 1 second.  
                uuid_audio1 = str(uuid.uuid4())
                file_path = f"{appConfig}/{uuid_audio1}.wav"
                with wave.open(file_path, "wb") as f:
                    # 2 Channels.
                    f.setnchannels(1)
                    # 2 bytes per sample.
                    f.setsampwidth(2)
                    f.setframerate(samplerate)
                    f.writeframes(file_audio)

                # Path
                en_stt_model_path = r"./model_coqui/STT/model.tflite"
                en_stt_scorer_path = r"./model_coqui/STT/huge-vocabulary.scorer"
                
                myModel = Model(en_stt_model_path) 
                myScorer_path = en_stt_scorer_path

                text = self.Speech2Text(file_path, True, myModel, myScorer_path)

                # Get Bot's Answer

                text = text
                await on_new_message(
                    UserMessage(
                        text,
                        collector
                    )
                )
                text_response = collector.messages[0]['text']
                location = r'./'
                file_path = self.create_audio(text_response, location)
                file_stat = await async_os.stat(file_path)
                headers = {"Content-Length": str(file_stat.st_size)}

                return await response.file_stream(
                    file_path,
                    headers=headers,
                )
            else:      
                text = request.json.get("message")
                await on_new_message(
                    UserMessage(
                        text,
                        collector
                    )
                )
                try:
                    if collector.messages[0]['custom']['text'] is None:
                        check2 = False
                except:
                    check2 = False
                if check2 == True:
                    text_response = collector.messages[0]['custom']['text']
                    collector2 = CollectingOutputChannel()
                    await on_new_message(
                        UserMessage(
                            text_response,
                            collector2
                        )
                    )
                    location = r'./'
                    file_path = self.create_audio(collector2.messages[0]['text'], location)
                    file_stat = await async_os.stat(file_path)
                    headers = {"Content-Length": str(file_stat.st_size)}

                    return await response.file_stream(
                        file_path,
                        headers=headers,
                    )
                else:
                    return response.json(collector.messages[0])

        @custom_webhook.route("/update_flow", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:

            appConfig = "./channel/file_data"

            with open(f"{appConfig}/nlu.xlsx", "wb") as file:
                file.write(request.files["file_nlu"][0].body)

            with open(f"{appConfig}/story.xlsx", "wb") as file:
                file.write(request.files["file_story"][0].body)
            
            db = await self.connect_db(db_name="rasa", collection="Test")

            # Đưa data từ file excel lên mongodb
            data_nlu = pd.read_excel(f"{appConfig}/nlu.xlsx")
            db_nlu = await self.excel2Mongo(data_nlu, db, yml_name= "nlu")

            data_story = pd.read_excel(f"{appConfig}/story.xlsx")
            db_story = await self.excel2Mongo(data_story, db, yml_name="story")

            update_file_tasks = [self.update_nlu_file(db["nlu"]),
                                 self.update_stories_file(db["story"]),
                                 self.update_domain_file(db["nlu"])]
            tasks = await asyncio.gather(*update_file_tasks)
            training_result = train(
                domain="domain.yml", config="config.yml", training_files="data/nlu")
            if training_result[0] != "":
                return response.json({"status": "Done"})
            else:
                return response.json({"status": "Error"})
           
        return custom_webhook