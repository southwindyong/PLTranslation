


#############################开源模型代码翻译，读取代码传递给大模型进行翻译###################################
#############################开源模型代码翻译，读取代码传递给大模型进行翻译###################################
#############################开源模型代码翻译，读取代码传递给大模型进行翻译###################################
import os
import logging
from dotenv import load_dotenv
import time
import argparse
from tqdm import tqdm
import torch
import codegeex
from codegeex.tokenizer import CodeGeeXTokenizer
from codegeex.torch import CodeGeeXModel
from transformers import AutoTokenizer, AutoModelForCausalLM

# 创建一个日志目录，存放日志文件
os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(
    filename=f"logs/translation.log", 
    level=logging.INFO, 
    format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main(args):
    # 定义各种编程语言的文件扩展名
    extensions = { 'Python': 'py','C': 'c','C++': 'cpp','Java': 'java','Go': 'go', "Rust": "rs", "C#": "cs" }

    # 设置输入和输出文件夹路径
    in_folder = f'dataset/{args.dataset}/{args.source_lang}/Code'
    out_folder = f'output/{args.model}/{args.dataset}/{args.source_lang}/{args.target_lang}'

    in_files = os.listdir(in_folder)
    print(f'found {len(in_files)} inputs')

    # 检查是否有已经翻译过的文件
    already_extracted_files = []
    if os.path.exists(out_folder):
        already_extracted_files = os.listdir(out_folder)
        if len(already_extracted_files) > 0:
            already_extracted_files = [x.split('.')[0] for x in already_extracted_files if os.stat(f'{out_folder}/{x}').st_size != 0]

    if len(already_extracted_files) > 0:
        in_files = [x for x in in_files if x.split('.')[0] not in already_extracted_files]

    ext = extensions[args.target_lang]
    device = f'cuda:{args.gpu_id}'

    # 根据选择的模型加载相应的tokenizer和model
    tokenizer, model = None, None
    if args.model == 'CodeGeeX':
        tokenizer = CodeGeeXTokenizer(
            tokenizer_path=os.getcwd() + "/CodeGeeX/codegeex/tokenizer/",
            mode="codegeex-13b"
        )
        state_dict = torch.load(os.getcwd() + "/CodeGeeX/codegeex_13b.pt", map_location="cpu")
        state_dict = state_dict["module"]

        model = CodeGeeXModel(
            hidden_size=5120, num_layers=39, num_attention_heads=40, padded_vocab_size=52224, max_position_embeddings=2048
        )
        model.load_state_dict(state_dict)
        model.eval()
        model.half()
        torch.cuda.set_device(device)
        model.cuda()
        torch.cuda.synchronize()

    elif args.model == 'StarCoder':
        tokenizer = AutoTokenizer.from_pretrained('bigcode/starcoder', use_auth_token=os.environ['STARCODER_AUTH_TOKEN'], cache_dir='./huggingface')
        model = AutoModelForCausalLM.from_pretrained('bigcode/starcoder', use_auth_token=os.environ['STARCODER_AUTH_TOKEN'], cache_dir='./huggingface').to(device)
    elif args.model == 'CodeGen':
        kwargs = {}
        kwargs["torch_dtype"] = torch.float16
        tokenizer = AutoTokenizer.from_pretrained('Salesforce/codegen-16B-multi', cache_dir='./huggingface')
        model = AutoModelForCausalLM.from_pretrained('Salesforce/codegen-16B-multi', cache_dir='./huggingface', **kwargs).to(device)
    elif args.model == 'LLaMa':
        tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-2-13b-chat-hf', use_auth_token=os.environ['LLAMA2_AUTH_TOKEN'], cache_dir='./huggingface')
        model = AutoModelForCausalLM.from_pretrained('meta-llama/Llama-2-13b-chat-hf', use_auth_token=os.environ['LLAMA2_AUTH_TOKEN'], cache_dir='./huggingface').to(device)
    elif args.model == 'TB-Airoboros':
        tokenizer = AutoTokenizer.from_pretrained('TheBloke/airoboros-13B-HF', cache_dir='./huggingface')
        model = AutoModelForCausalLM.from_pretrained('TheBloke/airoboros-13B-HF', cache_dir='./huggingface').to(device)
    elif args.model == 'TB-Vicuna':
        tokenizer = AutoTokenizer.from_pretrained('TheBloke/Wizard-Vicuna-13B-Uncensored-HF', cache_dir='./huggingface')
        model = AutoModelForCausalLM.from_pretrained('TheBloke/Wizard-Vicuna-13B-Uncensored-HF', cache_dir='./huggingface').to(device)

    # 循环处理输入文件
    os.makedirs(out_folder, exist_ok=True)
    for f in tqdm(in_files):
        prompt_file = f'{in_folder}/{f}'

        with open(prompt_file, "r", encoding="ISO-8859-1", errors='ignore') as fin:
            prompt = fin.readlines()

            # 根据模型生成相应的翻译提示
            if args.model == 'CodeGeeX':
                prompt = f"code translation\n{args.source_lang}:\n" + "".join(prompt) + f'\n\n{args.target_lang}:\n'
            elif args.model == 'StarCoder':
                prompt = f"{args.source_lang} Code:\n\n" + "".join(prompt) + f'\n\nTranslate the above {args.source_lang} code to {args.target_lang}.\n\n{args.target_lang} Code:\n\n'
                prefix_token = "<fim_prefix>"
                suffix_token = "<fim_suffix><fim_middle>"
                prompt = prefix_token + prompt + suffix_token
            elif args.model == 'CodeGen':
                prompt = f"{args.source_lang} Code:\n\n" + "".join(prompt) + f'\n\nTranslate the above {args.source_lang} code to {args.target_lang}.\n\n{args.target_lang} Code:\n\n'
            elif args.model == 'LLaMa':
                prompt = f"{args.source_lang} Code:\n\n" + "".join(prompt) + f'\n\nTranslate the above {args.source_lang} code to {args.target_lang}.\n\n{args.target_lang} Code:\n\n'
            elif args.model == 'TB-Airoboros':
                prompt = f"{args.source_lang} Code:\n\n" + "".join(prompt) + f'\n\nTranslate the above {args.source_lang} code to {args.target_lang}.\n\n{args.target_lang} Code:\n\n'
            elif args.model == 'TB-Vicuna':
                prompt = f"{args.source_lang} Code:\n\n" + "".join(prompt) + f'\n\nTranslate the above {args.source_lang} code to {args.target_lang}.\n\n{args.target_lang} Code:\n\n'

            try:
                t0 = time.perf_counter()

                inputs = []
                if args.model == 'CodeGeeX':
                    inputs = tokenizer.encode_code(prompt)
                    inputs = torch.tensor(inputs).reshape(1, len(inputs)).to(device)
                else:
                    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)

                total_input_tokens = inputs.shape[1]
                model_max_length = 4096 if args.model == 'LLaMa' else 2048
                if total_input_tokens >= model_max_length:
                    out_file = f'{out_folder}/{f.split(".")[0]}.{ext}'
                    with open(out_file, 'w') as fot:
                        print("# Token size exceeded.", file=fot)
                    continue
                max_new_tokens = model_max_length - total_input_tokens

                raw_outputs = ''
                if args.model == 'CodeGeeX':
                    raw_outputs = codegeex.generate(
                        model,
                        tokenizer,
                        prompt,
                        out_seq_length=max_new_tokens,
                        seq_length=2048,
                        top_k=args.k,
                        top_p=args.p,
                        temperature=args.temperature,
                        micro_batch_size=1,
                        backend="megatron",
                        verbose=True,
                    )
                
                else:
                    raw_outputs = model.generate(
                        inputs,
                        max_new_tokens=max_new_tokens,
                        do_sample=True,
                        top_p=args.p,
                        top_k=args.k,
                        temperature=args.temperature,
                        repetition_penalty=1,
                        pad_token_id=tokenizer.eos_token_id,
                    )


                t1 = time.perf_counter()
                print("Total generation time:", t1 - t0)
                out_file = f'{out_folder}/{f.split(".")[0]}.{ext}'                
                with open(out_file, 'w') as fot:
                    if args.model == 'CodeGeeX':
                        for g in raw_outputs:
                            fot.write(g)
                    else:
                        print(tokenizer.decode(raw_outputs[0]), file=fot)

            except (ValueError, FileNotFoundError) as e:
                print(e)
                continue

