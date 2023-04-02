import yaml
from pathlib import Path
import alsaaudio
import sys

class BotConfig:
    
    OUTPUT_DEVICE_INDEX=1
    
    def __init__(self):    
        self.conf_path = str(Path(__file__).resolve().parent.joinpath('', 'bot_config.yaml'))
        self.load_config()
            
    def load_config(self):
        with open(self.conf_path, "r") as stream:
            try:
                self.bot_config_yaml = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        self._volume = self.get_speaker_volume()[0]         
        self._gpt_model = self.bot_config_yaml['ai_personality']['gpt_model']
        self._max_tokens = int(self.bot_config_yaml['ai_personality']['max_tokens'])
        self._temperature = float(self.bot_config_yaml['ai_personality']['temperature'])
        self._initial_prompt = self.bot_config_yaml['ai_personality']['initial_prompt']
        self._voice_name = self.bot_config_yaml['voice']['voice_name']
        self._pitch = int(self.bot_config_yaml['voice']['pitch'])
        self._rate = int(self.bot_config_yaml['voice']['rate'])       
        self._show_gpt_response = self.bot_config_yaml['general']['show_gpt_response']       
        self._show_recognized = self.bot_config_yaml['general']['show_recognized']                                                          

    def save_config(self):
        self.bot_config_yaml['ai_personality']['gpt_model'] = self._gpt_model
        self.bot_config_yaml['ai_personality']['max_tokens'] = self._max_tokens
        self.bot_config_yaml['ai_personality']['temperature'] = self._temperature
        self.bot_config_yaml['ai_personality']['initial_prompt'] = self._initial_prompt
        self.bot_config_yaml['voice']['voice_name'] = self._voice_name
        self.bot_config_yaml['voice']['pitch'] = self._pitch     
        self.bot_config_yaml['voice']['rate'] = self._rate  
        self.bot_config_yaml['voice']['volume'] = self._volume  
        self.change_speaker_volume(self._volume)                 
        self.bot_config_yaml['general']['show_gpt_response'] = self._show_gpt_response  
        self.bot_config_yaml['general']['show_recognized'] = self._show_recognized          
        
        with open(self.conf_path, 'w') as stream:
            try:
                yaml.dump(self.bot_config_yaml, stream, sort_keys=False)
            except yaml.YAMLError as exc:
                print(exc)          

    def get_mixer(self, device_index):
        try:
            mixer = alsaaudio.Mixer(control='PCM', cardindex = device_index)
            return mixer
        except alsaaudio.ALSAAudioError:
            print("No such mixer", file=sys.stderr)
            
    def change_speaker_volume(self, volume):
        mixer = self.get_mixer(self.OUTPUT_DEVICE_INDEX)
        mixer.setvolume(volume)
        
    def get_speaker_volume(self):
        mixer = self.get_mixer(self.OUTPUT_DEVICE_INDEX)
        return mixer.getvolume()    
         
    @property
    def gpt_model(self):
         return self._gpt_model
       
    @gpt_model.setter
    def gpt_model(self, gpt_model):
        self._gpt_model = gpt_model         
        
    @property
    def max_tokens(self):
         return self._max_tokens
       
    @max_tokens.setter
    def max_tokens(self, max_tokens):
        self._max_tokens = int(max_tokens)     

    @property
    def temperature(self):
         return self._temperature
       
    @temperature.setter
    def temperature(self, temperature):
        self._temperature = float(temperature)    

    @property
    def initial_prompt(self):
         return self._initial_prompt
       
    @initial_prompt.setter
    def initial_prompt(self, initial_prompt):
        self._initial_prompt = initial_prompt  
        
    @property
    def volume(self):
        return self._volume
       
    @volume.setter
    def volume(self, volume):
        self._volume = int(volume)  
                
    @property
    def voice_name(self):
         return self._voice_name
       
    @voice_name.setter
    def voice_name(self, voice_name):
        self._voice_name = voice_name    
        
    @property
    def pitch(self):
         return self._pitch
       
    @pitch.setter
    def pitch(self, pitch):
        self._pitch = int(pitch)    
        
    @property
    def rate(self):
         return self._rate
       
    @rate.setter
    def rate(self, rate):
        self._rate = int(rate)    
        
    @property
    def show_gpt_response(self):
         return self._show_gpt_response
       
    @show_gpt_response.setter
    def show_gpt_response(self, show_gpt_response):
        self._show_gpt_response = show_gpt_response
        
    @property
    def show_recognized(self):
         return self._show_recognized
       
    @show_recognized.setter
    def show_recognized(self, show_recognized):
        self._show_recognized = show_recognized