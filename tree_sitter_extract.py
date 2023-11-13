from tree_sitter import Language, Parser

# Language.build_library(
#     'build/my-languages.so',

#     [
#         'vendor/tree-sitter-cpp',
#         'vendor/tree-sitter-kotlin',
#         'vendor/tree-sitter-java',
#     ]
# )
def create_treesitter_so():
    Language.build_library(
        'build/my-languages.so',

        [
            'vendor/tree-sitter-cpp',
            'vendor/tree-sitter-kotlin',
            'vendor/tree-sitter-java',
        ]
    )


def get_tree_sitter_features(conf_info, file_type):
    return extract_constructs_edit_info(conf_info, file_type)

def extract_constructs_edit_info(conf_info, file_type):
    CPP_LANG = Language('build/my-languages.so', 'cpp')
    KOTLIN_LANG = Language('build/my-languages.so', 'kotlin')
    JAVA_LANG = Language('build/my-languages.so', 'java')
    parser = Parser()
    if file_type == 'cpp':
        parser.set_language(CPP_LANG) 
    elif file_type == 'java':
        parser.set_language(JAVA_LANG)
    elif file_type == 'kotlin':
        parser.set_language(KOTLIN_LANG)
    a_cons_edit = extract_features_from_one_file(conf_info['a_path'], conf_info['a_contents'], parser)
    b_cons_edit = extract_features_from_one_file(conf_info['b_path'], conf_info['b_contents'], parser)
    base_cons_edit = extract_features_from_one_file(conf_info['base_path'], conf_info['base_contents'], parser)
    return {
        'a_cons_edit' : a_cons_edit,
        'b_cons_edit' : b_cons_edit,
        'base_cons_edit' : base_cons_edit,
    }
    
#第二参数 region 即a对应的conflict中的区域
def extract_features_from_one_file(file_path, region, parser):
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
            return match_index[0], match_index[0] + loc
        else:
            return match_index[0], match_index[0] + loc

    with open(file_path, 'r', errors='ignore') as file:
        codelines = [line.strip('\n') for line in file.readlines()]
        conflines = str.splitlines(region)
        if len(conflines) == 0:
            return {
                    'constructs' :[],
                    'identifiers' : [],
                }
        startline, endline = get_begin_end(codelines, conflines)
        if startline < 0:
            if startline == -1:
                return {
                    'constructs' :[],
                    'identifiers' : [],
                }
            elif startline == -2:
                return {
                    'constructs' :[],
                    'identifiers' : [],
                }
            else:
                pass
        return get_constructs_and_edit_info(file_path, startline, endline, parser)

def get_constructs_and_edit_info(file_path, startline, endline, parser):
    def search_cons(root, i, j, cons):
        if(root.start_point[0] >= startline and root.end_point[0] < endline):
            cons.append(root)
        else:
            for node in root.children:
                search_cons(node, i, j, cons)

    def search_ids(root, i, j, ids):
        if(root.start_point[0] >= startline and root.end_point[0] < endline and root.type == 'identifier'):
            ids.append(root)
        for node in root.children:
            search_ids(node, i, j, ids)

    with open(file_path, 'r', errors='ignore') as f:
        print("parse : " + file_path)
        code = f.read()
        ast = parser.parse(code.encode())
        root = ast.root_node
        constructs = []
        identifiers = []
        search_cons(root, startline, endline, constructs)
        search_ids(root, startline, endline, identifiers)
        return {
            'constructs' : [cons.type for cons in constructs],
            'identifiers' : list(set([str(id.text, 'utf-8') for id in identifiers]))
        }


# parser = Parser()
# parser.set_language(KOTLIN_LANG)
# with open(r"G:\mergebot\output\conflictFiles\tachiyomi\100_a.kt", 'r', errors='ignore') as f:
#     code = f.read()
#     ast = parser.parse(code.encode())
#     print(ast.root_node.text)

# Language.build_library(
#     'build/my-languages.so',

#     [
#         'vendor/tree-sitter-cpp',
#         'vendor/tree-sitter-kotlin',
#         'vendor/tree-sitter-java',
#     ]
# )