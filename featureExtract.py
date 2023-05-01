import json
import os
import csv
import jpype
import pandas as pd
import re
import functools

def collect_conflict(data, conf_dict, fileIndex):
    def get_class_5(conflict):
        if conflict['label'] == 'A' or conflict['label'] == 'B':
            return conflict['label']
        if conflict['label'] == 'AB' or conflict['label'] == 'BA':
            return 'concat'
        if conflict['label'] in ['REM-BASE-B', 'REM-BASE-AB','REM-BASE-BA','REM-BASE-A']:
            return 'rem-b-comb'
        a_text = str.split(conflict['a_contents'], '\n') 
        b_text = str.split(conflict['b_contents'], '\n')
        res_text = str.split(conflict['res_region'], '\n')
        # a_f = functools.reduce(lambda l,r : l and r in res_text, a_text, True)
        for i in range(len(res_text)):
            if res_text[i] not in a_text and res_text[i] not in b_text and not is_blank(res_text[i]):
                return 'new'
        return 'comb'

    cur_repo = data['repo']
    for conflict in data['conflicting_chunks']:
        if 'label' in conflict and conflict['label'] != 'RES_FILE_EMPTY':
            conf_dict.append({
                'A': conflict['a_contents'],
                'B': conflict['b_contents'],
                'base': conflict['base_contents'],
                'resolution': conflict['res_region'],
                'label': get_class_5(conflict),
                'pre_label': conflict['label'],
                'index': fileIndex,
                'repo': cur_repo
            })

def is_blank(s):
    if s == '':
        return True
    for c in s:
        if c not in [' ', '\n', '\t']:
            return False
    return True


def extract_feature(conflict):
    return {
        **extract_keywords_from_AST(conflict),
        # **extract_keywords(conflict),
        **extract_edit_type(conflict),
        **extract_exist(conflict)
    }


def statistic_keywords_num(conflict):
    def get_keyword_from_javapaser(filename, region):
        conf_dir = 'G:/merge/fse2022/automated-analysis-data/Java/'
        with open(conf_dir + filename, 'r', encoding='utf-8') as javafile:
            codelines = [line.strip('\n') for line in javafile.readlines()]
            conflines = str.splitlines(region)
            if len(region) == 0:
                return -1, -1
            if conflines[0] == "":
                conflines = conflines[1:]
            startline, endline = get_begin_end(codelines, conflines)
            if startline < 0:
                return startline, endline
            # invocate JAR
            [dn, fdn] = Extractor.call(filename, startline, endline)
            return dn, fdn

    index = conflict['index']
    a_filename = str(index) + '_a.java'
    b_filename = str(index) + '_b.java'
    a_dn, a_fdn = get_keyword_from_javapaser(a_filename, conflict['A'])
    b_dn, b_fdn = get_keyword_from_javapaser(b_filename, conflict['B'])
    return [a_dn, a_fdn, b_dn, b_fdn]


def get_begin_end(codelines, conflines):
    if len(conflines) == 0:
        return -1, -1
    loc = len(conflines)
    match_index = []
    for i in range(len(codelines) - loc + 1):
        if codelines[i: i + loc] == conflines:
            match_index.append(i)
    if len(match_index) == 0:
        return -2, loc
    elif len(match_index) == 1:
        return match_index[0] + 1, match_index[0] + loc + 1
    else:
        return match_index[0] + 1, match_index[0] + loc + 1



def extract_keywords_from_AST(conflict):
    def get_keyword_from_javapaser(filename, region, index):
        if len(region) == 0:
            return ['empty'], ['empty']
        conf_dir = 'G:/merge/fse2022/automated-analysis-data/Java/'
        with open(conf_dir + filename, 'r', encoding='utf-8') as javafile:
            codelines = [line.strip('\n') for line in javafile.readlines()]
            conflines = str.splitlines(region)
            if conflines[0] == "":
                # mergebert 数据集的问题，会在 b_region 前自动加一个 \n
                conflines = conflines[1:]
            if len(conflines) == 0:
                return ['empty'], ['empty']
            startline, endline = get_begin_end(codelines, conflines)
            if startline < 0:
                if startline == -1:
                    return ['empty'], ['empty']
                elif startline == -2:
                    return ['notfound'], ['empty']
                else:
                    return ['unknown'], ['empty']
                # elif startline == -3:              
                #     return ['multple'], ['empty']
            # invoke JAR
            [kw, fkw] = Extractor.call(filename, startline, endline)
            kw = [str(word) for word in kw]
            fkw = [str(word) for word in fkw]
            return kw, fkw

    index = conflict['index']
    a_filename = str(index) + '_a.java'
    b_filename = str(index) + '_b.java'
    a_kw, a_fkw = get_keyword_from_javapaser(a_filename, conflict['A'], index)
    b_kw, b_fkw = get_keyword_from_javapaser(b_filename, conflict['B'], index)
    if len(a_fkw) == 1:
        a_fkw.append('empty')
    if len(b_fkw) == 1:
        b_fkw.append('empty')
    # return {
    #     'a_kw1': a_fkw[0],
    #     'a_kw2': a_fkw[1],
    #     'b_kw1': b_fkw[0],
    #     'b_kw2': b_fkw[1]
    # }
    return {
        'a_kw': a_kw,
        'a_fkw': a_fkw,
        'b_kw': b_kw,
        'b_fkw': b_fkw
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
        # 'a_keyword_3': a_kw[1],
        'b_keyword_1': b_kw[0],
        'b_keyword_2': b_kw[1],
        # 'b_keyword_3': a_kw[1],
    }


