from langchain.prompts import PromptTemplate
from transformers import LlamaForCausalLM,LlamaTokenizer,AutoModelForCausalLM,AutoTokenizer
import torch
torch.cuda.set_device(0)
model_name = "/home/Data/huggingface/hub/deepseek-coder-33b-instruct/deepseek-coder-33b-instruct" 
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_name,torch_dtype=torch.float16, low_cpu_mem_usage=True).to('cuda')

def generate(query,return_input=False,skip_special_tokens = True)->str:
    messages=[        { 'role': 'user', 'content': query}
    ]
    inputs = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to('cuda')
    # 32021 is the id of <|EOT|> token
    outputs = model.generate(inputs, max_new_tokens=1024, do_sample=False,temperature=0 ,num_return_sequences=1, eos_token_id=32021)
    return tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
response = generate(Repair_prompt, False, True)
print(response)