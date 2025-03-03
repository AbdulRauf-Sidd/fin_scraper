import os
from mistralai import Mistral

api_key = "eMbFOheAKGHjaEE7thfEr9nkGFWvlbwi"
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model= model,
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. The user will give you finincical event names, along wth files names, and using that, And you need to classify them into the following categories:  press release, capitals market day, annual general meeting, fact cheet, esg, annalyst presentation, or other.  just give me the classifcation. no explaintation. just the classification"
        },

        {
            "role": "user",
            "content": "file name: https://www.pvh.com/-/media/Files/pvh/responsibility/PVH-CR-Report-2023.pdf     event name: pvh cr report 2023",
        },
    ]
)
print(chat_response.choices[0].message.content)