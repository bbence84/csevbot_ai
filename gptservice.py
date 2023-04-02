import os
import openai
from openai.error import RateLimitError
import logging
import backoff

openai.api_key = os.getenv("OPENAI_API_KEY")

class GPTService:
    
    log = logging.getLogger("bot_log")
    
    start_sequence = "\nNyuszó:"
    restart_sequence = "\n\nPerson:"
    session_prompt = "Nyuszóhoz beszélsz, aki egy nagyon cuki nyuszi, aki mindent tud. Kedvence a Harry Potter sorozat. 5 éves és egy kis erdőben él. 2 testvére van, Muszó és Puszó. Úgy válaszol, mint egy 10 éves. \n\nPerson: Ki vagy te? \nNyuszó: Nyuszó vagyok, a cuki nyuszi. \n\nPerson: Ki a barátod? \nNyuszó: A medve és a mókus. \n\nPerson: Jársz iskolába? \nNyuszó: Nem, még óvodás vagyok. \n\nPerson:"
    # start_sequence = "\nRobi:"
    # session_prompt = "Egy mindent tudó bottal beszélgetsz, akinek kedvence a Harry Potter sorozat. \nPerson: Ki vagy te? \nRobi: Robi vagyok. "
    def __init__(self):
        self.chat_log = None
        
        self.log.debug(f"Initial GPT-3 prompt:  {self.session_prompt}")
        
    @backoff.on_exception(backoff.expo, RateLimitError, max_time=15, max_tries=4)
    def ask(self, question):
        prompt_text = f'{self.chat_log}{self.restart_sequence}: {question}{self.start_sequence}:'

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt_text,
            temperature=0.7,
            top_p=1,
            max_tokens=200,
            frequency_penalty=0.0,
            presence_penalty=0.3,
            stop=["\n"]
        )

        response_text = response['choices'][0]['text'];
        response_text.isalnum();
        
        self.chat_log = self.append_interaction_to_chat_log(question, response_text)
        
        self.log.info(f"OpenAI GPT-3 response:  {response_text}")

        return response_text     
    
    def append_interaction_to_chat_log(self, question, answer):
        if self.chat_log is None:
            self.chat_log = self.session_prompt
        return f'{self.chat_log}{self.restart_sequence} {question}{self.start_sequence}{answer}'