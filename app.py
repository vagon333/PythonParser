import sys
import os
import threading
import subprocess
from flask import Flask
from skeleton import get_news_source_for_parsing


news_buffer_size = 20
thread_pool_size = 5
thread_list = []


class SubprocessThread(threading.Thread):
    def __init__(self, cmd, source_id):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.source_id = source_id
        threading.Thread.__init__(self)

    def run(self):
        process = subprocess.Popen(self.cmd, shell=True, env={
            **os.environ,
            'PYTHONPATH': ';'.join(sys.path)
        })
        print(f'Thread news source id {self.source_id} started')
        process.wait()
        if process.returncode != 0:
            print(
                '\u001b[31m'
                + f'News source {self.source_id} unsuccessfully finished'
                + '\u001b[0m'
            )
        else:
            print(
                '\u001b[32m'
                + f'News source {self.source_id} successfully finished'
                + '\u001b[0m'
            )


app = Flask(__name__)
script_folder_name = 'scripts'
script_folder = os.path.join(app.root_path, script_folder_name)
sys.path.append(script_folder)
if not os.path.exists(script_folder):
    os.makedirs(script_folder)


def compile_python_script_file(news_source_id, python_code, file_folder):
    file_name = f'partial_{news_source_id}.py'
    file_path = os.path.join(file_folder, file_name)
    with open(file_path, 'w', newline='\n') as python_script:
        python_script.write(python_code)
    return file_name


@app.route('/get_news')
# @app.route('/get_news', methods=['POST'])
def get_news():
    global thread_list
    thread_list = [thread for thread in thread_list if thread.is_alive()]
    source_id_in_progress_list = [
        thread.source_id for thread in thread_list
    ]
    news_source_dict_list = get_news_source_for_parsing()
    print(f'Start threading')
    for news_source_dict in news_source_dict_list:
        news_source_id = news_source_dict['cgNewsSourceID']
        if news_source_id not in source_id_in_progress_list:
            news_source_url = news_source_dict['NewsSourceUrl']
            python_code = news_source_dict['NewsExtractionSourceCode']
            file_name = compile_python_script_file(
                news_source_id, python_code, script_folder
            )
            cmd = (
                'skeleton.py '
                f'--partial_file_name={file_name} '
                f'--source_id={news_source_id} '
                f'--source_url="{news_source_url}" '
                f'--buffer_size={news_buffer_size} '
                f'--pool_size={thread_pool_size} '
            )
            thread = SubprocessThread(cmd, news_source_id)
            thread_list.append(thread)
    for thread in thread_list:
        if not thread.is_alive():
            thread.start()
    threads_string = '<br />'.join(
            [
                f'Source ID {source_id}' for source_id
                in source_id_in_progress_list
            ]
        )
    return (
            f'{len(source_id_in_progress_list)} resources left to load<br />'
            + ('-' * 25) + '<br />' + threads_string
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
