import json
import os
import chardet

file_suffix = ""

def extract_metadata_from_m_and_r(m, r):
    conf_list = []
    m = ['<\start>'] + m + ['<\end>']
    r = ['<\start>'] + r + ['<\end>']
    cstart = [len(m) + 1]
    c2 = [0]
    c3 = [0]
    cend = [-1]
    for i in range(len(m)):
        if m[i].startswith('<<<<<'):
            cstart.append(i)
        if m[i].startswith('|||||'):
            c2.append(i)
        if m[i].startswith('======'):
            c3.append(i)
        if m[i].startswith('>>>>>'):
            cend.append(i)
    if not len(cstart) == len(c2) == len(c3) == len(cend):
        return []
        # raise Exception('invalid file')
    conf_nums = len(cstart)
    for i in range(1, conf_nums):
        conf = {
            'prefix': m[cend[i - 1] + 1 : cstart[i]][-5:],
            'suffix': m[cend[i] + 1 : cstart[(i + 1) % conf_nums]][:5],
            'a_contents': m[cstart[i] + 1 : c2[i]],
            'base_contents':m[c2[i] + 1 : c3[i]],
            'b_contents': m[c3[i] + 1 : cend[i]],
            'chunk_num' : conf_nums - 1,
            'file_suffix': file_suffix
        }
        find_res(conf, r)
        conf_list.append(conf)
    return conf_list


def compute_label(conf):
    a = filter_blank_line(conf['a_contents'])
    b = filter_blank_line(conf['b_contents'])
    res = filter_blank_line(conf['resolve'])
    if a == res:
        return 'A'
    elif b == res:
        return 'B'
    elif a + b == res:
        return "CC12"
    # elif len(res) == 0:
    #     return "EM"
    elif b + a == res:
        return "CC21"
    elif all([line in a or line in b for line in res]):
        return 'CB'
    else:
        return 'NC'


def filter_blank_line(lines):
    return [line for line in lines if not is_blank(line)]


def is_blank(s):
    if s == '':
        return True
    for c in s:
        if c not in [' ', '\n', '\t']:
            return False
    return True


def find_res(conf, resolve):
    def best_match(fix, res):
        assert len(fix) >= 0
        if len(fix) == 0:
            return []
        
        cur_index = []
        max_match = 0
        for i in range(len(res)):
            for j in range(len(fix)):
                if fix[j] != res[i + j]:
                    break
                if j > 20:
                    break

                if j + 1 > max_match:
                    cur_index = []
                    max_match = j + 1
                    cur_index.append(i)
                elif j + 1 == max_match:
                    cur_index.append(i)

        return cur_index
    

    def try_match(fix, res):
        bm = best_match(fix, res)
        if len(bm) > 1 and is_blank(fix[0]) and len(fix) > 1:
            tmp_match = best_match(fix[1:], res)
            if len(tmp_match) == 1:
                bm = tmp_match
        return bm


    best_match_end = try_match(conf['suffix'], resolve)
    best_match_start = [len(resolve) - 1 - i for i in try_match(conf['prefix'][::-1], resolve[::-1])]
    end_len = len(best_match_end)
    start_len = len(best_match_start)
    if end_len == 0 or start_len == 0:
        conf['res_state'] = 'not_found'
        # conf['label'] = 'NC'
        return 
    elif end_len == 1 and start_len == 1:
        res_end = best_match_end[0]
        res_start = best_match_start[0]
    elif end_len == 1 and start_len != 1:
        res_end = best_match_end[0]
        tmp = [i for i in best_match_start if i < res_end]
        if len(tmp) == 0:
            res_start = 1
            res_end = 0
        else:
            res_start = max(tmp)
    elif end_len != 1 and start_len == 1:
        res_start = best_match_start[0]
        tmp = [i for i in best_match_end if i > res_start]
        if len(tmp) == 0:
            res_start = 1
            res_end = 0
        else:
            res_end = min(tmp)
    else:
        conf['res_state'] = 'ambiguous'
        # conf['label'] = 'NC'
        return 

    if res_start >= res_end:
        conf['res_state'] = 'not_found'
        # conf['label'] = 'NC'
    else:
        conf['res_state'] = 'found'
        conf['resolve'] = resolve[res_start + 1 : res_end]
        conf['label'] = compute_label(conf)
    

def flatten_text(confs):
    for conf in confs:
        conf['a_contents'] = ''.join(conf['a_contents'])
        conf['b_contents'] = ''.join(conf['b_contents'])
        conf['base_contents'] = ''.join(conf['base_contents'])
        if 'resolve' in conf.keys():
            conf['resolve'] = ''.join(conf['resolve'])
    return confs


def extract_metadata_file(project_path):
    conf_list = []
    for home, dirs, files in os.walk(project_path):
        for filename in files:
            if 'merged' in filename:
                index = filename[:filename.index('_') + 1]
                suffix = filename[filename.index('.'):]
                print('processing' + home + filename)

                conflict_path = os.path.join(home, index + 'merged' + suffix)
                resolve_path = os.path.join(home, index + 'resolved' + suffix)
                global file_suffix
                file_suffix = suffix

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

                try:
                    with open(resolve_path, 'r', encoding='utf-8') as r:
                        resolved =  [line for line in r.readlines()]
                except UnicodeDecodeError as e:
                    with open(resolve_path, 'rb') as f:
                        content = f.read()
                        result = chardet.detect(content)
                        encoding = result['encoding']
                    with open(resolve_path, 'r', encoding=encoding) as m:
                        resolved =  [line for line in m.readlines()]

                cur_confs = {
                        "conflicting_chunks": flatten_text(extract_metadata_from_m_and_r(merged, resolved)),
                        'filename': home,
                        'filetype': file_suffix
                    }
                conf_list.append(cur_confs)
                with open(os.path.join(home, index + 'metadata.json'), 'w', encoding='utf-8') as j:
                    j.write(json.dumps(cur_confs))
