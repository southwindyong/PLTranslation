import os
import subprocess
import pandas as pd
from pathlib import Path
from subprocess import Popen, PIPE

def compile_and_test(source_lang, target_lang, report_dir):
    print('testing translations')
    dataset = 'my_dataset'
    translation_dir = f"output/{dataset}/{source_lang}/{target_lang}"
    test_dir = f"dataset/{dataset}/{source_lang}/TestCases"
    source_code_dir = f"dataset/{dataset}/{source_lang}/Code"
    os.makedirs(report_dir, exist_ok=True)
    files = [f for f in os.listdir(translation_dir) if f != '.DS_Store']
    
    print("length of files:", len(files))

    compile_failed = []
    test_passed = []
    test_failed = []
    test_failed_details = []
    runtime_failed = []
    runtime_failed_details = []
    infinite_loop = []
    
    def run_code(command, input_data, timeout=100):
        p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            stdout, stderr_data = p.communicate(input=input_data.encode(), timeout=timeout)
            return stdout.decode().strip(), stderr_data.decode().strip()
        except subprocess.TimeoutExpired:
            return None, "Timeout expired"

    if target_lang == "Python":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                # 编译翻译后的代码
                subprocess.run(f"python3 -m py_compile {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                
                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code(['python3', f"{translation_dir}/{files[i]}"], f_in)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                original_output, _ = run_code(['python3', source_file], f_in)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))

    elif target_lang == "Java":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                # 编译翻译后的代码
                subprocess.run(f"javac {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                
                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code(['java', files[i].split('.')[0]], f_in, cwd=translation_dir)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                subprocess.run(f"javac {source_file}", check=True, capture_output=True, shell=True, timeout=30)
                original_output, _ = run_code(['java', files[i].split('.')[0]], f_in, cwd=source_code_dir)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))
        dir_files = os.listdir(translation_dir)
        for fil in dir_files:
            if ".class" in fil: 
                os.remove(f"{translation_dir}/{fil}")

    elif target_lang == "C++":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                # 编译翻译后的代码
                subprocess.run(f"g++ -o exec_output -std=c++11 {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True)

                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code(['./exec_output'], f_in)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                subprocess.run(f"g++ -o exec_output -std=c++11 {source_file}", check=True, capture_output=True, shell=True)
                original_output, _ = run_code(['./exec_output'], f_in)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))

    elif target_lang == "C":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                # 编译翻译后的代码
                subprocess.run(f"gcc {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=10)

                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code(['./a.out'], f_in)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                subprocess.run(f"gcc {source_file}", check=True, capture_output=True, shell=True, timeout=10)
                original_output, _ = run_code(['./a.out'], f_in)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))

    elif target_lang == "Go":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                # 编译翻译后的代码
                subprocess.run(f"go build {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)

                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code([f"./{files[i].split('.')[0]}"], f_in)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                subprocess.run(f"go build {source_file}", check=True, capture_output=True, shell=True, timeout=30)
                original_output, _ = run_code([f"./{files[i].split('.')[0]}"], f_in)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))
            wd = os.getcwd()
            if os.path.isfile(wd + "/" + files[i].split(".")[0]):
                os.remove(wd + "/" + files[i].split(".")[0])

    elif target_lang == "Rust":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                bin_name = files[i].split('.')[0]

                # 编辑翻译后的代码
                subprocess.run(f'rustc -o {bin_name} {translation_dir}/{files[i]}', check=True, capture_output=True, shell=True)
                # 运行翻译后的代码
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                translated_output, _ = run_code([f"./{bin_name}"], f_in)

                # 编译并运行源代码
                source_file = f"{source_code_dir}/{files[i].split('.')[0]}.{source_lang}"
                subprocess.run(f'rustc -o {bin_name} {source_file}', check=True, capture_output=True, shell=True)
                original_output, _ = run_code([f"./{bin_name}"], f_in)

                # 比较输出
                if translated_output == f_out.strip() and original_output == f_out.strip():
                    test_passed.append((files[i], True))
                else:
                    if translated_output == f_out.strip() and original_output != f_out.strip():
                        test_failed_details.append(f"Code syntax is correct, but the source code and the translated code have different outputs. For an input of '{f_in}', the outputs are '{original_output}' and '{translated_output}' respectively.")
                    test_failed.append((files[i], False))
            except Exception as e:
                compile_failed.append((files[i], False))

    return compile_failed, test_passed, test_failed, test_failed_details

