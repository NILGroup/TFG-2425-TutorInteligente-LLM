import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") )

def ask(context, question="", _temperature = 0.3, _model= "gpt-4o-mini"):

    completion = client.chat.completions.create(
        model= _model,
        messages=[
            {
                "role": "system",
                "content": context
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature= _temperature,
    )
    return completion.choices[0].message.content
