import os
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY ") )

def ask(context, previous_info, question):

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": context},
            {
                "role": "user",
                "content": question
            }
        ]
    )
    return completion.choices[0].message.content
