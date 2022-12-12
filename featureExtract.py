import json
import os
import csv
import pandas as pd

def collect_conflict(data, conf_dict):
    for conflict in data['conflicting_chunks']:
        if 'label' in conflict:
            conf_dict.append({
                'A': conflict['a_contents'],
                'B': conflict['b_contents'],
                'base': conflict['base_contents'],
                'label': conflict['label'] if conflict['label'] == 'A' or conflict['label'] == 'B' else  'N'
            })


def extract_feature(conflict):
    return {
        **extract_keywords(conflict),
        **extract_edit_type(conflict),
        **extract_exist(conflict)
    }


def extract_keywords(conflict):
    def delete_brace(text):
        while text.find('{') == -1:
            start_pos = text.find('{')
            end_pos = text.find('}', start_pos)
            if end_pos == -1:
                break
            text = text[0: start_pos] + (text[end_pos + 1:] if end_pos != len(text) - 1 else [])
        return text

    def get_keywords(text, nums):
        text = delete_brace(text)
        start_pos = {text.find(keyword) : keyword for keyword in keywords if text.find(keyword) > -1}
        sorted_keywords = [start_pos[pos] for pos in sorted(start_pos.keys())]
        return [labels[key] for key in (sorted_keywords + ['empty']*nums)[:nums]]

    keywords = [
        'import',
        'private',
        'public',
        'protected',
        '.',
        '=',
        'if',
        'else',
        'for',
        'while',
        'return',
    ]
    # labels = {
    #     'empty':0,
    #     'import': 1,
    #     'private': 2,
    #     'public': 2,
    #     'protected': 2,
    #     'if': 3,
    #     'else': 3,
    #     'for': 4,
    #     'while': 4,
    #     '.': 5,
    #     '=': 6,
    #     'return': 7,
    # }
    labels = {
        'empty': 'empty',
        'import': 'import',
        'private': 'method',
        'public': 'method',
        'protected': 'method',
        'if': 'branch',
        'else': 'branch',
        'for': 'loop',
        'while': 'loop',
        '.': 'invocation',
        '=': 'assignment',
        'return': 'return',
    }
    num_kw = 3
    a_kw = get_keywords(conflict['A'], num_kw)
    b_kw = get_keywords(conflict['B'], num_kw)
    return {
        'a_keyword_1': a_kw[0],
        'a_keyword_2': a_kw[1],
        'a_keyword_3': a_kw[1],
        'b_keyword_1': b_kw[0],
        'b_keyword_2': b_kw[1],
        'b_keyword_3': a_kw[1],
    }


def extract_edit_type(conflict):
    def get_edit_type_line(cur, base):
        cur = [line for line in str.splitlines(cur) if len(line) > 0]
        base = [line for line in str.splitlines(base) if len(line) >0]
        if len(cur) == 0:
            return 0
        else:
            return len([line for line in cur if line in base])/len(cur)
    
    get_edit_type = get_edit_type_line
    return {
        'a_edit_type': get_edit_type(conflict['A'], conflict['base']),
        'b_edit_type': get_edit_type(conflict['B'], conflict['base']),
        'ab_edit_type':get_edit_type(conflict['A'], conflict['B'])
    }


def extract_exist(conflict):
    return {
        'a_exist': False if conflict['A'] == '' or conflict['A'] == '\n' else True,
        'b_exist': False if conflict['B'] == '' or conflict['B'] == '\n' else True,
        'base_exist': False if conflict['base'] == '' or conflict['base'] == '\n' else True
    }


conf_list = []
conflict_path = 'G:/merge/fse2022/automated-analysis-data/Java/'
for home, dirs, files in os.walk(conflict_path):
    for filename in files:
        if filename.endswith('.json'):
            with open(os.path.join(home, filename), 'r') as f:
                collect_conflict(json.load(f), conf_list)

featured_conflicts = [dict(extract_feature(conf), **conf) for conf in conf_list]

with open('./abm.json', 'w', encoding='utf-8') as jfile:
    jfile.write(json.dumps({"conf" : featured_conflicts}))

