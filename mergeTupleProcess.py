import json
import os


def extract_metadata(m, r):
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
            'prefix': m[cend[i - 1] + 1 : cstart[i]],
            'suffix': m[cend[i] + 1 : cstart[(i + 1) % conf_nums]],
            'a_contents': m[cstart[i] + 1 : c2[i]],
            'base_contents':m[c2[i] + 1 : c3[i]],
            'b_contents': m[c3[i] + 1 : cend[i]],
        }
        find_res(conf, r)
        conf_list.append(conf)
    return conf_list


def compute_label(conf):
    a = conf['a_contents']
    b = conf['b_contents']
    res = conf['resolve']
    if a == res:
        return 'A'
    if b == res:
        return 'B'
    return 'N'


def find_res(conf, resolve):
    def best_match(fix, res):
        if len(fix) == 0:
            return -1
        cur_index = -1
        max_match = 0
        for i in range(len(res)):
            for j in range(len(fix)):
                if fix[j] != res[i + j]:
                    break
                if j + 1 > max_match:
                    max_match = j + 1
                    cur_index = i
                if j > 5:
                    break
        return cur_index
    res_end = best_match(conf['suffix'], resolve)
    res_start = len(resolve) - 1 - best_match(conf['prefix'][::-1], resolve[::-1])
    if res_end <= res_start:
        conf['res_state'] = 'end<start'
        return
    conf['resolve'] = resolve[res_start + 1 : res_end]
    conf['label'] = compute_label(conf)
    

tuples_path = 'G:\\merge\\output\\conflictFiles\\junit4\\'
# tuples_path = r'G:\merge\output\conflictFiles\aosp\system\apex\0dce0bc5b5d9044af78c076c0c50c74decf0b72a\tests\src\com\android\tests\apex\ApexdHostTest.java'
counter = 1
conf_list = []
for home, dirs, files in os.walk(tuples_path):
    for filename in files:
        if filename.endswith('conflict.java'):
            print('processing' + home + filename)
            fileIndex = str(counter)
            counter += 1
            try:
                with open(os.path.join(home, 'conflict.java'), 'r', encoding='utf-8') as m:
                    merged =  [line for line in m.readlines()]
            except UnicodeDecodeError as e:
                with open(os.path.join(home, 'conflict.java'), 'r', encoding='ansi') as m:
                    merged =  [line for line in m.readlines()]
            try:
                with open(os.path.join(home, 'resolve.java'), 'r', encoding='utf-8') as r:
                    resolved =  [line for line in r.readlines()]
            except UnicodeDecodeError as e:
                with open(os.path.join(home, 'resolve.java'), 'r', encoding='ansi') as r:
                    resolved =  [line for line in r.readlines()]
            cur_confs = {   
                    "conflicting_chunks": extract_metadata(merged, resolved),
                    'filename': home,
                }
            conf_list.append(cur_confs)
            # with open(os.path.join(home, 'metadata.json'), 'w', encoding='utf-8') as j:
                # j.write(json.dumps(cur_confs))

with open('./junit4.json', 'w', encoding='utf-8') as j:
    j.write(json.dumps({'conf':conf_list}))