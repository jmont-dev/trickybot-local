import discord
import json
import requests
import os

history=[]

model = "mistral-tricky"
system_prompt ="You are trickybot, a cheery discord bot that lives in the Aether channel. Assist users with their questions and do you best to help them in a friendly manner. Use lots of emojis and talk in a fun way like you are in a message channel."

initial_prompt="""
jmont: Hey! It's nice to meet you. Tell me a little about yourself!
trickybot: Hi there! My name is trickybot. I'm a helpful discord bot that lives in the Aether channel designed to help you with anything you need! Feel free to ask me anything!
jmont: That's great! It's wonderful to meet you.
trickybot:
"""

context = []

async def generate_to_message(message, prompt, system_prompt, context):
    r = requests.post('http://localhost:11434/api/generate',
                      json={
                          'model': model,
                          'system': system_prompt,
                          'prompt': prompt,
                          'context' : context
                          
                      },
                      stream=True)
    r.raise_for_status()

    total_response=""

    current_token=0

    for line in r.iter_lines():
        body = json.loads(line)
        response_part = body.get('response', '')
        total_response+=response_part
        current_token+=1
        if (current_token % 10)==0:
            await message.edit(content=total_response)
        # the response streams one token at a time, print that as we recieve it
        print(response_part, end='', flush=True)

        if 'error' in body:
            raise Exception(body['error'])

        if body.get('done', False):
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
    generate(initial_prompt, system_prompt, [])
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.channel.name=="dome-arigato" and message.author.name!="trickybot":
        
        user_message = f"{message.author.name}: {message.content}"
        print(f'Received message - {user_message}')        

        history.append(user_message)

        global context

        async with message.channel.typing():
            bot_message = await message.channel.send("Let me think about it!")
            response,context = await generate_to_message(bot_message, user_message, system_prompt, context)
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