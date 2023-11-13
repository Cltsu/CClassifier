from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import sklearn.metrics as m
from sklearn.feature_extraction import DictVectorizer
import joblib
from sklearn.pipeline import Pipeline
import json
import random
import pandas as pd
import numpy as np
import csv
import os

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
    tmp_str = conf['a_contents'] + conf['b_contents'] + conf['base_contents']
    for i in range(len(tmp_str)):
        if tmp_str[i] != ' ' and tmp_str[i] != '\n':
            return False
    return True


def get_train_target(dataset):
    def select_label(data):
        if data['label'] == "CC12" or data['label'] == "CC21":
            data['label'] = 'CC'
                                                                            
    features = [
        'a_constructs',
        'b_constructs',
        'a_id_sim',
        'b_id_sim',
        'ab_id_sim',
        'a_line_sim',
        'b_line_sim',
        'ab_line_sim',
        'chunk_num',
        'label',
    ]
    feature_dataset = [{key:value for (key, value) in data.items() if key in features} for data in dataset]
    feature_dataset = [data for data in feature_dataset if 'label' in data.keys()]
    for sample in feature_dataset:
        sample['a_cons1'] = sample['a_constructs'][0] if len(sample['a_constructs']) > 0 else 'empty'
        sample['a_cons2'] = sample['a_constructs'][1] if len(sample['a_constructs']) > 1 else 'empty'
        sample['b_cons1'] = sample['b_constructs'][0] if len(sample['b_constructs']) > 0 else 'empty'
        sample['b_cons2'] = sample['b_constructs'][1] if len(sample['b_constructs']) > 1 else 'empty'
        sample.pop('a_constructs')
        sample.pop('b_constructs')
        select_label(sample)
    # feature_dataset = [data for data in feature_dataset if data['label'] != 'A' and data['label'] != 'B']
    # feature_dataset = [data for data in feature_dataset if data['label'] == 'A' or data['label'] == 'B']
    # feature_dataset = sample_normal(feature_dataset)
    target = [data['label'] for data in feature_dataset]
    train = [data for data in feature_dataset]
    for sample in train:
        sample.pop('label')
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


def evaluate_model(project_name, json_path, save_csv=False):
    dataset = {}
    with open(json_path, 'r', encoding='utf-8') as jfile:
        dataset = json.load(jfile)
    dataset = dataset['conf']
    dataset = [sample for sample in dataset if not is_trivial(sample)]

    random.shuffle(dataset)
    train, target = get_train_target(dataset)

    vec=DictVectorizer(sparse=False)
    train = vec.fit_transform(train)

    x_train, x_test, y_train, y_test = train_test_split(train, target, test_size=0.15)
    ## clf = RandomForestClassifier(max_depth=35, min_samples_split=5, random_state=0, class_weight='balanced')
    clf = RandomForestClassifier(max_depth=35, min_samples_split=2, random_state=0, class_weight='balanced', n_estimators=400, min_samples_leaf= 1)
    clf.fit(x_train, y_train)

    label_set = set([label for label in target])
    labeled_test = {label:([],[]) for label in label_set}
    for i in range(len(y_test)):
        labeled_test[y_test[i]][0].append(x_test[i])
        labeled_test[y_test[i]][1].append(y_test[i])
    
    for label in label_set:
        print(label + ' : ' + str(len(labeled_test[label][0])))
        if(labeled_test[label][0] == []):
            continue
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
    print('overall:')
    print('accuracy:')
    acc = accuracy_score(y_test, predicts)
    print(acc)
    print('precision:')
    pre = precision_score(y_test, predicts, average='weighted')
    print(pre)
    print('recall:')
    rec = recall_score(y_test, predicts, average='weighted')
    print(rec)
    print('f1:')
    f1_s = f1_score(y_test, predicts, average='weighted')
    print(f1_s)

    statistics = [np.append(precision, pre), np.append(recall, rec), np.append(f1, f1_s)]
    save_to_csv(statistics, project_name)

def save_to_csv(statistics, project_name):
    col = ['A', 'B', 'CB', 'CC', 'NC', 'overall']
    stat = pd.DataFrame(columns=col, data=statistics)

    all_info = None
    col = ['repo','A-precision', 'A-recall', 'A-f1', 'B-precision', 'B-recall', 'B-f1', 'CB-precision', 'CB-recall', 'CB-f1',
           'CC-precision', 'CC-recall', 'CC-f1','NC-precision', 'NC-recall', 'NC-f1', 'overall-precision', 'overall-recall', 'overall-f1']
    if os.path.exists('./statistics/repo.csv'):
        all_info = pd.read_csv('./statistics/repo.csv')
    else:
        all_info = pd.DataFrame(columns=col)
    cur_info = np.array([statistics[0], statistics[1], statistics[2]]).transpose().reshape(1, -1)
    cur_info = pd.DataFrame(columns=col[1:], data=cur_info)
    cur_info['repo'] = project_name
    print(cur_info)

    all_info = all_info.append(cur_info)
    all_info.to_csv('./statistics/' + 'repo.csv', index=False)

    stat.insert(0, '', ['precision', 'recall', 'f1-score'])
    stat.to_csv('./statistics/' + project_name + '.csv', index=False)
    


def train_model(project_name, json_path, file_type, save_model = True, save_path = ''):
    dataset = {}
    with open(json_path, 'r', encoding='utf-8') as jfile:
        dataset = json.load(jfile)
    dataset = dataset['conf']
    dataset = [sample for sample in dataset if not is_trivial(sample)]

    random.shuffle(dataset)
    train, target = get_train_target(dataset)

    vec=DictVectorizer(sparse=False)
    train = vec.fit_transform(train)

    clf = RandomForestClassifier(max_depth=35, min_samples_split=2, random_state=0, class_weight='balanced', n_estimators=400, min_samples_leaf= 1)
    clf.fit(train, target)

    if save_model:
        vec_clf = Pipeline([('vectorizer', vec), ('forest', clf)])
        if(project_name != ''):
            project_name += '_'
        joblib.dump(vec_clf, save_path + project_name  + file_type + '.joblib')
