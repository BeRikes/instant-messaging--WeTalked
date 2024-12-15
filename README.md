# WeTalked

#### 介绍
软件工程实践课期末大作业——即时通讯小程序WeTalked

#### 参与贡献
毛子函(main contributor)、潘颂朗、孙涛、郑恺、陆宇扬

## 使用说明
### 环境配置
#### client客户端
python环境，python版本不要太老，项目搭建时的python版本是3.8.0\
无需下载其他包
#### server服务器
请终端运行以下命令\
`pip install pyodbc`\
`pip install bcrypt`
### client客户端使用
请终端运行\
`python client.py`\
运行时更改client.wtd文件，此文件中的内容为<serverIP-serverPort-networkBufferSize>，三个变量更改为正确内容，即可运行。

如果进行大流量通讯，请调大buffer_size参数
### server服务器使用
请终端运行`python server.py`，运行之前将ip地址改为本机ip或者远程服务器ip地址