# if __name__ == "__main__":
#     load_dotenv()
#     parser = argparse.ArgumentParser(description='run translation with open-source models given dataset and languages')
#     parser.add_argument('--model', help='model to use for code translation. should be one of [CodeGeeX,StarCoder,CodeGen,TB-Airoboros,TB-Vicuna,LLaMa]', required=True, type=str)
#     parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar,evalplus]', required=True, type=str)
#     parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--k', help='The number of highest probability vocabulary tokens to keep for top-k-filtering. Only applies for sampling mode, with range from 1 to 100.', required=True, type=int)
#     parser.add_argument('--p', help='Only the most probable tokens with probabilities that add up to top_p or higher are considered during decoding. The valid range is 0.0 to 1.0. 1.0 is equivalent to disabled and is the default. Only applies to sampling mode. Also known as nucleus sampling.', required=True, type=float)
#     parser.add_argument('--temperature', help='A value used to warp next-token probabilities in sampling mode. Values less than 1.0 sharpen the probability distribution, resulting in "less random" output. Values greater than 1.0 flatten the probability distribution, resulting in "more random" output. A value of 1.0 has no effect and is the default. The allowed range is 0.0 to 2.0.', required=True, type=float)
#     parser.add_argument('--gpu_id', help='gpu id to use', required=True, type=int)
#     args = parser.parse_args()

