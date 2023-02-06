from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import sklearn.metrics as m
from sklearn.feature_extraction import DictVectorizer
import json
import random
import pandas as pd

def sample_normal(dataset):
    label_set = set([sample['label'] for sample in dataset])
    label_dict = {}
    for label in label_set:
        label_dict[label] = [sample for sample in dataset if sample['label'] == label]
    min_size = min([len(samples) for (label, samples) in label_dict.items()])
    for key in label_dict.keys():
        random.shuffle(label_dict[key])
    return [sample for samples in label_dict.values() for sample in samples[:min_size]]


def is_trivial(conf):
    tmp_str = conf['A'] + conf['B'] + conf['base']
    for i in range(len(tmp_str)):
        if tmp_str[i] != ' ' and tmp_str[i] != '\n':
            return False
    return True


def get_train_target(dataset):
    def select_label(data):
        if data['label'].startswith('rem'):
            data['label'] = 'comb'
        # if data['label'] != 'concat':
        #     data['label'] = 'new' 
        # if data['label'] == 'comb':
        #     data['label'] = 'new'
        # if data['label'] != 'A' and data['label'] != 'B':
        #     data['label'] = 'new'
        # if data['label'] == 'A' or data['label'] == 'B':
        #     data['label'] = 'AB'
        # if data['label'] == 'concat':
        #     data['label'] = 'new'
        pass
                                                                            
    features = [
        'a_kw',
        'a_fkw',
        'b_kw',
        'b_fkw',
        'a_exist',
        'b_exist',
        'base_exist',
        'a_token_sim',
        'b_token_sim',
        'a_edit_type',
        'b_edit_type',
        'ab_edit_type',
        'label',
        'a_region_size',
        'b_region_size',
        'base_region_size',
        'conf_chunk_size',
    ]
    feature_dataset = [{key:value for (key, value) in data.items() if key in features} for data in dataset]
    for sample in feature_dataset:
        sample['a_kw1'] = sample['a_kw'][0] if len(sample['a_kw']) > 0 else 'empty'
        sample['a_kw2'] = sample['a_kw'][1] if len(sample['a_kw']) > 1 else 'empty'
        sample['b_kw1'] = sample['b_kw'][0] if len(sample['b_kw']) > 0 else 'empty'
        sample['b_kw2'] = sample['b_kw'][1] if len(sample['b_kw']) > 1 else 'empty'
        sample.pop('a_kw')
        sample.pop('a_fkw')
        sample.pop('b_kw')
        sample.pop('b_fkw')
        select_label(sample)
    # feature_dataset = [data for data in feature_dataset if data['label'] != 'A' and data['label'] != 'B']
    # feature_dataset = [data for data in feature_dataset if data['label'] == 'A' or data['label'] == 'B']
    # feature_dataset = sample_normal(feature_dataset)
    target = [data['label'] for data in feature_dataset]
    train = [data for data in feature_dataset]
    for sample in train:
        sample.pop('label')
    vec=DictVectorizer(sparse=False)
    train = vec.fit_transform(train)
    return train, target


def error_predict_analysis(predict, target, label_set):
    if len(predict) != len(target):
        print('lens are not same')
        return
    count = {label:0 for label in label_set}
    for i in range(len(predict)):
        if target[i] != predict[i]:
            count[predict[i]] += 1
        else:
            count[target[i]] += 1
    print(count)
    print(count[target[0]] / len(target))

dataset = {}
with open('./c5_2.json', 'r', encoding='utf-8') as jfile:
    dataset = json.load(jfile)
dataset = dataset['conf']
dataset = [sample for sample in dataset if not is_trivial(sample)]

random.shuffle(dataset)
train, target = get_train_target(dataset)
x_train, x_test, y_train, y_test = train_test_split(train, target, test_size=0.1)

# clf = tree.DecisionTreeClassifier()
clf = RandomForestClassifier(max_depth=35, min_samples_split=5, random_state=0, class_weight='balanced')
clf.fit(x_train, y_train)

label_set = set([label for label in y_train])
labeled_test = {label:([],[]) for label in label_set}
for i in range(len(y_test)):
    labeled_test[y_test[i]][0].append(x_test[i])
    labeled_test[y_test[i]][1].append(y_test[i])

for label in label_set:
    print(label + ' : ' + str(len(labeled_test[label][0])))
    pred_label = clf.predict(labeled_test[label][0])
    target_label = labeled_test[label][1]
    error_predict_analysis(pred_label, target_label, label_set)

print('--------------------')
predicts = clf.predict(x_test)
precision = precision_score(y_test, predicts, average=None)
recall = recall_score(y_test, predicts, average=None)
f1 = f1_score(y_test, predicts, average=None)
print(sorted(list(label_set)))
print('precision:')
print(precision)
print('recall:')
print(recall)
print('f1:')
print(f1)
# print(accuracy_score(y_test, clf.predict(x_test)))