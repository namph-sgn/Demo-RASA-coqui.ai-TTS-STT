# #!/usr/bin/python

# # -*- coding: utf8 -*-

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import datetime as dt
# import sys
# sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
# sys.stdin = codecs.getreader('utf_8')(sys.stdin)

import numpy as np
from stt import Model

import TTS
from pathlib import Path
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

import wave


class ActionTextToSpeech(Action):
    def name(self) -> Text:
        return "action_TTS"


    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        text_input = text.lower()

        if "to tts" in text_input:
            index = text_input.index("to tts")
            text_tts = text.replace(text[index:index+6],"")
            text = text_tts.strip()
            custom_json = {
                "type": "TTS",
                "text": text
            }
            dispatcher.utter_custom_json(custom_json)
        else:
            dispatcher.utter_message("Sorry I didn't get that. Can you rephrase?")
        return []