def extract_edit_type(conflict):
    def get_edit_type_line(cur, base):
        cur = [line for line in str.splitlines(cur) if len(line) > 0]
        base = [line for line in str.splitlines(base) if len(line) >0]
        if len(cur) == 0:
            return 0
        else:
            return len([line for line in cur if line in base])/len(cur)

    def get_edit_type_token(cur, base):
        if cur == "" or base == "":
            return 0
        cur_tokens = Tokenizer.javaParserCodeStr(cur)
        base_tokens = Tokenizer.javaParserCodeStr(base)
        java_reserved_words = ['boolean', 'byte', 'char', 'double', 'false', 'float', 'int', 'long', 'new', 'short', 'true', 'void', 
            'instanceof', 'break', 'case', 'catch', 'continue', 'default', 'do', 'else', 'for', 'if', 'reture', 'switch', 'try', 'while', 
            'finally', 'throw', 'this', 'super', 'abstract', 'fianal', 'native', 'private', 'protected', 'public', 'static', 'synchronized', 
            'transient', 'volatile', 'class', 'extend', 'implements', 'interface', 'ackage', 'import', 'throws']
        regex = '[a-z|A-Z|_][a-z|A-Z|_|0-9]*'
        cur_tokens = [token for token in cur_tokens if token not in java_reserved_words and re.fullmatch(regex, str(token))]
        base_tokens = [token for token in base_tokens if token not in java_reserved_words and re.fullmatch(regex, str(token))]
        # print(cur_tokens)
        # print(base_tokens)
        # print('-----------------')
        same_token = [token for token in cur_tokens if token in base_tokens]
        if len(cur_tokens) == 0:
            return 0
        return len(same_token) / len(cur_tokens)

    get_edit_type = get_edit_type_line
    return {
        'a_edit_type': get_edit_type(conflict['A'], conflict['base']),
        'b_edit_type': get_edit_type(conflict['B'], conflict['base']),
        'ab_edit_type':get_edit_type(conflict['A'], conflict['B']),
        'a_token_sim': get_edit_type_token(conflict['A'], conflict['base']),
        'b_token_sim': get_edit_type_token(conflict['B'], conflict['base'])
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
        if filename.endswith('metadata.json'):
        # if filename == '20_metadata.json':
            fileIndex = filename[:filename.find('_')]
            filesize = os.path.getsize(os.path.join(home, fileIndex + '_a.java'))
            if filesize < 102400: #1M = 1048576 ,100K = 102400
                with open(os.path.join(home, filename), 'r', encoding='utf-8') as f:
                    collect_conflict(json.load(f), conf_list, fileIndex)


jarPath = os.path.join(os.path.abspath('G:/project/java/ASTExtract/out/artifacts/ASTExtract_jar/ASTExtract.jar'))
jvmPath = jpype.getDefaultJVMPath()
jpype.startJVM(jvmPath, '-ea', '-Djava.class.path=%s' % (jarPath))
javaClassExtractor = jpype.JClass('nju.merge.ASTExtractor')
Extractor = javaClassExtractor()
javaClassTokenize = jpype.JClass('nju.merge.Tokenize')
Tokenizer = javaClassTokenize()


featured_conflicts = [dict(extract_feature(conf), **conf) for conf in conf_list]
with open('./c5.json', 'w', encoding='utf-8') as jfile:
    jfile.write(json.dumps({"conf" : featured_conflicts}))


# keywords_num_statistic = [statistic_keywords_num(conf) for conf in conf_list]
# with open('./tmp1.json', 'w', encoding='utf-8') as jfile:
#     jfile.write(json.dumps({"conf" : keywords_num_statistic}))


# keywords_num_statistic = [extract_edit_type(conf) for conf in conf_list]
# with open('./tmp1.json', 'w', encoding='utf-8') as jfile:
#     jfile.write(json.dumps({"conf" : keywords_num_statistic}))


jpype.shutdownJVM()



