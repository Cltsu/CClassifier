
from flask import Flask, request
from flask import jsonify
import os
import classify_utils

app = Flask(__name__)

from flask_cors import CORS, cross_origin
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content_Type'

@app.route("/predict", methods=['POST'])
@cross_origin()
def predict():
    conf_data = request.get_json()
    repo_path = conf_data['path']
    target = conf_data['target']
    source = conf_data['source']

    v1 = conf_data['version1']
    v2 = conf_data['version2']
    conf = conf_data['conflict']
    base = conf_data['base']

    filetype = conf_data['filetype']
    print('-' * 100)
    # print("receive:" + str(conf_data))
    conf_files = [v1, v2, conf, base]
    exists = [os.path.exists(file) for file in conf_files]
    if(not all(exists)):
        return {
            'code': 500,
            'msg': conf_files[exists.index(False)] + ' does not exist',
            'data': [],
        }
    
    project_name = os.path.basename(repo_path)
    model_path = os.path.join(os.getcwd(), 'model', project_name + '_' + filetype + ".joblib")
    labels = []
    ret = {}
    if(os.path.isfile(model_path)):
        print("use model : " + model_path)
        labels = classify_utils.predict(project_name, filetype, v1, v2, base, conf)
    else:
        if(filetype == 'java'):
            print("use defualt model for java")
            labels = classify_utils.predict('java', 'java', v1, v2, base, conf)
        elif(filetype == 'cpp'):
            print("use defualt model for cpp")
            labels = classify_utils.predict('cpp', 'cpp', v1, v2, base, conf)
        elif(filetype == 'kotlin'):
            print("use defualt model for kotlin")
            labels = classify_utils.predict('kotlin', 'kotlin', v1, v2, base, conf)
        else:
            return {
                'code': 500,
                'msg': '不支持文件类型' + filetype,
                'data': [],
            }
    ret['code'] = 200
    ret['msg'] = '预测成功'
    ret['data'] = labels
    print('-' * 100)
    print("return : " + str(ret))
    return jsonify(ret)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000)
