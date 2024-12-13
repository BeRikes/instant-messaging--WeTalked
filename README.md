# WeTalked

#### 介绍
软件工程实践课期末大作业——即时通讯小程序WeTalked

#### 参与贡献
毛子函、潘颂朗、孙涛、郑恺、陆宇扬

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
`python client.py --ip <> --port <>`\
<>部分需要填入服务器的ip地址和服务进程端口号\

如果进行大流量通讯，请运行`python client.py --ip <> --port <> --buffer_size <>`buffer_size参数指定为比1024大
### server服务器使用
请终端运行`python server.py`，运行之前将ip地址改为本机ip或者远程服务器ip地址