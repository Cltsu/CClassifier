import dataset_utils
import train_utils
import config
import json
import os
import sys

# 将json文件合成一个lang.json文件，并使用这个json来训练模型
def train_universal_model(lang):
    jsons_path = config.CONFLICT_PATH + '/datasets/' + lang
    data = []
    for filename in os.listdir(jsons_path):
        if(filename.endswith(".json") and filename != lang + '.json'):
            file_path = os.path.join(jsons_path, filename)
            print(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)['conf']
                if len(json_data) > 1000:
                    train_utils.train_model(filename[:filename.index('.')], file_path, lang, save_model=True, save_path='./models/')
                data += json_data

    lang_dataset_path = os.path.join(jsons_path, lang + '.json')
    with open(lang_dataset_path, 'w+', encoding='utf-8') as jfile:
        jfile.write(json.dumps({"conf" : data}))

    train_utils.train_model('' , lang_dataset_path, lang,  save_model = True, save_path = './models/')


# 得到metadata和json数据集
def data_process(lang):
    conflict_path = os.path.join(config.CONFLICT_PATH, 'conflict_files', lang)
    for reponame in os.listdir(conflict_path):
        conflict_path_repo = os.path.join(conflict_path, reponame)
        dataset_utils.conflict_data_process_pipeline(conflict_path_repo, config.CONFLICT_PATH + "/datasets/" + lang + '/' + reponame + ".json")



if(len(sys.argv) == 1):
    print('select from [cpp, java, kotlin]')
else:
    lang = sys.argv[1]
    data_process(lang)
    train_universal_model(lang)