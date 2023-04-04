import os
import azure.cognitiveservices.speech as speechsdk
import time
import logging
import argparse
import RPi.GPIO as GPIO
import textwrap
import re

# Translations
trans_hu = {"listening" : "FÜLEL", "thinking" : "GONDOL", "speaking" : "BESZÉL", "silent":"CSENDBEN", "lang": "Hungarian"}
trans_en = {"listening" : "LISTENING", "thinking" : "THINKING", "speaking" : "SPEAKING", "silent":"SILENT", "lang": "English"}
trans_de = {"listening" : "HÖREN", "thinking" : "DENKEN", "speaking" : "SPRECHEN", "silent":"STILL", "lang": "German"}
translation = {}
translation["hu"] = trans_hu
translation["en"] = trans_en
translation["de"] = trans_de

# Local classes
from utils import Utils
utils = Utils()

from botconfig import BotConfig
bot_config = BotConfig()

from gptchatservice import GPTChatService

from lcdservice_color_ili import LCDServiceColor
lcd_service = LCDServiceColor()

# Set API keys and API settings
speech_key, service_region = os.environ.get('SPEECH_KEY'), os.environ.get('SPEECH_REGION'), 
speech_lang, speech_voice = "hu-HU", "hu-HU-NoemiNeural"

# Audio HW settings
output_device_name="sysdefault:CARD=UACDemoV10"
input_device_name="hw:CARD=WEBCAM"
mute_mic_during_tts = True

# Global variable for stopping execution
done = False 
listening = True
thinking = False
speaking = False

# Statistics
total_tts_duration = 0
total_stt_chars = 0
program_start_time = 0

# Method to call once recognition ends
def stop_cb(evt):
    speech_recognizer.stop_continuous_recognition()
    global done
    done= True

def check_single_char_dot(string):
    pattern = r'^[a-zA-Z0-9]\.'
    match = re.search(pattern, string)
    if match:
        return True
    else:
        return False
    
# Speech to Text utterance / command recognition finished event    
def recognized(evt: speechsdk.SpeechRecognitionEventArgs):

    try:

        global thinking
        global speaking
        global total_stt_chars

        if (speaking == True or thinking == True):
            return;
        
        stt_text = evt.result.text
        
        if stt_text == "" or check_single_char_dot(stt_text): return
        print(f"Recognized (len: {len(stt_text)}): {stt_text}")
        total_stt_chars += len(stt_text)

        if (mute_mic_during_tts): utils.mute_mic(device_name=input_device_name)
        
        change_mood_thinking(stt_text)
           
        thinking = True
        response_text = gpt_service.ask(stt_text)
        #print("AI response: ", response_text)
        thinking = False
        
        change_mood_talking(response_text)
        time.sleep(0.5) 
        
        speak_text(response_text)
                
        if (mute_mic_during_tts): utils.unmute_mic(device_name=input_device_name)
        
        if (listening == False):
            return
        
        print("Speak!")

        lcd_service.draw_face(face=LCDServiceColor.FACE_LISTEN, icon=LCDServiceColor.ICON_MIC, additional_text=translation[ui_lang]['listening'])
        
    except Exception as e:
        if hasattr(e, 'message'):
            print(e.message)
        else:
            print(e)          
        return "" 

def change_mood_thinking(top_text):
    wrapper = textwrap.TextWrapper(width=70)
    text_wrapped = wrapper.fill(text=top_text)
    if (bot_config.show_recognized == False): 
        text_wrapped = ''
    # lcd_service.draw_icon(icon=LCDService.ICON_LOAD, additional_text="AI")
    lcd_service.draw_face(face=LCDServiceColor.FACE_THINK, icon=LCDServiceColor.ICON_LOAD, additional_text=translation[ui_lang]['thinking'], top_small_text=text_wrapped)

def change_mood_talking(top_text):
    wrapper = textwrap.TextWrapper(width=70)
    text_wrapped = wrapper.fill(text=top_text)
    if (bot_config.show_gpt_response == False):
        text_wrapped = ''    
    lcd_service.draw_face(face=LCDServiceColor.FACE_TALK, icon=LCDServiceColor.ICON_SPEAKER, additional_text=translation[ui_lang]['speaking'], top_small_text=text_wrapped)
       
        
def speak_text(text):
    global speaking
    global total_tts_duration
    
    # Finally, start the Azure TTS synthesis 
    # Use SSML to set speaking rate and pitch
    text_ssml = f"<speak version='1.0' xml:lang='{speech_lang}'><voice xml:lang='{speech_lang}' xml:gender='Female' name='{speech_voice}'><prosody volume='+30%' rate='{speech_rate}%' pitch='{speech_pitch}%'>{text}</prosody></voice></speak>"
            
    speaking = True    
    result = speech_synthesizer.speak_ssml_async(text_ssml).get()
    sleep_duration = result.audio_duration.microseconds / 1000000
    time.sleep(sleep_duration)
    print(f"AI response ({result.audio_duration.seconds} sec): {text}")
    total_tts_duration += result.audio_duration.seconds
    speaking = False
        
