import os
import logging
import time
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from selfmodel import generate

def translate_code(source_lang, target_lang, dataset_name, gpu_id=0):
    # Define various programming languages file extensions
    extensions = {'Python': 'py', 'C': 'c', 'C++': 'cpp', 'Java': 'java', 'Go': 'go', "Rust": "rs", "C#": "cs"}

    # Set input and output folder paths
    in_folder = f'dataset/{dataset_name}/{source_lang}/Code'
    # out_folder = f'output/{os.path.basename(model_path)}/{dataset_name}/{source_lang}/{target_lang}'
    out_folder = f'output/{dataset_name}/{source_lang}/{target_lang}'

    # Create output folder if it doesn't exist
    os.makedirs(out_folder, exist_ok=True)
    
    in_files = os.listdir(in_folder)
    print(f'找到 {len(in_files)} 个输入文件')

    ext = extensions[target_lang]
    # device = f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu'

    # # Load tokenizer and model from specified path
    # tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    # model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True, device=device)

    # Loop through input files
    for f in tqdm(in_files):
        prompt_file = f'{in_folder}/{f}'

        # with open(prompt_file, "r", encoding="ISO-8859-1", errors='ignore') as fin:
        with open(prompt_file, "r", encoding="utf-8", errors='ignore') as fin:
            source_code = fin.read()
            prompt = f"code translation\nsource_lang:{source_lang}\nsource_code：{source_code}\n\ntarget_lang：{target_lang}\n"

            try:
                t0 = time.perf_counter()

                # inputs = tokenizer(prompt, return_tensors="pt").to(device)
                # max_length = 2048 if "llama" in model_path.lower() else 1024

                # outputs = model.generate(inputs.input_ids, max_length=max_length, num_beams=5, early_stopping=True)
                response = generate(prompt, False, True)
                print(response)

                t1 = time.perf_counter()
                print("总生成时间:", t1 - t0)
                out_file = f'{out_folder}/{f.split(".")[0]}.{ext}'
                generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
                # with open(out_file, 'w') as fot:
                with open(out_file, 'w', encoding='utf-8') as fot:
                    fot.write(generated_code)
                
                # Print generated code to console
                print(f'生成的代码 ({source_lang} -> {target_lang}):')
                print(generated_code)

            except Exception as e:
                print(e)
                continue

# 示例调用
if __name__ == "__main__":
    # model_path = '/home/fdse/yyc/PLTranslationEmpirical/codegeex2-6b'
    translate_code(source_lang='Python', target_lang='Java', dataset_name='my_dataset', gpu_id=0)