#     # Initialize configurations
#     source = args.source_lang
#     target = args.target_lang
#     logging.info(f"translating examples from {source} to {target} using {args.model} and {args.dataset} dataset")
#     main(args)


######################################修复代码翻译错误########################################
######################################修复代码翻译错误########################################
######################################修复代码翻译错误########################################
######################################修复代码翻译错误########################################
######################################修复代码翻译错误########################################
import os
import openai
import logging
import tiktoken
import json
from pathlib import Path
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
import re
import argparse

os.makedirs(f'logs', exist_ok=True)
logging.basicConfig(filename=f"logs/repair.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Repair:
    EXTENTIONS = {
        "Java": "java",
        "Python": "py",
        "C": "c",
        "C++": "cpp",
        "Go": "go",
    }

    def __init__(self, args) -> None:
        self.args = args

    def __enter__(self):
        # Set up OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key

        self.main_dir = os.getcwd()
        self.translation_dir = Path(self.main_dir).joinpath(f'output/{self.args.model}/{self.args.dataset}')

        # Find the input directory with all the code examples
        self.input_dir = Path(self.main_dir).joinpath('dataset', self.args.dataset)
        if not self.input_dir.exists():
            raise FileNotFoundError(
                f"Directory {str(self.input_dir)} does not exist.")

        # Make a directory at output/<model>/<dataset>
        self.out_dir = Path(self.main_dir).joinpath("output", self.args.model + f'_IO_{self.args.attempt}', self.args.dataset)
        if not self.out_dir.exists():
            self.out_dir.mkdir(parents=True)

        return self

    def send_message_to_openai(self, message_log):
        "Use OpenAI's ChatCompletion API to get the chatbot's response"
        encoding = tiktoken.encoding_for_model("gpt-4")
        num_tokens = len(encoding.encode(message_log[1]["content"]))

        response = "exceptional case"
        is_success = False
        max_attempts = 5
        while max_attempts > 0:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # The name of the OpenAI chatbot model to use
                    # The conversation history up to this point, as a list of dictionaries
                    messages=message_log,
                    # The maximum number of tokens (words or subwords) in the generated response
                    max_tokens=max(1, 8000-num_tokens),
                    # The "creativity" of the generated response (higher temperature = more creative)
                    temperature=0.7,
                )
                is_success = True
                break
            except openai.error.InvalidRequestError as e:
                return "# Token size exceeded."
            except:
                max_attempts -= 1
                continue

        if not is_success:
            return response

        # Find the first response from the chatbot that has text in it (some responses may not have text)
        for choice in response.choices:
            if "text" in choice:
                return choice.text

        # If no response with text is found, return the first response's content (which may be empty)
        return response.choices[0].message.content

    def translate_with_OPENAI(self, source, target, source_code, translated_code, stderr, test_inputs, test_outputs, generated) -> str:
        content = ''
        if self.args.error_type in ['compile', 'runtime'] and self.args.dataset == 'evalplus':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following error because it is syntactically incorrect:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Print only the {target} code inside ```{target.lower()}{{response}}```and do not add any other natural language description in your output, and do not change the method signature from incorrect translation. Make sure your generated code is syntactically correct."
        elif self.args.error_type in ['compile', 'runtime']:
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following error because it is syntactically incorrect:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Print only the {target} code inside ```{target.lower()}{{response}}```and do not add any other natural language description in your output. Make sure your generated code is syntactically correct."
        elif self.args.error_type == 'incorrect' and self.args.dataset == 'evalplus':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following test failure:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Print only the {target} code inside ```{target.lower()}{{response}}```and do not add any other natural language description in your output, and do not change the method signature from incorrect translation. Make sure your generated code is syntactically correct."
        elif self.args.error_type == 'incorrect':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following output:\n{generated}\n\ninstead of the following expected output:\n{test_outputs}\n\nCan you re-generate your response and translate the above {source} code to {target}. Print only the {target} code inside ```{target.lower()}{{response}}```and do not add any other natural language description in your output. Make sure your generated code is syntactically correct. Your generated {target} code should take the following input and generate the expected output:\n\nInput:\n{test_inputs}\n\nExpected Output:\n{test_outputs}"

        message = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": content}]
        response = self.send_message_to_openai(message)
        return response.replace(f"```{target.lower()}", "").replace("```", "")

    def translate_with_HF(self, model, tokenizer, device, source, target, source_code, translated_code, stderr, test_inputs, test_outputs, generated) -> str:
        content = ''
        if self.args.error_type in ['compile', 'runtime'] and self.args.dataset == 'evalplus':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following error because it is syntactically incorrect:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Do not add any natural language description in your response, and do not change the method signature from incorrect translation.\n\n{target} Code:\n"
        elif self.args.error_type in ['compile', 'runtime']:
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following error because it is syntactically incorrect:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Do not add any natural language description in your response.\n\n{target} Code:\n"
        elif self.args.error_type == 'incorrect' and self.args.dataset == 'evalplus':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following test failure:\n\n{stderr}\n\nCan you re-generate your response and translate the above {source} code to {target}. Do not add any natural language description in your output, and do not change the method signature from incorrect translation.\n\n{target} Code:\n"
        elif self.args.error_type == 'incorrect':
            content = f"You were asked to translate the following {source} code to {target}:\n\n{source_code}\n\nYour response was the following {target} code:\n\n{translated_code}\n\nExecuting your generated code gives the following output:\n{generated}\n\ninstead of the following expected output:\n{test_outputs}\n\nCan you re-generate your response and translate the above {source} code to {target}. Do not add any natural language description in your response. Your generated {target} code should take the following input and generate the expected output:\n\nInput:\n{test_inputs}\n\nExpected Output:\n{test_outputs}\n\n{target} Code:\n"

        if self.args.model == 'StarCoder':
            content = "<fim_prefix>" + content + "<fim_suffix><fim_middle>"

        inputs = tokenizer.encode(content, return_tensors="pt").to(device)

        total_input_tokens = inputs.shape[1]
        context_length = 4096 if self.args.model == 'LLaMa' else 2048

        if total_input_tokens >= context_length:
            return "# Token size exceeded."

        max_new_tokens = context_length - total_input_tokens

        raw_outputs = model.generate(
                    inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    top_p=self.args.p,
                    top_k=self.args.k,
                    temperature=self.args.temperature,
                    repetition_penalty=1,
                    pad_token_id=tokenizer.eos_token_id,
                )

        return tokenizer.decode(raw_outputs[0])


    def fix(self, source, target):

        self.errors = {}
        with open(f'fix_reports/{self.args.model}_{self.args.dataset}_errors_from_{source}_to_{target}_{self.args.attempt}.json', 'r') as f:
            self.errors = json.load(f)

        tokenizer, model = None, None
        device = f'cuda:{self.args.gpu_id}' if torch.cuda.is_available() else 'cpu'
        if self.args.model != 'GPT-4':
            model_path = ''
            auth_token = None
            kwargs = {}
            if self.args.model == 'LLaMa':
                model_path = 'meta-llama/Llama-2-13b-chat-hf'
                auth_token = os.environ['LLAMA2_AUTH_TOKEN']
            elif self.args.model == 'StarCoder':
                model_path = 'bigcode/starcoder'
                auth_token = os.environ['STARCODER_AUTH_TOKEN']
            elif self.args.model == 'CodeGen':
                model_path = 'Salesforce/codegen-16B-multi'
                kwargs["torch_dtype"] = torch.float16

            tokenizer = AutoTokenizer.from_pretrained(model_path, use_auth_token=auth_token, cache_dir='./huggingface')
            model = AutoModelForCausalLM.from_pretrained(model_path, use_auth_token=auth_token, cache_dir='./huggingface', **kwargs).to(device)

        snippets = self.errors[self.args.error_type]
        for snippet in tqdm(snippets, total=len(snippets), bar_format="{desc:<5.5}{percentage:3.0f}%|{bar:10}{r_bar}"):
            code_id = snippet[0].split('.')[0]

            stderr, test_inputs, test_outputs, generated = '', '', '', ''
            if self.args.error_type in ['compile', 'runtime']:
                filename, stderr = snippet
            
            elif self.args.error_type == 'incorrect' and self.args.dataset == 'evalplus':
                filename, stderr = snippet

            elif self.args.error_type == 'incorrect':
                filename, test_inputs, test_outputs, generated = snippet

            stderr_output = stderr.strip()
            test_inputs = test_inputs.strip()
            test_outputs = test_outputs.strip()
            generated = generated.strip()

            source_code = ''
            with open(f'{self.input_dir}/{source}/Code/' + filename.split('.')[0] + f'.{self.EXTENTIONS[source]}', 'r') as f:
                source_code = f.read().strip()

            recent_translated_code = ''
            with open(f'{self.translation_dir}/{source}/{target}/{filename}', 'r') as f:
                recent_translated_code = f.read().strip()
            
            # Save the generated code
            target_dir = self.out_dir.joinpath(f"{source}", f"{target}")
            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            filename_of_translated_code = target_dir.joinpath(filename)

            translated_code_fp = Path(filename_of_translated_code)
            if translated_code_fp.exists():
                continue

            translated_code = ''
            if self.args.model == 'GPT-4':
                translated_code = self.translate_with_OPENAI(
                    source, target, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated)
            elif self.args.model in ['LLaMa', 'StarCoder', 'CodeGen']:
                translated_code = self.translate_with_HF(
                    model, tokenizer, device, source, target, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated)
            
            translated_code = re.sub('public\s*class\s*.+', 'public class ' + code_id + ' {', translated_code)

            with open(filename_of_translated_code, "w") as f:
                print(translated_code, file=f)

    def __exit__(self, exception, _, __):
        print(exception)