# Register speech recognizer events, e.g. when an utterance is recognized
def set_speech_recognizer_events():
    speech_recognizer.recognized.connect(recognized)
    speech_recognizer.session_started.connect(lambda evt: print('RECOGNIZE STARTED {}'.format(evt)))    
    speech_recognizer.session_stopped.connect(lambda evt: print('RECOGNIZE STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('RECOGNIZE CANCELED {}'.format(evt)))

def run_ai():

    global program_start_time

    set_speech_recognizer_events()

    # Start continous speech recognition
    if (mute_mic_during_tts): utils.unmute_mic(device_name=input_device_name)

    program_start_time = time.time()

    speech_recognizer.start_continuous_recognition()   
    print("Speak!")
    lcd_service.draw_face(face=LCDServiceColor.FACE_LISTEN, icon=LCDServiceColor.ICON_MIC, additional_text=translation[ui_lang]['listening'])
    while not done:
        time.sleep(.5)

def check_internet():
        
    logging.basicConfig(filename='gpt_service.log', level=logging.DEBUG, filemode='w')
    log = logging.getLogger("bot_log")    
    log.info("Checking internet connection")
    if (utils.has_internet() == True):
        return
        
    time.sleep(1)

    while not utils.has_internet():
        lcd_service.draw_large_icon(LCDServiceColor.ICON_ERROR, "No internet!")
        time.sleep(1)
    
    lcd_service.draw_large_icon(LCDServiceColor.ICON_WIFI, "Internet connected! :)")
    time.sleep(1)
    lcd_service.clear_screen()    
    
def init_azure():

    global speech_voice
    global speech_lang
    global ui_lang
    
    speech_voice = bot_config.voice_name
    speech_lang = speech_voice[0:5]
    ui_lang = speech_voice[0:2]
   
    global speech_rate
    global speech_pitch
    
    speech_rate = bot_config.rate
    speech_pitch = bot_config.pitch
    # Init Azure Text to Speech & Speech to Text configuration
    
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region, speech_recognition_language=speech_lang)
    speech_config.speech_synthesis_voice_name = speech_voice
    audio_config_output = speechsdk.audio.AudioOutputConfig(device_name=output_device_name)
    audio_config_input = speechsdk.audio.AudioConfig(device_name=input_device_name)

    # Create speech recognizer
    global speech_recognizer
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config_input)

    # Create speech synthesizer
    global speech_synthesizer
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config_output)

    # Set to reuse speech synthesizer HTTP connection 
    connection = speechsdk.Connection.from_speech_synthesizer(speech_synthesizer)
    connection.open(True)
    
def init_gpio():
    GPIO.setmode(GPIO.BCM) # Use physical pin numbering
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    GPIO.add_event_detect(15,GPIO.RISING,callback=button_pushed, bouncetime=500) # Setup event on pin 10 rising edge
    
    
def button_pushed(channel):

    global thinking
    if (thinking == True):
        return
    
    global listening
    listening = not listening
    global speech_recognizer
    global speech_synthesizer
    if (listening == True):
        lcd_service.draw_face(face=LCDServiceColor.FACE_LISTEN, icon=LCDServiceColor.ICON_MIC, additional_text=translation[ui_lang]['listening'])
        #set_speech_recognizer_events()
        speech_recognizer.start_continuous_recognition()   
    if (listening == False):
        lcd_service.draw_face(face=LCDServiceColor.FACE_SILENT, icon=LCDServiceColor.ICON_MIC_OFF, additional_text=translation[ui_lang]['silent'])  
        speech_recognizer.stop_continuous_recognition()  
        speech_synthesizer.stop_speaking()


def init_ai():
    global gpt_service
    gpt_service = GPTChatService(translation[ui_lang]['lang'])
    print(translation[ui_lang]['lang'])

def end_program(write_stats = True):

    lcd_service.clear_screen()
    GPIO.cleanup()     

    if (write_stats):
        global gpt_service
        global program_start_time
        global total_stt_chars
        global total_tts_duration

        program_end_time = time.time()
        program_run_duration = program_end_time - program_start_time
        print(f'STATS: program duration: {program_run_duration} seconds')
        print(f'STATS: total TTS duration: {total_tts_duration} sec')
        print(f'STATS: total STT characters: {total_stt_chars} chars')    
        print(f'STATS: total OpenAI API tokens: {gpt_service.get_stats()}')        
    


def main():
    try:
        init_gpio()
        check_internet()
        init_azure()        
        init_ai()        
        run_ai() 
    except KeyboardInterrupt:
        end_program()   
    finally:
        end_program()       
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--audio_input", help='Audio input device')
    parser.add_argument("-o", "--audio_output", help='Audio output device')
    parser.add_argument("-r", "--record_card", help='Audio record card')
    args = parser.parse_args()
    if (args.audio_input is not None):
        input_device_name=args.audio_input
        print(f"Audio input override: {input_device_name}")
    if (args.audio_output is not None):
        output_device_name=args.audio_output  
        print(f"Audio output override: {output_device_name}")  
        
    main()
