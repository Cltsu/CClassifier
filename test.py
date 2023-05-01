import classify_utils
import dataset_utils
import train_utils
# dataset_utils.conflict_process_pipeline( 'G:\mergebot\output\conflictFiles\platform_external_protobuf\\', 'platform_external_protobuf','cpp', 'G:\\mergebot\\')

# train_utils.train_model("", r"G:\mergebot\datasets\platform_external_protobuf.json")
# train_utils.train_model("", r"G:\mergebot\datasets\tachiyomi.json")
print(classify_utils.predict('hibernate-orm', 'java', './web_service/testcase/a.java',
     './web_service/testcase/b.java',
     './web_service/testcase/base.java',
     './web_service/testcase/merged.java'))
