import json
import os
import csv
import pandas as pd
import re
import functools
import extract_metadata
import shutil
import classify_utils
import train_utils

# 传入gitMergeScenario获得的数据集
# 得到可以用于训练的json文件
def conflict_process_pipeline(conflicts_path, project_name, file_type, work_dir):
    json_path = work_dir + "/datasets/" + file_type + '/' + project_name + ".json"
    conflict_data_process_pipeline(conflicts_path, json_path)
    train_utils.train_model(project_name, json_path, file_type, save_model = True, save_path = './models/')


def conflict_data_process_pipeline(conflicts_path, json_path):
    # index_files_path = "./index_conflict_files/" + project_name + '/'
    extract_metadata_for_one_gitrepo(conflicts_path)
    # move_and_index_conflict_files(conflicts_path, index_files_path)
    collect(conflicts_path, json_path)


# 从gitMergeScenario中获得的数据集，首先抽取出metadata，放在对应的conflict tuple文件夹内
# repo_path 即被gitMS处理之后得到的数据集的路径
def extract_metadata_for_one_gitrepo(repo_path):
    print('extract_metadata')
    extract_metadata.extract_metadata_file(repo_path)

# deprecated
# 把得到metadata之后的conflict tuple移动到一个文件夹内部并编号
def move_and_index_conflict_files(conflict_path, save_path):
    print('move_and_index_conflict_files')
    chunk_index = 0
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print(f"{save_path} created successfully.")
    else:
        return
    for home, dirs, files in os.walk(conflict_path):
        for filename in files:
            if filename.endswith('metadata.json') and os.path.isfile(os.path.join(home, 'metadata.json')) and os.path.isfile(os.path.join(home, 'ours.java')) and os.path.isfile(os.path.join(home, 'theirs.java')) and os.path.isfile(os.path.join(home, 'conflict.java')) and os.path.isfile(os.path.join(home, 'resolve.java')):
                shutil.copy(os.path.join(home, 'metadata.json'), os.path.join(save_path, str(chunk_index) + '_' + 'metadata.json'))
                shutil.copy(os.path.join(home, 'ours.java'), os.path.join(save_path, str(chunk_index) + '_' + 'a.java'))
                shutil.copy(os.path.join(home, 'theirs.java'), os.path.join(save_path, str(chunk_index) + '_' + 'b.java'))
                shutil.copy(os.path.join(home, 'conflict.java'), os.path.join(save_path, str(chunk_index) + '_' + 'merged.java'))
                shutil.copy(os.path.join(home, 'resolve.java'), os.path.join(save_path, str(chunk_index) + '_' + 'resolved.java'))
                if os.path.isfile(os.path.join(home, 'base.java')):
                    shutil.copy(os.path.join(home, 'base.java'), os.path.join(save_path, str(chunk_index) + '_' + 'base.java'))
                chunk_index += 1


# 构建数据集相关的函数,从得到metadata文件之后的tuple集合中抽取出所有conflict
# 并对提取这些conflict的feature，形成一个json文件，用以训练模型。
def collect(index_repo_path, json_path=""):
    print("collect conflict to json file")
    conf_list = []
    conflict_path = index_repo_path
    for home, dirs, files in os.walk(conflict_path):
        for filename in files:
            if filename.endswith('metadata.json'):
                file_suffix = ""
                with open(os.path.join(home, filename), 'r', encoding='utf-8') as meta:
                    file_suffix = json.load(meta)['filetype']
                fileIndex = filename[:filename.find('_')]
                filesize = os.path.getsize(os.path.join(home, fileIndex + '_a' + file_suffix))
                if filesize < 102400: #1M = 1048576 ,100K = 102400
                    with open(os.path.join(home, filename), 'r', encoding='utf-8') as f:
                        tmp = json.load(f)["conflicting_chunks"]
                        a_path = os.path.join(home, fileIndex + '_a' + file_suffix)
                        b_path = os.path.join(home, fileIndex + '_b' + file_suffix)
                        base_path = os.path.join(home, fileIndex + '_base' + file_suffix)
                        merged_path = os.path.join(home, fileIndex + '_merged' + file_suffix)
                        for cur_conf in tmp:
                            file_type = ""
                            if(file_suffix == '.java'):
                                file_type = "java"
                            elif(file_suffix == '.kt'):
                                file_type = 'kotlin'
                            else:
                                file_type = 'cpp'
                            conf_list.append(dict(classify_utils.get_featured_conflict(cur_conf, merged_path, a_path, b_path, base_path, file_type), **cur_conf))
    
    if not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    with open(json_path, 'w+', encoding='utf-8') as jfile:
        jfile.write(json.dumps({"conf" : conf_list}))