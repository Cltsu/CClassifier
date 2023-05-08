### 配置环境
envirment.yml包含了本模块的完整依赖，在当前目录下使用命令创建anaconda环境并启动
```
conda env create -f environment.yml
conda activate merge
```
使用flask run命令启动web服务。
```
flask run
```

### 模型
当前只有一个测试用模型，models文件下的java.rar文件，解压为java.joblib即可