import os
import re

def list_files(startpath):
    files = []
    for root, dirs, walkfiles in os.walk(startpath):
        for name in walkfiles:
            files.append(os.path.join(root, name))
    return files

def clean_codegeex(dataset):
    main_path = f'output/codegeex2-6b/{dataset}'
    output_path = 'output/codegeex2-6b/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()

        valid_lines = []
        for line in data.split('\n'):
            if line.strip() in ['C:', 'C++:', 'Java:', 'Python:', 'Go:', '"""']:
                break
            else:
                valid_lines.append(line)
        
        data = '\n'.join(valid_lines)
        data = data.replace('', '')
        data = data.replace(f'```{target_lang.lower()}', '')
        data = data.replace(f'```', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)
        
        if target_lang == 'Java' and dataset == 'evalplus':
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        print("cleaned data:",data)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_codegen(dataset):
    main_path = f'output/CodeGen/{dataset}'
    output_path = 'output/CodeGen/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()

        data = data[data.find(f'{target_lang} Code:')+len(f'{target_lang} Code:'):].strip()        

        valid_lines = []
        for line in data.split('\n'):
            if line.strip() in ["*/", 'C Code:', 'C++ Code:', 'Java Code:', 'Python Code:', 'Go Code:']:
                break
            else:
                valid_lines.append(line)
        
        data = '\n'.join(valid_lines)
        data = data.replace('', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)

        if target_lang == 'Java' and dataset == 'evalplus' and 'package com.example;' not in data:
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_starcoder(dataset):
    main_path = f'output/StarCoder/{dataset}'
    output_path = 'output/StarCoder/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()
        
        data = data[data.find('<fim_suffix><fim_middle>')+len('<fim_suffix><fim_middle>'):]

        valid_lines = []
        for line in data.split('\n'):
            if line.strip() in ["'''", 'C Code:', 'C++ Code:', 'Java Code:', 'Python Code:', 'Go Code:', '"""'] or line.strip().startswith("Input") or line.strip().startswith("Output"):
                break
            else:
                valid_lines.append(line)
        
        data = '\n'.join(valid_lines)
        data = data.replace('', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)

        if target_lang == 'Java' and dataset == 'evalplus' and 'package com.example;' not in data:
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_llama(dataset):
    main_path = f'output/LLaMa/{dataset}'
    output_path = 'output/LLaMa/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()

        data = data[data.find(f'{target_lang} Code:')+len(f'{target_lang} Code:'):].strip()

        valid_lines = []
        for line in data.split('\n'):
            if line.strip().startswith("Sure"):
                continue
            if line.strip().startswith("Please") or line.strip().startswith("Note") or line.strip().startswith("Here") or line.strip().startswith("In"):
                break
            else:
                valid_lines.append(line)
        
        data = '\n'.join(valid_lines)

        data = data.replace('</s>', '')
        data = data.replace(f'```{target_lang.lower()}', '')
        data = data.replace(f'```', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)

        if target_lang == 'Java' and dataset == 'evalplus' and 'package com.example;' not in data:
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_airoboros(dataset):
    main_path = f'output/TB-Airoboros/{dataset}'
    output_path = 'output/TB-Airoboros/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()

        data = data[data.find(f'{target_lang} Code:')+len(f'{target_lang} Code:'):].strip()

        data = data.replace('</s>', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)

        if target_lang == 'Java' and dataset == 'evalplus':
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_vicuna(dataset):
    main_path = f'output/TB-Vicuna/{dataset}'
    output_path = 'output/TB-Vicuna/'

    files = list_files(main_path)

    for f in files:
        splitted = f.split('/')
        filename = splitted[-1].strip()
        target_lang = splitted[-2].strip()
        source_lang = splitted[-3].strip()

        with open(f, 'r') as file:
            data = file.read()

        data = data[data.find(f'{target_lang} Code:')+len(f'{target_lang} Code:'):].strip()

        valid_lines = []
        for line in data.split('\n'):
            if line.strip().startswith("Translate the above") or line.strip().startswith("Note:") or line.strip().startswith("What is"):
                break
            else:
                valid_lines.append(line)
        
        data = '\n'.join(valid_lines)

        data = data.replace('</s>', '')

        if target_lang == 'Java':
            data = re.sub('public\s*class\s*.+', 'public class ' + filename.split('.')[0] + ' {', data)

        if target_lang == 'Java' and dataset == 'evalplus':
            data = 'package com.example;\n' + data

        os.makedirs(output_path + dataset + '/' + source_lang + '/' + target_lang, exist_ok=True)
        with open(output_path + dataset + '/' + source_lang + '/' + target_lang + '/' + filename, 'w') as file:
            file.write(data)

def clean_model(model, dataset):
    if model == 'CodeGeeX':
        clean_codegeex(dataset)
    elif model == 'StarCoder':
        clean_starcoder(dataset)
    elif model == 'LLaMa':
        clean_llama(dataset)
    elif model == 'CodeGen':
        clean_codegen(dataset)
    elif model == 'TB-Airoboros':
        clean_airoboros(dataset)
    elif model == 'TB-Vicuna':
        clean_vicuna(dataset)

# Example usage:
# clean_model('CodeGeeX', 'evalplus')
# clean_model('LLaMa', 'real-life-cli')
if __name__ == "__main__":
    clean_model('CodeGeeX','my_dataset')