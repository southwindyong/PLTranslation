import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import json
from pathlib import Path

def main(source_lang, target_lang, dataset, model, report_dir, attempt):#attempt是第几次尝试
    print('exporting reports')
    # dataset = 'codenet'
    dataset = 'my_dataset'
    translation_dir = f"output/{model}/{dataset}/{source_lang}/{target_lang}"
    test_dir = f"dataset/{dataset}/{source_lang}/TestCases"
    os.makedirs(report_dir, exist_ok=True)
    files = [f for f in os.listdir(translation_dir) if f != '.DS_Store']

    compile_failed = []
    test_passed = []
    test_failed = []
    test_failed_details = []
    runtime_failed = []
    runtime_failed_details = []
    token_exceeded = []
    infinite_loop = []

    ordered_unsuccessful_fp = Path(report_dir).joinpath(f"{model}_{dataset}_compileReport_from_" + str(source_lang) + "_to_" + str(target_lang) + "_ordered_unsuccessful.txt")
    ordered_files = [x.strip() for x in open(ordered_unsuccessful_fp, "r").readlines()]

    if target_lang == "Python":
        for i in range(0, len(files)):
            if files[i] not in ordered_files:
                continue

            try:
                print('Filename: ', files[i])
                subprocess.run("python3 -m py_compile " + translation_dir + "/" + files[i], check=True, capture_output=True, shell=True, timeout=30)
                with open(test_dir + "/" + files[i].split(".")[0] + "_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(test_dir + "/" + files[i].split(".")[0] + "_out.txt", "r").read()

                p = Popen(['python3', translation_dir + "/" + files[i]], stdin=PIPE, stdout=PIPE, stderr=PIPE)

                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append((files[i], "the program enters an infinite loop"))
                    continue

                if stdout.decode(errors="ignore").strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append((files[i], f_in, f_out, stdout.decode(errors="ignore")))
                        test_failed_details.append('Filename: ' + files[i] + ' Actual: ' + str(f_out) + ' Generated: ' + str(stdout.decode(errors="ignore")))
                    else:
                        runtime_failed.append((files[i], stderr_data.decode()))
                        runtime_failed_details.append('Filename: ' + files[i] + ' Error_type: ' + str(stderr_data.decode()))

            except subprocess.CalledProcessError as exc:
                if '# Token size exceeded.' in open(translation_dir + "/" + files[i], 'r').read():
                    token_exceeded.append(files[i])
                else:
                    compile_failed.append((files[i], exc.stderr.decode()))

    elif target_lang == "Java":
        for i in range(0, len(files)):
            if files[i] not in ordered_files:
                continue

            try:
                print('Filename: ', files[i])
                subprocess.run("javac " + translation_dir + "/" + files[i], check=True, capture_output=True, shell=True, timeout=30)
                with open(test_dir + "/" + files[i].split(".")[0] + "_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(test_dir + "/" + files[i].split(".")[0] + "_out.txt", "r").read()
                p = Popen(['java', files[i].split(".")[0]], cwd=translation_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)

                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append((files[i], "the program enters an infinite loop"))
                    continue

                if stdout.decode(errors="ignore").strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append((files[i], f_in, f_out, stdout.decode(errors="ignore")))
                        test_failed_details.append('Filename: ' + files[i] + ' Actual: ' + str(f_out) + ' Generated: ' + str(stdout.decode(errors="ignore")))
                    else:
                        runtime_failed.append((files[i], stderr_data.decode()))
                        runtime_failed_details.append('Filename: ' + files[i] + ' Error_type: ' + str(stderr_data.decode()))

            except subprocess.CalledProcessError as exc:
                if '# Token size exceeded.' in open(translation_dir + "/" + files[i], 'r').read():
                    token_exceeded.append(files[i])
                else:
                    compile_failed.append((files[i], exc.stderr.decode()))

        dir_files = os.listdir(translation_dir)
        for fil in dir_files:
            if ".class" in fil:
                os.remove(translation_dir + "/" + fil)

    elif target_lang == "C++":
        for i in range(0, len(files)):
            if files[i] not in ordered_files:
                continue

            try:
                print('Filename: ', files[i])
                subprocess.run("g++ -o exec_output -std=c++11 " + translation_dir + "/" + files[i], check=True, capture_output=True, shell=True)
                with open(test_dir + "/" + files[i].split(".")[0] + "_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(test_dir + "/" + files[i].split(".")[0] + "_out.txt", "r").read()
                p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append((files[i], "the program enters an infinite loop"))
                    continue

                if stdout.decode(errors="ignore").strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append((files[i], f_in, f_out, stdout.decode(errors="ignore")))
                        test_failed_details.append('Filename: ' + files[i] + ' Actual: ' + str(f_out) + ' Generated: ' + str(stdout.decode(errors="ignore")))
                    else:
                        runtime_failed.append((files[i], stderr_data.decode()))
                        runtime_failed_details.append('Filename: ' + files[i] + ' Error_type: ' + str(stderr_data.decode()))

            except subprocess.CalledProcessError as exc:
                if '# Token size exceeded.' in open(translation_dir + "/" + files[i], 'r').read():
                    token_exceeded.append(files[i])
                else:
                    compile_failed.append((files[i], exc.stderr.decode()))

    elif target_lang == "C":
        for i in range(0, len(files)):
            if files[i] not in ordered_files:
                continue
            try:
                print('Filename: ', files[i])
                subprocess.run("gcc " + translation_dir + "/" + files[i], check=True, capture_output=True, shell=True, timeout=10)
                with open(test_dir + "/" + files[i].split(".")[0] + "_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(test_dir + "/" + files[i].split(".")[0] + "_out.txt", "r").read()
                p = Popen(['./a.out'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append((files[i], "the program enters an infinite loop"))
                    continue

                if stdout.decode(errors="ignore").strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append((files[i], f_in, f_out, stdout.decode(errors="ignore")))
                        test_failed_details.append('Filename: ' + files[i] + ' Actual: ' + str(f_out) + ' Generated: ' + str(stdout.decode(errors="ignore")))
                    else:
                        runtime_failed.append((files[i], stderr_data.decode()))
                        runtime_failed_details.append('Filename: ' + files[i] + ' Error_type: ' + str(stderr_data.decode()))

            except subprocess.CalledProcessError as exc:
                if '# Token size exceeded.' in open(translation_dir + "/" + files[i], 'r').read():
                    token_exceeded.append(files[i])
                else:
                    compile_failed.append((files[i], exc.stderr.decode()))

    elif target_lang == "Go":
        for i in range(0, len(files)):
            if files[i] not in ordered_files:
                continue

            try:
                print('Filename: ', files[i])
                subprocess.run("go build " + translation_dir + "/" + files[i], check=True, capture_output=True, shell=True, timeout=30)
                with open(test_dir + "/" + files[i].split(".")[0] + "_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(test_dir + "/" + files[i].split(".")[0] + "_out.txt", "r").read()
                p = Popen(["./" + files[i].split(".")[0]], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)

                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append((files[i], "the program enters an infinite loop"))
                    continue

                if stdout.decode(errors="ignore").strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append((files[i], f_in, f_out, stdout.decode(errors="ignore")))
                        test_failed_details.append('Filename: ' + files[i] + ' Actual: ' + str(f_out) + ' Generated: ' + str(stdout.decode(errors="ignore")))
                    else:
                        runtime_failed.append((files[i], stderr_data.decode()))
                        runtime_failed_details.append('Filename: ' + files[i] + ' Error_type: ' + str(stderr_data.decode()))

            except subprocess.CalledProcessError as exc:
                if '# Token size exceeded.' in open(translation_dir + "/" + files[i], 'r').read():
                    token_exceeded.append(files[i])
                else:
                    compile_failed.append((files[i], exc.stderr.decode()))

    # 写报告
    def write_to_file(filename, data):
        with open(Path(report_dir).joinpath(filename), 'w') as file:
            json.dump(data, file, indent=4)
    
    print("compile_failed:",compile_failed)
    print("test_passed:",test_passed)
    print("test_failed",test_failed)
    print("test_failed_details",test_failed_details)
    print("runtime_failed",runtime_failed)
    print("runtime_failed_details",runtime_failed_details)
    print("token_exceeded",token_exceeded)
    print("infinite_loop",infinite_loop)

    write_to_file(f'{model}_{dataset}_compile_failed_{attempt}.json', compile_failed)
    write_to_file(f'{model}_{dataset}_test_passed_{attempt}.json', test_passed)
    write_to_file(f'{model}_{dataset}_test_failed_{attempt}.json', test_failed)
    write_to_file(f'{model}_{dataset}_test_failed_details_{attempt}.json', test_failed_details)
    write_to_file(f'{model}_{dataset}_runtime_failed_{attempt}.json', runtime_failed)
    write_to_file(f'{model}_{dataset}_runtime_failed_details_{attempt}.json', runtime_failed_details)
    write_to_file(f'{model}_{dataset}_token_exceeded_{attempt}.json', token_exceeded)
    write_to_file(f'{model}_{dataset}_infinite_loop_{attempt}.json', infinite_loop)


# 示例调用
if __name__ == "__main__":
    report_dir = "my_report_dir"
    model = "codegeex2-6b"
    dataset = "my_dataset"
    source_lang = "Python"
    target_lang = "Java"

    translation_dir = f"output/{model}/{dataset}/{source_lang}/{target_lang}"
    files = [f for f in os.listdir(translation_dir) if f != '.DS_Store']
    ordered_unsuccessful_fp = Path(report_dir).joinpath(f"{model}_{dataset}_compileReport_from_" + str(source_lang) + "_to_" + str(target_lang) + "_ordered_unsuccessful.txt")
    with open(ordered_unsuccessful_fp, 'w') as f:
            for file in files:
                f.write(f"{file}\n")
    main(source_lang, target_lang, dataset, model, report_dir , "1")
