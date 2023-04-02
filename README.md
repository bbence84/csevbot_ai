# Csevbot AI
A POC for a voice assistant built using Raspberry Pi, OpenAI and Azure APIs

Detailed description on the medium.com article: https://medium.com/@bbence84/how-i-built-a-3d-printed-ai-chatgpt-enabled-voice-assistant-and-what-i-learned-in-the-process-f19663c3aad8

## Prerequisites
- OpenAI account and API key
- Microsoft Azure account and Speech API key

## Installation
Recommended to install all the things in a Python Virtual Env.

## Python packages
Install all required python packages using:
pip install -r requirements.txt

## Environment variables
You need to set the following 3 environment variables for the program to work:

export OPENAI_API_KEY='openai_api_key'

export SPEECH_KEY='azure_speech_api_key'

export SPEECH_REGION='region'  
(can be e.g. westeurope)

## Running the config UI and the bot upon startup

TODO
