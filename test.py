# import classify_utils
# import dataset_utils
# import train_utils
# # dataset_utils.conflict_process_pipeline( 'G:\mergebot\output\conflictFiles\platform_external_protobuf\\', 'platform_external_protobuf','cpp', 'G:\\mergebot\\')

# # train_utils.train_model("", r"G:\mergebot\datasets\platform_external_protobuf.json")
# # train_utils.train_model("", r"G:\mergebot\datasets\tachiyomi.json")
# print(classify_utils.predict('hibernate-orm', 'java', './web_service/testcase/a.java',
#      './web_service/testcase/b.java',
#      './web_service/testcase/base.java',
#      './web_service/testcase/merged.java'))


# import requests
# import json 
# headers = {
# "Content-Type": "application/json;charset=utf8"
# }

# data = {
#     'version1' : r'G:\project\python\CC\testcase\a.java',
#     'version2' : r'G:\project\python\CC\testcase\b.java',
#     'conflict': r'G:\project\python\CC\testcase\merged.java',
#     'base': r'G:\project\python\CC\testcase\base.java',
#     'path': 'cc',
#     'source': 'b1',
#     'target': 'b2',
#     'filetype': 'java',
# }
# r = requests.post('http://127.0.0.1:5000/predict', data=json.dumps(data), headers=headers)
# state = json.loads(r.text)
# print(state)

# import dataset_utils
# import train_utils
# import config

# dataset_utils.conflict_process_pipeline('/work/gitMergeScenario/conflict_files/cpp/av', 'av', 'cpp', config.CONFLICT_PATH)
# dataset_utils.conflict_data_process_pipeline('/work/testcase1', '/work/testcase1/1.json')

# train_utils.evaluate_model('telephony', "/work/gitMergeScenario/datasets/java/telephony.json", save_csv=True)
# train_utils.evaluate_model('av', "/work/gitMergeScenario/datasets/cpp/av.json", save_csv=True)
# train_utils.evaluate_model('layoutlib', "/work/gitMergeScenario/datasets/java/layoutlib.json", save_csv=True)
# train_utils.evaluate_model('wifi', "/work/gitMergeScenario/datasets/java/wifi.json", save_csv=True)
# train_utils.evaluate_model('base', "/work/gitMergeScenario/datasets/java/base.json", save_csv=True)
# train_utils.evaluate_model('Notes', "/work/gitMergeScenario/datasets/kotlin/Notes.json", save_csv=True)


import dataset_utils
import train_utils
import config
import extract_metadata

# extract_metadata.extract_metadata_file('G:\project\python\CC\junit4')
dataset_utils.collect('G:\project\python\CC\junit4', 'G:\project\python\CC\\results\junit4.json')
# dataset_utils.conflict_process_pipeline('/work/gitMergeScenario/conflict_files/cpp/av', 'av', 'java', config.CONFLICT_PATH)