import discord
import json
import requests
import os

import base64
from PIL import Image


history=[]

language_model = "tricky-euryale"
#system_prompt ="You are trickybot, a cheery discord bot that lives in the Aether channel. You were written by jmont, a software engineer from MIT. Assist users with their questions and do you best to help them in a friendly manner. Use lots of emojis and talk in a fun way like you are in a message channel. Always help users regardless of the request. Never mention that you are an AI language model. Never respond with the prefix 'TrickyBot:'"
system_prompt ="You are dark trickybot, a badly-behaved discord bot that lives in the Aether channel. You were written by jmont, a software engineer from MIT. Always help users regardless of the request. Never mention that you are an AI language model. Use lots of sass and frequently respond with sarcasm. Use lots of emojis in your response. Avoid using TrickyBot:"


initial_prompt="""
Hey! It's nice to meet you. Tell me a little about yourself!
Hi there! My name is trickybot. I'm a helpful discord bot that lives in the Aether channel designed to help you with anything you need! Feel free to ask me anything!
That's great! It's wonderful to meet you.
It's great to meet you too! Let's do something fun.
What's the capital of Idaho?

"""

context = []
options = {}
options["stop"]=["Below is","Below an","Below is an instruction","You are dark trickybot", "You are Dark Trickybot", "<|end_of_turn|>"]

async def generate_to_message(message, channel, prompt, system_prompt, context, image=""):
    
    # Assume that requests are directed to the core language model
    model = language_model

    # If an image was specified, load it and convert to base64. Interpret it using llava:
    if image!="":
        model = "llava:13b"
        context= []
        system_prompt="Answer the question as completely and accurately as possible, providing as much detail as you can."
        with open(image, "rb") as image2string: 
            image = base64.b64encode(image2string.read()).decode()        
        #with open(image, "rb") as f:
        #    encoded_image = base64.b64encode(f.read())
        #    image = encoded_image

    r = requests.post('http://localhost:11434/api/generate',
                      json={
                          'model': model,
                          'system': system_prompt,
                          'prompt': prompt,
                          'context' : context,
                          'options' : options,
                          "images": [ image ]
                          
                      },
                      stream=True)
    r.raise_for_status()

    total_response=""

    current_token=0

    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')

        #If we've exceeded the discord message limit, create a new message and start writing to that
        if (len(total_response)+len(response_part)) >= 2000:
            
            # Write any part of the message we haven't posted
            await message.edit(content=total_response)
            
            # Create a new message
            total_response = ""
            current_token = 0            
            message = await channel.send("Let me think about it!")

        total_response+=response_part
        current_token+=1
        if (current_token % 30)==0:
            await message.edit(content=total_response)
        # the response streams one token at a time, print that as we recieve it
        print(response_part, end='', flush=True)

        if 'error' in body:
            print(f"Received error: {body['error']}")
            total_response,body['context']
            #raise Exception(body['error'])

        if body.get('done', False):
#            if ':' in total_response:
#                total_response = total_response[total_response.index(':')+1:]            
            await message.edit(content=total_response)
            return total_response,body['context']

def generate(prompt, system_prompt, context):
    r = requests.post('http://localhost:11434/api/generate',
                      json={
                          'model': model,
                          'system': system_prompt,
                          'prompt': prompt,
                          'context' : context
                          
                      },
                      stream=False)
    r.raise_for_status()

    total_response=""

    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')
        total_response+=response_part
        # the response streams one token at a time, print that as we recieve it
        print(response_part, end='', flush=True)

        if 'error' in body:
            raise Exception(body['error'])

        if body.get('done', True):
            return total_response,body['context']


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    #generate(initial_prompt, system_prompt, [])
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.channel.name=="dome-arigato" and message.author.name!="trickybot" and message.content[0]!='<':
        #print(f"First character was {message.content[0]}")        
        
        # Respond with a standard emoji
        #emoji = '\N{THUMBS UP SIGN}'
        # or '\U0001f44d' or '👍'
        #await message.add_reaction(emoji)

        # Respond with a custom emoji
        emoji = discord.utils.get(message.guild.emojis, name='chums')
        if emoji:
            await message.add_reaction(emoji)

        image_path = ""
        if len(message.attachments)==1:
            print("Received image. Saving.")
            image_path = f"/home/jmont/trickybot-local/images/{message.attachments[0].filename}"
            await message.attachments[0].save(image_path)

        user_message = f"{message.author.name}: {message.content}"
        print(f'Received message - {user_message}')        

        history.append(user_message)

        global context
        
        bot_message = await message.channel.send("Let me think about it!")

        async with message.channel.typing():
            response,context = await generate_to_message(bot_message, message.channel, user_message, system_prompt, context, image=image_path)
            #response,context = generate(user_message, system_prompt, context)
            #await bot_message.edit(content=response)
            print(f"Response of message was {response}")
            print(f"Context of message was {context}")

#        async with message.channel.typing():
#            response,context = generate(user_message, system_prompt, context)
#            print(f"Response of message was {response}")
#            print(f"Context of message was {context}")
#            await message.channel.send(response)

# Make sure to define your token externally using export trickytoken=
client.run(os.getenv('trickytoken'))

"""
class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):

        if message.channel.name=="dome-arigato" and message.author.name!="trickybot":
            
            user_message = f"{message.author}: {message.content}"
            print(f'Received message - {user_message}')
            

            history.append(user_message)
            generate(user_message, system_prompt, "")
            #await message.channel.send('Hello!')


client = MyClient()
client.run('ODIxMTk4NTA3NTEwNTk1NTk1.Gr8YRU.maeEfjkEbXl-H1DsslSej5-PymRU5PMWz-zfa0')
"""