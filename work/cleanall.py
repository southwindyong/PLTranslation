import os
import re

def list_files(startpath):
    files = []
    for root, dirs, walkfiles in os.walk(startpath):
        for name in walkfiles:
            files.append(os.path.join(root, name))
    return files

def clean(dataset):
    main_path = f'output/{dataset}'
    output_path = 'output/'

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
            
if __name__ == "__main__":
    clean_model('my_dataset')