import json
import os
import csv
import pandas as pd
import re
import functools
import tree_sitter_extract
import joblib
import numpy as np
import chardet

# parameter: conf_info, path of [conf,left,right,base], file_type ['cpp', 'java', 'kotlin']
# return featured conflict
def get_featured_conflict(conf_info, conf_path, a_path, b_path, base_path, file_type):
    return extract_feature({
        "conf_path" : conf_path,
        'a_path' : a_path,
        'b_path' : b_path,
        'base_path' : base_path,
        **conf_info,
    }, file_type)


def count_chunk_num(conflict_path):
    try:
        with open(conflict_path, 'r', encoding='utf-8') as m:
            merged =  [line for line in m.readlines()]
    except UnicodeDecodeError as e:
        with open(conflict_path, 'rb') as f:
            content = f.read()
            result = chardet.detect(content)
            encoding = result['encoding']
        with open(conflict_path, 'r', encoding=encoding) as m:
            merged =  [line for line in m.readlines()]
    chunk_num = 0
    for line in merged:
        if line.startswith('<<<<<'):
            chunk_num += 1
    return chunk_num


def extract_feature(conf_info, file_type):
    cons_and_edit = tree_sitter_extract.get_tree_sitter_features(conf_info, file_type)
    a_constructs = cons_and_edit['a_cons_edit']['constructs']
    a_identifers = cons_and_edit['a_cons_edit']['identifiers']
    b_constructs = cons_and_edit['b_cons_edit']['constructs']
    b_identifers = cons_and_edit['b_cons_edit']['identifiers']
    base_identifers = cons_and_edit['base_cons_edit']['identifiers']
    chunk_num = count_chunk_num(conf_info['conf_path'])
    return {
        'a_constructs' : process_constructs(a_constructs),
        'b_constructs' : process_constructs(b_constructs),
        'a_id_sim' : get_identifier_similarity(a_identifers, base_identifers),
        'b_id_sim' : get_identifier_similarity(b_identifers, base_identifers),
        'ab_id_sim' : get_identifier_similarity(a_identifers, b_identifers),
        'chunk_num' : chunk_num,
        **get_line_similarity(conf_info),
        **get_chunk_info(conf_info),
    }

def get_chunk_info(conf_info):
    a_line_num = conf_info['a_contents'].count('\n')
    b_line_num = conf_info['b_contents'].count('\n')
    o_line_num = conf_info['base_contents'].count('\n')
    return {
        'a_line_num' : a_line_num,
        'b_line_num' : b_line_num,
        'o_line_num' : o_line_num,
        'ab_line_diff' : a_line_num - b_line_num,
        'ao_line_diff' : a_line_num - o_line_num,
        'bo_line_diff' : b_line_num - o_line_num,
    }

def process_constructs(constructs):
    seen = set()
    result = [x for x in constructs if x not in ['{','}',',','(',')'] and not (x in seen or seen.add(x))]
    return result

def get_identifier_similarity(a_ids, b_ids):
    if len(a_ids) == 0 or len(b_ids) == 0:
        return 0
    same_ids = [token for token in a_ids if token in b_ids]
    return len(same_ids) / len(a_ids)


def get_line_similarity(conf_info):
    def get_edit_type_line(cur, base):
        cur = [line for line in str.splitlines(cur) if len(line) > 0]
        base = [line for line in str.splitlines(base) if len(line) >0]
        if len(cur) == 0:
            return 0
        else:
            return len([line for line in cur if line in base])/len(cur)
    return {
        'a_line_sim': get_edit_type_line(conf_info['a_contents'], conf_info['base_contents']),
        'b_line_sim': get_edit_type_line(conf_info['b_contents'], conf_info['base_contents']),
        'ab_line_sim':get_edit_type_line(conf_info['a_contents'], conf_info['b_contents']),
    }



# 调用模型
# 通过project_name 来查找调用哪一个模型
def predict(project_name, file_type, v1, v2, base, conf):
    vec_clf = get_model(project_name, file_type)
    print(conf)
    conflict_chunks = get_conf_info(conf)
    print(conflict_chunks)
    featured_conflicts = [get_featured_conflict(chunk, conf, v1, v2, base, file_type) for chunk in conflict_chunks]
    print(featured_conflicts)
    labels_proba = [vec_clf.predict_proba(chunk) for chunk in featured_conflicts]
    print("probability of [v1, v2, cb, cc, nc] : ")
    print(labels_proba)
    labels = ['V1', 'V2', 'CB', 'CC', 'NC']
    ret = []
    for i in range(len(labels_proba)):
        ret.append({
            'index': i,
            'confidence':np.max(labels_proba[i]),
            'label': labels[np.argmax(labels_proba[i])]
        })
    return ret


def filter_features(featured_conflict):
    return featured_conflict


def get_conf_info(conf_path):
    chunks = []
    with open(conf_path, 'r', encoding='utf-8') as file:
        cur_chunk = {
            'A':[],
            'B':[],
            'base':[],
        }
        lines = file.readlines()
        f = 'none'
        for i in range(len(lines)):
            if lines[i].startswith('<<<<<'):
                f = 'A'
                continue
            if lines[i].startswith('|||||'):
                f = 'base'
                continue
            if lines[i].startswith('======'):
                f = 'B'
                continue
            if lines[i].startswith('>>>>>'):
                f = 'none'
                chunks.append({
                    'a_contents': ''.join(cur_chunk['A']),
                    'b_contents': ''.join(cur_chunk['B']),
                    'base_contents': ''.join(cur_chunk['base'])
                })
                cur_chunk = {
                    'A':[],
                    'B':[],
                    'base':[],
                }
            if f != 'none':
                cur_chunk[f].append(lines[i])
    return chunks


def get_model(project_name, file_type):
    model_path = "./models/" + project_name + ".joblib"
    return joblib.load(model_path)


