import os
import json
from pathlib import Path
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from tqdm import tqdm
import re
import logging
from compileback import compile_and_test  # 导入编译和测试函数

class Repair:
    EXTENSIONS = {
        "Java": "java",
        "Python": "py",
        "C": "c",
        "C++": "cpp",
        "Go": "go",
    }

    def __init__(self, dataset, source_lang, target_lang, k, p, temperature, gpu_id, error_type):
        self.dataset = dataset
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.k = k
        self.p = p
        self.temperature = temperature
        self.gpu_id = gpu_id
        self.error_type = error_type

    def fix(self, attempt):
        # 设置路径
        main_dir = os.getcwd()
        input_dir = Path(main_dir).joinpath('dataset', self.dataset)
        translation_dir = Path(main_dir).joinpath(f'output/{self.dataset}')
        out_dir = Path(main_dir).joinpath("output", f'_IO_{attempt}', self.dataset)

        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(filename='logs/repair.log', level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # 查找包含所有代码示例的输入目录
        if not input_dir.exists():
            raise FileNotFoundError(f"目录 {str(input_dir)} 不存在。")

        if not out_dir.exists():
            out_dir.mkdir(parents=True)

        # 从 JSON 文件加载错误片段
        errors = {}
        with open(f'my_report_dir/{self.code_model}_{self.dataset}_compiled_failed_{attempt}.json', 'r') as f:
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

            # 检查并确保所有变量都是字符串类型
            stderr_output = stderr.strip() if stderr else ''
            test_inputs = test_inputs.strip() if test_inputs else ''
            test_outputs = test_outputs.strip() if test_outputs else ''
            generated = generated.strip() if generated else ''

            # 读取源代码
            source_code = ''
            source_code_path = input_dir.joinpath(f'{self.source_lang}/Code/{filename.split(".")[0]}.{self.EXTENSIONS[self.source_lang]}')
            with open(source_code_path, 'r') as f:
                source_code = f.read().strip()

            # 读取最近的翻译代码
            recent_translated_code = ''
            recent_translated_code_path = translation_dir.joinpath(f'{self.source_lang}/{self.target_lang}/{filename}')
            with open(recent_translated_code_path, 'r') as f:
                recent_translated_code = f.read().strip()

            # 生成新的翻译代码
            translated_code = self.generate_translated_code(
                source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated)

            # 写回翻译代码文件
            filename_of_translated_code = translation_dir.joinpath(f'{self.source_lang}/{self.target_lang}/{filename}')
            with open(filename_of_translated_code, "w") as f:
                f.write(translated_code)

    def generate_translated_code(self, source_code, recent_translated_code, stderr_output, test_inputs, test_outputs, generated):
        if self.error_type in ['compile', 'runtime']:
            if self.dataset == 'evalplus':
                prompt = f"""GPT-4 Fix Prompt when effect is COMPILE ERROR or RUNTIME ERROR and dataset is Evalplus:

You were asked to translate the following {self.source_lang} code to {self.target_lang}:
{source_code}

Your response was the following {self.target_lang} code:
{recent_translated_code}

Executing your generated code gives the following error because it is syntactically incorrect:
{stderr_output}

Can you re-generate your response and translate the above {self.source_lang} code to {self.target_lang}. Print only the {self.target_lang} code inside ```{self.target_lang}{{response}}``` and do not add any other natural language description in your output, and do not change the method signature from incorrect translation. Make sure your generated code is syntactically correct."""
            else:
                prompt = f"""GPT-4 Fix Prompt when effect is COMPILE ERROR or RUNTIME ERROR and dataset is CodeNet or AVATAR:

You were asked to translate the following {self.source_lang} code to {self.target_lang}:
{source_code}

Your response was the following {self.target_lang} code:{recent_translated_code}
Executing your generated code gives the following error because it is syntactically incorrect:
{stderr_output}

Can you re-generate your response and translate the above {self.source_lang} code to {self.target_lang}. Print only the {self.target_lang} code inside ```{self.target_lang}{{response}}``` and do not add any other natural language description in your output. Make sure your generated code is syntactically correct."""
        else:  # incorrect output
            if self.dataset == 'evalplus':
                prompt = f"""GPT-4 Fix Prompt when effect is INCORRECT OUTPUT and dataset is Evalplus:

You were asked to translate the following {self.source_lang} code to {self.target_lang}:
{source_code}

Your response was the following {self.target_lang} code:
{recent_translated_code}

Executing your generated code gives the following test failure:
{stderr_output}

Can you re-generate your response and translate the above {self.source_lang} code to {self.target_lang}. Print only the {self.target_lang} code inside ```{self.target_lang}{{response}}``` and do not add any other natural language description in your output, and do not change the method signature from incorrect translation. Make sure your generated code is syntactically correct."""
            else:
                prompt = f"""GPT-4 Fix Prompt when effect is INCORRECT OUTPUT and dataset is CodeNet or AVATAR:

You were asked to translate the following {self.source_lang} code to {self.target_lang}:
{source_code}

Your response was the following {self.target_lang} code:
{recent_translated_code}

Executing your generated code gives the following output:
{generated}

instead of the following expected output:
{test_outputs}

Can you re-generate your response and translate the above {self.source_lang} code to {self.target_lang}. Print only the {self.target_lang} code inside ```{self.target_lang}{{response}}``` and do not add any other natural language description in your output. Make sure your generated code is syntactically correct. Your generated {self.target_lang} code should take the following input and generate the expected output:

Input:
{test_inputs}

Expected Output:
{test_outputs}"""

        response = generate(prompt, False, True)
        return response


# 示例用法
if __name__ == "__main__":
    # 初始化环境变量
    load_dotenv()

    # 示例用法
    dataset = 'evalplus'
    source_lang = 'Python'
    target_lang = 'Java'
    k = 10
    p = 0.9
    temperature = 1.0
    gpu_id = 0
    error_type = 'incorrect'
    max_attempts = 5  # 最大修复次数

    repair_instance = Repair(dataset, source_lang, target_lang, k, p, temperature, gpu_id, error_type)

    # 循环修复过程
    for attempt in range(1, max_attempts + 1):
        repair_instance.fix(attempt)
        # 调用 compile.py 中的编译和测试函数
        compile_failed, test_failed, test_passed, test_failed_details = compile_and_test(source_lang, target_lang, model, "my_report_dir")
        # 如果有编译失败，继续进行修复
        if compile_failed:
            print(f"第 {attempt} 次尝试失败，继续进行修复...")
            continue
        # 如果测试失败，记录详细信息并继续修复
        if test_failed:
            with open("my_report_dir/test_failed_report.txt", "a") as report_file:
                for detail in test_failed_details:
                    report_file.write(f"代码语法没有错误，但源代码与翻译代码输出不相同，在输入为（）的情况下输出分别为（）和（）。\n{detail}\n")
            print(f"第 {attempt} 次尝试失败，继续进行修复...")
            continue
        # 如果所有测试通过，修复成功，退出循环
        if test_passed:
            print(f"修复成功于第 {attempt} 次尝试")
            break
