import os
import openai
from openai.error import RateLimitError
import logging
import backoff
import time
import re
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")

from botconfig import BotConfig
bot_config = BotConfig()



class GPTChatService:
    
    log = logging.getLogger("bot_log")
    logging.basicConfig(filename='gpt_service.log', level=logging.DEBUG, filemode='w')
    
    def __init__(self, default_language="German"):

        self.default_language = default_language        

        default_lang_prompt = f" Respond in {self.default_language} by default."
        
        self.initial_prompt = [{"role": "user", "content":bot_config.initial_prompt + default_lang_prompt }]

        self.chat_messages = self.initial_prompt
                
        self.log.debug(f"Initial ChatGPT prompt:  {self.chat_messages}")

        self.tokenizer_encoding = tiktoken.get_encoding("cl100k_base")

        # Statistics
        self.total_ai_tokens = 0        
        
    @backoff.on_exception(backoff.expo, RateLimitError, max_time=10, max_tries=2)    
    def ask(self, question):
    
        self.append_text_to_chat_log(question, True)
        
        # print('OpenAI API call started')
               
        start = time.time()

        try:
            response = openai.ChatCompletion.create(
                model=bot_config.gpt_model,
                messages=self.chat_messages ,
                max_tokens=bot_config.max_tokens,
                temperature=bot_config.temperature
            )
        except Exception as e:
            print(f"OpenAI API returned an Error")
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)          
            return ""    
        
        
                
        # print(f'OpenAI API call ended: {time.time() - start} ms')

        response_text = response['choices'][0]['message']['content'];
        response_text.isalnum();

        self.update_stats(self.chat_messages, response_text)
        
        response_text = self.adjust_response(response_text)
        
        self.append_text_to_chat_log(response_text)
        
        self.log.info(f"OpenAI ChatGPT response:  {response_text}")

        return response_text     
    
    def update_stats(self, chat_messages, response):

        start = time.time()
        
        self.total_ai_tokens += self.num_tokens_from_string(response)
        for msg in chat_messages:
            self.total_ai_tokens += self.num_tokens_from_string(msg['content'])
        print(f'Current token count: {self.total_ai_tokens}')

        print(f'Token count ended: {time.time() - start} ms')

    def get_stats(self):
        return self.total_ai_tokens
 
    def append_text_to_chat_log(self, text, is_user = True):
        role = "assistant"
        if (is_user):
            role = "user"
        self.chat_messages.append({"role": role, "content": text })
        self.log.info(f"Chat buffer:  {self.chat_messages}")
        
    def adjust_response(self, response_text):
        adjusted_response_text = response_text
        if response_text.endswith('.'): 
            word_before_last_dot = re.findall(r'\b\d+\b(?=[^\W_]*\.[^\W_]*$)', response_text)
            if word_before_last_dot:
                number_str = word_before_last_dot[0]
                sentence_without_dot = response_text[:-1] if response_text[-2] == ' ' else response_text[:-1] + ' '
                if number_str in sentence_without_dot:
                    adjusted_response_text = sentence_without_dot.replace(number_str + ".", number_str)
        return adjusted_response_text


    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        num_tokens = len(self.tokenizer_encoding.encode(string))
        return num_tokens