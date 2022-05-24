import os
import openai
from IPython.display import *
from ipywidgets import *

@interact(query = widgets.Textarea(
    value='How tall is Mount Everest?',
    placeholder='Ask Gary a question',
    description='Question:',
    continuous_update = False))
def get_answer(query):
    openai.api_key = "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"
    response = openai.Completion.create(
      engine="text-davinci-002",
      prompt= query,
      max_tokens=4000 - len(query),
      temperature=0,
      frequency_penalty=0,
      presence_penalty=0,
      best_of = 1
    )
    txt = response["choices"][0]["text"][2:]
    display(Markdown(txt))