# if __name__ == "__main__":
#     # Initialize OPENAI-API keys
#     load_dotenv()

#     parser = argparse.ArgumentParser(description='run repair with a given model, dataset and languages')
#     parser.add_argument('--model', help='model to use for code translation. should be one of [GPT-4,LLaMa,StarCoder,CodeGen]', required=True, type=str)
#     parser.add_argument('--dataset', help='dataset to use for code translation. should be one of [codenet,avatar,evalplus]', required=True, type=str)
#     parser.add_argument('--source_lang', help='source language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--target_lang', help='target language to use for code translation. should be one of [Python,Java,C,C++,Go]', required=True, type=str)
#     parser.add_argument('--k', help='The number of highest probability vocabulary tokens to keep for top-k-filtering. Only applies for sampling mode, with range from 1 to 100.', required=True, type=int)
#     parser.add_argument('--p', help='Only the most probable tokens with probabilities that add up to top_p or higher are considered during decoding. The valid range is 0.0 to 1.0. 1.0 is equivalent to disabled and is the default. Only applies to sampling mode. Also known as nucleus sampling.', required=True, type=float)
#     parser.add_argument('--temperature', help='A value used to warp next-token probabilities in sampling mode. Values less than 1.0 sharpen the probability distribution, resulting in "less random" output. Values greater than 1.0 flatten the probability distribution, resulting in "more random" output. A value of 1.0 has no effect and is the default. The allowed range is 0.0 to 2.0.', required=True, type=float)
#     parser.add_argument('--gpu_id', help='GPU ID to use for translation.', required=True, type=int)
#     parser.add_argument('--error_type', help='Error type to repair. should be one of [compile,runtime,incorrect]', required=True, type=str)
#     parser.add_argument('--attempt', help='Attempt number to repair.', required=True, type=int)
#     args = parser.parse_args()

#     source = args.source_lang
#     target = args.target_lang
#     with Repair(args) as repair:
#         logging.info(f"Repairing examples from {source} to {target} in {args.dataset} dataset for {args.error_type} errors using {args.model} model.")
#         repair.fix(source, target)
