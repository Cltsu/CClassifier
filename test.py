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


import requests
import json 
headers = {
"Content-Type": "application/json;charset=utf8"
}

data = {
    'version1' : r'G:\project\python\CC\testcase/151_a.java',
    'version2' : r'G:\project\python\CC\testcase/151_b.java',
    'conflict': r'G:\project\python\CC\testcase/151_merged.java',
    'base': r'G:\project\python\CC\testcase/151_base.java',
    'path': 'cc',
    'source': 'b1',
    'target': 'b2',
    'filetype': 'java',
}
r = requests.post('http://127.0.0.1:5000/predict', data=json.dumps(data), headers=headers)
state = json.loads(r.text)
print(state)

