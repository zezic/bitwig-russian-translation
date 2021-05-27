from dotenv import dotenv_values
import requests
import os
import shutil
import sys

config = dotenv_values()


class Translator:
    def __init__(self, iam_token, folder_id):
        self.token = iam_token
        self.folder_id = folder_id
        self.url = 'https://translate.api.cloud.yandex.net/translate/v2/translate'

    def translate(self, text):
        data = {
            'sourceLanguageCode': 'en',
            'targetLanguageCode': 'ru',
            'folderId': self.folder_id,
            'texts': [text]
        }
        headers = {'Authorization': 'Bearer {}'.format(self.token)}

        resp = requests.post(self.url, json=data, headers=headers).json()

        return resp.get('translations')[0].get('text')


tr = Translator(config.get('IAM_TOKEN'), config.get('FOLDER_ID'))


def translate_file(path):
    ru_file_path = path.replace('.pro', '_ru.pro')
    if os.path.exists(ru_file_path):
        return

    output = []
    with open(path, 'r') as fd:
        print('---')
        print(path)
        print('---')
        for line in fd.readlines():
            line = line
            if '=' in line:
                prop, sep, text = line.partition('=')
                chunks = text.split('\n')

                translated_chunks = []
                for chunk in chunks:
                    if len(chunk.strip()) == 0:
                        translated_chunks.append(chunk)
                        continue
                    translated_chunk = tr.translate(chunk)
                    translated_chunks.append(translated_chunk)

                translated = '\n'.join(translated_chunks)

                output.append('{}={}'.format(prop, translated))
                print(translated)
            else:
                output.append('{}'.format(line))

    with open(ru_file_path, 'w+') as fd:
        fd.writelines(output)


def translate_dir(dir_path):
    filenames = os.listdir(dir_path)
    for filename in filenames:
        if 'resources.properties' not in filename:
            continue
        translate_file('{}/{}'.format(dir_path, filename))


translate_dir('./localization')
translate_dir('./localization/model')
