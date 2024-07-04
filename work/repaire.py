import os
import json
from pathlib import Path
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
import re

class Repair:
    EXTENTIONS = {
        "Java": "java",
        "Python": "py",
        "C": "c",
        "C++": "cpp",
        "Go": "go",
    }

    def __init__(self, model, code_model, dataset, source_lang, target_lang, k, p, temperature, gpu_id, error_type):
        self.model = model
        self.code_model = code_model
        self.dataset = dataset
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.k = k
        self.p = p
        self.temperature = temperature
        self.gpu_id = gpu_id
        self.error_type = error_type

    def fix(self,attempt):
        # Set up paths
        main_dir = os.getcwd()
        input_dir = Path(main_dir).joinpath('dataset', self.dataset)
        translation_dir = Path(main_dir).joinpath(f'output/{self.model}/{self.dataset}')
        out_dir = Path(main_dir).joinpath("output", self.model + f'_IO_{self.attempt}', self.dataset)

        os.makedirs(f'logs', exist_ok=True)
        logging.basicConfig(filename=f"logs/repair.log", level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # Find the input directory with all the code examples
        if not input_dir.exists():
            raise FileNotFoundError(
                f"Directory {str(input_dir)} does not exist.")

        if not out_dir.exists():
            out_dir.mkdir(parents=True)

        # Initialize model and tokenizer
        tokenizer, model = None, None
        device = f'cuda:{self.gpu_id}' if torch.cuda.is_available() else 'cpu'
        if self.model != 'GPT-4':
            model_path = ''
            auth_token = None
            kwargs = {}
            if self.model == 'LLaMa':
                model_path = 'meta-llama/Llama-2-13b-chat-hf'
                auth_token = os.getenv('LLAMA2_AUTH_TOKEN')
            elif self.model == 'StarCoder':
                model_path = 'bigcode/starcoder'
                auth_token = os.getenv('STARCODER_AUTH_TOKEN')
            elif self.model == 'CodeGen':
                model_path = 'Salesforce/codegen-16B-multi'
                kwargs["torch_dtype"] = torch.float16

            tokenizer = AutoTokenizer.from_pretrained(model_path, use_auth_token=auth_token, cache_dir='./huggingface')
            model = AutoModelForCausalLM.from_pretrained(model_path, use_auth_token=auth_token, cache_dir='./huggingface', **kwargs).to(device)

        # Load error snippets from JSON file
        errors = {}
        with open(f'my_report_dir/{self.code_model}_{self.dataset}_compiled_failed_{self.attempt}.json', 'r') as f:
            errors = json.load(f)

        snippets = errors[self.error_type]
        for snippet in tqdm(snippets, total=len(snippets), bar_format="{desc:<5.5}{percentage:3.0f}%|{bar:10}{r_bar}"):
            code_id = snippet[0].split('.')[0]

            stderr, test_inputs, test_outputs, generated = '', '', '', ''
            if self.error_type in ['compile', 'runtime']:
                filename, stderr = snippet
            elif self.error_type == 'incorrect' and self.dataset == 'evalplus':
                filename, stderr = snippet
            elif self.error_type == 'incorrect':
                filename, test_inputs, test_outputs, generated = snippet

            stderr_output = stderr.strip()
            test_inputs = test_inputs.strip()
            test_outputs = test_outputs.strip()
            generated = generated.strip()

            # Read source code
            source_code = ''
            with open(f'{input_dir}/{self.source_lang}/Code/' + filename.split('.')[0] + f'.{self.EXTENTIONS[self.source_lang]}', 'r') as f:
                source_code = f.read().strip()

            # Read recent translated code
            recent_translated_code = ''
            with open(f'{translation_dir}/{self.source_lang}/{self.target_lang}/{filename}', 'r') as f:
                recent_translated_code = f.read().strip()

            # Save the generated code
            target_dir = out_dir.joinpath(f"{self.source_lang}", f"{self.target_lang}")
            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            filename_of_translated_code = target_dir.joinpath(filename)

            translated_code = ''
            if self.model == 'GPT-4':
                translated_code = self.translate_with_OPENAI(
                    source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated)
            elif self.model in ['LLaMa', 'StarCoder', 'CodeGen']:
                translated_code = self.translate_with_HF(
                    model, tokenizer, device, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated)

            translated_code = re.sub('public\s*class\s*.+', 'public class ' + code_id + ' {', translated_code)

            with open(filename_of_translated_code, "w") as f:
                print(translated_code, file=f)

    def translate_with_OPENAI(self, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated):
        # Placeholder for OpenAI translation logic
        pass

    def translate_with_HF(self, model, tokenizer, device, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated):
        # Placeholder for Hugging Face translation logic
        pass

# 示例用法
if __name__ == "__main__":
    # Initialize environment variables
    load_dotenv()

    # Example usage
    model = 'LLaMa'
    dataset = 'evalplus'
    source_lang = 'Python'
    target_lang = 'Java'
    k = 10
    p = 0.9
    temperature = 1.0
    gpu_id = 0
    error_type = 'incorrect'
    attempt = 1
    code_model = "codegeex2-6b"

    repair_instance = Repair(model, code_model,dataset, source_lang, target_lang, k, p, temperature, gpu_id, error_type)
    repair_instance.fix(attempt)
