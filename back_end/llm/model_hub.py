# dependencies
# import transformers
# from transformers import AutoTokenizer
# import torch
from typing import Union, List
from dotenv import load_dotenv
import google.generativeai as genai
import os

# class HuggingfaceModel(object):
#     def __init__(self, model_url:str, context_length:int):
#         self.tokenizer = AutoTokenizer.from_pretrained(model_url)
#         self.pipeline = transformers.pipeline(
#             task ="text-generation",
#             model = model_url,
#             torch_dtype = torch.float32,
#             device_map = "auto",
#         )
#         self.context_length = context_length
        
#     def __call__(self,input_prompt: Union[str, List[str]])->Union[str, List[str]]:
#         sequences = self.pipeline(
#             input_prompt,
#             do_sample=True,
#             top_k=10,
#             temperature=0.1,
#             top_p=0.95,
#             num_return_sequences=1,
#             eos_token_id=self.tokenizer.eos_token_id,
#             max_length=self.context_length,
#             truncation = True
#         )
#         if isinstance(input_prompt,list):
#             return [seq for seq in sequences]
#         else:
#             return sequences


# class Respone_Schema(typing_extensions.TypedDict):
#     url: str
#     contents: list[Subcontent_Schema]

import asyncio

class Gemini_Inference(object):
    gemma_prompt = f"<start_of_turn>user\n{{input_prompt}}<end_of_turn><eos>\n"

    def __init__(self,model_url:str, context_length:int):
        load_dotenv()
        genai.configure(api_key=os.environ['gemini_key'])
        self.model = genai.GenerativeModel(model_url)
        self.context_length = context_length
    
    def __call__(self,
                 input_prompt: Union[str, List[str]]
                 )->Union[str, List[str]]:

        print('prompt:',input_prompt)        
        final_prompt = self.gemma_prompt.format(input_prompt = input_prompt)
        
        response = self.model.generate_content(contents = final_prompt, 
                                            #    generation_config = genai.GenerationConfig(
                                            #     response_schema = Respone_Schema
                                            #     )
        )
        return response.text.replace('```the function:','').replace('```','').replace('python','')


# model_hub
class ModelHub(object):
    model_dict = {
        'codellama': {
            'model_url':"codellama/CodeLlama-7b-Python-hf",
            'context_length': 16384,
            'model_class': 'HuggingfaceModel'
        },
        'openllama_3b':{
            'model_url':"openlm-research/open_llama_3b",
            'context_length': 16384,
            'model_class': 'HuggingfaceModel'
        },
         'openllama_7b':{
            'model_url':"openlm-research/open_llama_7b",
            'context_length': 2048,
            'model_class': 'HuggingfaceModel'
        },
         'gemini':{
            'model_url':"gemini-1.5-flash",
            'context_length': 2048,
            'model_class': 'Gemini_Inference'
        }
                 
    }
    @staticmethod
    def get_model(model:str):
        model_config = ModelHub.model_dict[model]
        model_class = eval(model_config['model_class'])
        return model_class(model_url = model_config['model_url'], 
                           context_length = model_config['context_length'])
