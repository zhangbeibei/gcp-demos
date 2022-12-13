from google.cloud import speech
from math import ceil
import numpy as np
 
# Instantiates a client
client = speech.SpeechClient()
 
'''
auto transcribe from two languages
'''
def transcribe_speech(audio_gcs_uri, language_list):
   audio = speech.RecognitionAudio(uri=audio_gcs_uri)
   if (len(language_list) == 2):
       config = speech.RecognitionConfig(
           encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
           sample_rate_hertz=16000,
           language_code=language_list[0],
           alternative_language_codes=[language_list[1]],
       )
   else:
       config = speech.RecognitionConfig(
           encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
           sample_rate_hertz=16000,
           language_code=language_list[0],
       )
 
   # Detects speech in the audio file
   response = client.recognize(config=config, audio=audio)
 
   transcript = None
   confidence = None
   languageCode = None
 
   for result in response.results:
       transcript = result.alternatives[0].transcript
       confidence = result.alternatives[0].confidence
       languageCode = result.language_code
  
   if not confidence is None:
       return {"transcript":transcript, "confidence":confidence, "languageCode":languageCode}
   else:
       return None
 
 
'''
auto transcribe from multi languages
'''
def auto_detect_multi_language(audio_gcs_uri, language_list):
 
   result_list = []
   confidence_list = []
 
   group_count = ceil (len(language_list)/2)
   language_array = np.array(language_list)
   language_group = np.array_split(language_array, group_count)
   for language in language_group:
       result_dict = transcribe_speech(audio_gcs_uri, language)
       if not result_dict is None:
           result_list.append(result_dict)
           confidence_list.append(result_dict["confidence"])
  
   index = confidence_list.index(max(confidence_list))
   return result_list[index]
 
 
# Example name of the audio file to transcribe, please replace it to your gcs uri
audio_gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
# Example Language list needed to be detected, please replace it to your language list
language_list = ["de-DE", "fr-FR", "it-IT", "es-ES", "pt-PT", "ru-RU", "ru-RU"]
 
auto_detect_result = auto_detect_multi_language(audio_gcs_uri, language_list)
print (auto_detect_result)