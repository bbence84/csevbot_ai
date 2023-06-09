from nicegui import ui
from botconfig import BotConfig
import yaml
from pathlib import Path
import os

bot_config = BotConfig()
preset_contents = []

def save_ui_config():
    bot_config.save_config()
    ui.notify('Save successful!')
    
def load_prompt_presets():
    global preset_contents  
    preset_path = str(Path(__file__).resolve().parent.joinpath('', 'ai_personalities.yaml'))
    with open(preset_path, "r") as stream:
        try:
            content = yaml.safe_load(stream)
            preset_contents = content['presets']
        except yaml.YAMLError as exc:
            print(exc)
            
def change_prompt_from_preset(preset_name):
    for preset in preset_contents:
        if (preset['name'] == preset_name):
            bot_config.initial_prompt = preset['prompt']
            

def build_config_ui():   
    global bot_config     
    global preset_contents
    
    prompt_preset_names = []
    
    for preset in preset_contents:
        prompt_preset_names.append(preset['name'])
    print(prompt_preset_names)
    
    ui.colors(primary='#3CB043')

    with ui.dialog() as dialog_reboot, ui.card():
        ui.label('Are you sure you want to reboot the device?')
        with ui.row():
            ui.button('Yes', on_click=lambda: dialog_reboot.submit('Yes'))
            ui.button('No', on_click=lambda: dialog_reboot.submit('No')) 

    async def show_confirm_reboot():
        result = await dialog_reboot
        if (result == 'Yes'):
            reboot_system()                               
    
    with ui.header(elevated=True):
        with ui.tabs() as tabs:
            # ui.tab(label='Home', name="home", icon='system')
            ui.tab(label='AI Personality', name="personality", icon='psychology')
            ui.tab(label='Voice', name="voice", icon='record_voice_over')
            ui.tab(label='System', name="system", icon='settings')
    with ui.footer():
        ui.label('Csevbot Settings - Copyright 2023 Bence Blaske')                

    with ui.tab_panels(tabs, value='personality').style('max-width: 800px; width: 100%'):
        # with ui.tab_panel('home'):
        #     welcome_label = """
        #     This is the configuration page for the CsevBot AI bot. \n
        #     You can change some of the settings that influence the behaviour and voice of the AI bot. \n
        #     Currently, there's not much validation, so be careful with changing the parameters and change them to only valid values. :)
        #     """
        #     ui.label(welcome_label)
        with ui.tab_panel('personality'):
            with ui.column():               
                ui.select(["gpt-3.5-turbo-0301","gpt-3.5-turbo","gpt-4","gpt-4-0314"], label='GPT Model Name').style('width: 200px').bind_value(bot_config, 'gpt_model')          
                with ui.row():                        
                    ui.input(label='Max tokens').bind_value(bot_config, 'max_tokens')        
                    ui.input(label='Temperature').bind_value(bot_config, 'temperature')     
                ui.select(prompt_preset_names, label='Prompt presets', on_change=lambda e: change_prompt_from_preset(e.value)).style('width: 400px')                                   
                ui.textarea(label='Initial prompt').bind_value(bot_config, 'initial_prompt').style('width: 100%')
                ui.button('Save', on_click=lambda: save_ui_config())             
        with ui.tab_panel('voice'):
            with ui.column():        
                #ui.input(label='Voice name').bind_value(bot_config, 'voice_name')
                ui.select(["en-GB-HollieNeural","en-GB-BellaNeural","en-US-AmberNeural",
                           "en-US-ChristopherNeural","en-US-JennyMultilingualNeural",
                           "de-DE-KatjaNeural","de-DE-LouisaNeural",
                           "it-IT-ElsaNeural","it-IT-GianniNeural",
                           "hu-HU-NoemiNeural","hu-HU-TamasNeural"], label='Voice name',  value=1).bind_value(bot_config, 'voice_name')
                ui.label('Volume')
                slider_volume = ui.slider(min=1, max=100, value=85).bind_value(bot_config, 'volume')
                ui.label().bind_text_from(slider_volume, 'value')    
                with ui.row().style('width: 100%'):       
                    with ui.column().style('width: 50%'):             
                        ui.label('Pitch') 
                        slider_pitch = ui.slider(min=-50, max=50).bind_value(bot_config, 'pitch')
                        ui.label().bind_text_from(slider_pitch, 'value')     
                    with ui.column().style('width: 50%'):                       
                        ui.label('Rate')  
                        slider_rate = ui.slider(min=-50, max=50).bind_value(bot_config, 'rate')
                        ui.label().bind_text_from(slider_rate, 'value')
                ui.button('Save', on_click=lambda: save_ui_config())            
        with ui.tab_panel('system'):
            with ui.column():
                ui.switch('Show recognized text on screen').bind_value(bot_config, 'show_recognized') 
                ui.switch('Show AI response text on screen').bind_value(bot_config, 'show_gpt_response')  
                ui.button('Save', on_click=lambda: save_ui_config())       
                ui.separator()                         
                ui.textarea(label='Logs').style('width: 100%')      
                with ui.row():
                    ui.button('Restart bot', on_click=lambda: restart_bot())    
                    ui.button('Stop bot', on_click=lambda: stop_bot())                        
                    ui.button('Reboot system', on_click=show_confirm_reboot)                             
                  
def stop_bot():
    ui.notify('Stopping bot...')
    os.system('sudo systemctl stop start_bot')

def restart_bot():
    ui.notify('Restarting bot...')
    os.system('sudo systemctl restart start_bot')
    
def reboot_system():
    ui.notify('Rebooting system...')
    os.system('sudo reboot')    
        
def main():
    load_prompt_presets()
    build_config_ui()   
    ui.run(title='CsevBot Settings', uvicorn_reload_includes='.py,.yaml')   
  
if __name__ in {"__main__", "__mp_main__"}:
    main()