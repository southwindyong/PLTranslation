import os
import subprocess
import pandas as pd
from pathlib import Path
from subprocess import Popen, PIPE

def main(source_lang, target_lang, model, report_dir):
    print('testing translations')
    dataset = 'my_dataset'
    translation_dir = f"output/{model}/{dataset}/{source_lang}/{target_lang}"
    test_dir = f"dataset/{dataset}/{source_lang}/TestCases"
    os.makedirs(report_dir, exist_ok=True)
    files = [f for f in os.listdir(translation_dir) if f != '.DS_Store']
    
    print("length of files:",len(files))

    compile_failed = []
    test_passed = []
    test_failed = []
    test_failed_details = []
    runtime_failed = []
    runtime_failed_details = []
    infinite_loop = []
    
    if target_lang == "Python":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                subprocess.run(f"python3 -m py_compile {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                p = Popen(['python3', f"{translation_dir}/{files[i]}"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])

    elif target_lang == "Java":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                subprocess.run(f"javac {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                p = Popen(['java', files[i].split('.')[0]], cwd=translation_dir, stdin=PIPE, stdout=PIPE, stderr=PIPE)    
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])
        dir_files = os.listdir(translation_dir)
        for fil in dir_files:
            if ".class" in fil: 
                os.remove(f"{translation_dir}/{fil}")

    elif target_lang == "C++":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                subprocess.run(f"g++ -o exec_output -std=c++11 {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True)
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                p = Popen(['./exec_output'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)    
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])

    elif target_lang == "C":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                subprocess.run(f"gcc {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=10)
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                p = Popen(['./a.out'], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)    
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])

    elif target_lang == "Go":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                subprocess.run(f"go build {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                p = Popen([f"./{files[i].split('.')[0]}"], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)    
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])
            wd = os.getcwd()
            if os.path.isfile(wd + "/" + files[i].split(".")[0]):
                os.remove(wd + "/" + files[i].split(".")[0])

    elif target_lang == "Rust":
        for i in range(len(files)):
            try:
                print('Filename: ', files[i])
                bin_name = files[i].split('.')[0]
                with open(f"{test_dir}/{files[i].split('.')[0]}_in.txt", 'r') as f:
                    f_in = f.read()
                f_out = open(f"{test_dir}/{files[i].split('.')[0]}_out.txt", "r").read()
                subprocess.run(f"rustc {translation_dir}/{files[i]}", check=True, capture_output=True, shell=True, timeout=30)
                p = Popen([f"./{bin_name}"], cwd=os.getcwd(), stdin=PIPE, stdout=PIPE, stderr=PIPE)
                try:
                    stdout, stderr_data = p.communicate(input=f_in.encode(), timeout=100)
                except subprocess.TimeoutExpired:
                    infinite_loop.append(files[i])
                    continue
                if stdout.decode().strip() == f_out.strip():
                    test_passed.append(files[i])
                else:
                    if stderr_data.decode() == '':
                        test_failed.append(files[i])
                        test_failed_details.append(f'Filename: {files[i]} Actual: {str(f_out)} Generated: {str(stdout.decode())}')  
                    else:
                        runtime_failed.append(files[i])
                        runtime_failed_details.append(f'Filename: {files[i]} Error_type: {str(stderr_data.decode())}') 
            except Exception as e:
                compile_failed.append(files[i])

    else:
        print(f"language: {target_lang} is not yet supported. Select from the following languages: [Python, Java, C, C++, Go, Rust]")
        return

    test_failed = list(set(test_failed))
    test_failed_details = list(set(test_failed_details))
    runtime_failed = list(set(runtime_failed))
    runtime_failed_details = list(set(runtime_failed_details))
    compile_failed = list(set(compile_failed))
    infinite_loop = list(set(infinite_loop))
    test_passed = list(set(test_passed))

    txt_fp = Path(report_dir).joinpath(f"{model}_{dataset}_compileReport_from_{source_lang}_to_{target_lang}.txt")
    with open(txt_fp, "w", encoding="utf-8") as report:
        report.writelines(f"Total Instances: {len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop)}\n\n")
        report.writelines(f"Total Correct: {len(test_passed)}\n")
        report.writelines(f"Total Runtime Failed: {len(runtime_failed)}\n")
        report.writelines(f"Total Compilation Failed: {len(compile_failed)}\n")
        report.writelines(f"Total Test Failed: {len(test_failed)}\n")
        report.writelines(f"Total Infinite Loop: {len(infinite_loop)}\n\n")
        report.writelines(f"Accuracy: {(len(test_passed) / (len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop))) * 100}\n")
        report.writelines(f"Runtime Rate: {(len(runtime_failed) / (len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop))) * 100}\n")
        report.writelines(f"Compilation Rate: {(len(compile_failed) / (len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop))) * 100}\n")
        report.writelines(f"Test Failed Rate: {(len(test_failed) / (len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop))) * 100}\n")
        report.writelines(f"Infinite Loop Rate: {(len(infinite_loop) / (len(test_passed) + len(compile_failed) + len(runtime_failed) + len(test_failed) + len(infinite_loop))) * 100}\n\n")
        report.writelines("=================================================================================================\n")
        report.writelines(f"Failed Test Files: {test_failed} \n")
        report.writelines(f"Failed Test Details: {test_failed_details} \n")
        report.writelines("=================================================================================================\n")
        report.writelines(f"Runtime Error Files: {runtime_failed} \n")
        report.writelines(f"Runtime Error Details: {runtime_failed_details} \n")
        report.writelines("=================================================================================================\n")
        report.writelines(f"Compilation Error Files: {compile_failed} \n")
        report.writelines("=================================================================================================\n")    
        report.writelines(f"Infinite Loop Files: {infinite_loop} \n")
        report.writelines("=================================================================================================\n")

    df = pd.DataFrame(columns=['Source Language', 'Target Language', 'Filename', 'BugType', 'RootCause', 'Impact', 'Comments'])
    index = 0
    for i in range(len(compile_failed)):
        list_row = [source_lang, target_lang, compile_failed[i], "", "", "Compilation Error", ""]
        df.loc[i] = list_row
        index += 1
    for i in range(len(runtime_failed)):
        list_row = [source_lang, target_lang, runtime_failed[i], "", "", "Runtime Error", ""]
        df.loc[index] = list_row
        index += 1 
    for i in range(len(test_failed)):
        list_row = [source_lang, target_lang, test_failed[i], "", "", "Test Failed", ""]
        df.loc[index] = list_row
        index += 1

    excel_fp = Path(report_dir).joinpath(f"{model}_{dataset}_compileReport_from_{source_lang}_to_{target_lang}.xlsx")
    df.to_excel(excel_fp, sheet_name='Sheet1')

    ordered_unsuccessful_fp = Path(report_dir).joinpath(f"{model}_{dataset}_compileReport_from_{source_lang}_to_{target_lang}_ordered_unsuccessful.txt")
    with open(ordered_unsuccessful_fp, 'w') as f:
        for unsuccessful_instance in compile_failed + runtime_failed + test_failed + infinite_loop:
            f.write(f"{unsuccessful_instance}\n")

    # Read and print the contents of the generated files to ensure successful writing
    with open(txt_fp, "r", encoding="utf-8") as report:
        print("\n\nText Report File Content:")
        print(report.read())

    df = pd.read_excel(excel_fp, sheet_name='Sheet1')
    print("\n\nExcel Report File Content:")
    print(df)

    with open(ordered_unsuccessful_fp, "r", encoding="utf-8") as f:
        print("\n\nOrdered Unsuccessful Instances File Content:")
        print(f.read())

if __name__ == "__main__":
    source_lang = "Python"
    target_lang = "Java"
    model = "codegeex2-6b"
    report_dir = "my_report_dir"
    main(source_lang, target_lang, model, report_dir)
