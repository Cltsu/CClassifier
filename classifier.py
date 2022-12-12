from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
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


dataset = {}
with open('./abm.json', 'r', encoding='utf-8') as jfile:
    dataset = json.load(jfile)
dataset = dataset['conf']
dataset = sample_normal(dataset)
random.shuffle(dataset)

features = [
    'a_keyword_1',
    'b_keyword_1',
    'a_keyword_2',
    'b_keyword_2',
    'a_exist',
    'b_exist',
    'base_exist',
    'a_edit_type',
    'b_edit_type',
    'ab_edit_type',
]
train = [{key:value for (key, value) in data.items() if key in features} for data in dataset]
vec=DictVectorizer(sparse=False)
train = vec.fit_transform(train)
target = [data['label'] for data in dataset]


# train = [
#     [
#         data['a_keyword_1'],
#         data['b_keyword_1'],
#         data['a_keyword_2'],
#         data['b_keyword_2'],
#         data['a_exist'],
#         data['b_exist'],
#         data['base_exist'],
#         data['a_edit_type'],
#         data['b_edit_type'],
#         data['ab_edit_type'],
#     ] for data in dataset]
# target = [data['label'] for data in dataset]

x_train, x_test, y_train, y_test = train_test_split(train, target, test_size=0.2)

# clf = tree.DecisionTreeClassifier()
clf = RandomForestClassifier(max_depth=15, min_samples_split=5, random_state=0)
clf.fit(x_train, y_train)
print(accuracy_score(y_test, clf.predict(x_test)))