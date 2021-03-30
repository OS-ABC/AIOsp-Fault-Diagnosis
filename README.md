# AIOsp-Fault-Diagnosis

### 介绍

>辅助运维人员进行微服务系统故障诊断及修复，故障根因诊断粒度为诊断到指标或日志，修复方案通过已有的图谱生成，项目实现为flask接口

### Install
```
pip install -r requirements.txt
```
```
1、安装MYSQL数据库
2、运行config/data_base_sql创建项目所需数据库
```

#### Note

- python_version = 3.7.9
- Mysql 数据库存储故障根因诊断结果和修复方案
- 若不考虑存储部分，可注释掉所有和SaveResult相关代码
- 使用项目中的数据库存储时注意在```dao```文件夹下的账号密码

### demo

- 数据下载地址
```
链接:https://pan.baidu.com/s/1bMwuqRpJ1hMhKPhxajp4kw  密码:ptmj
```
### demoRun

数据放入```data```文件夹
- hadoop数据：```run demo/hadoop_data_test.py```完成故障根因诊断并存储
- aiops数据：```run demo/aiops_2020_data_test.py```完成故障根因诊断并存储

### WEB接口启动
```
run app.py
```
### 生成修复方案
```
run generate_solutuons_service.py的time_generate_logs_solutions()
```
#### Note

- 未配置neo4j数据库和mysql数据库，该功能不可用

### 目录结构
    ├── fault_diagnosis_and_repair
        └── bean
            ├── input_model.py  //输入数据对应对象类
            ├── output_model.py //web接口输出对象类
            └── save_model.py  //与mysql数据库表对应类
        ├── config
            ├── data_base_sql  //mysql数据库创建SQL
            └── stop.txt  //停用词
        ├── dao
            ├── db_dao.py //mysql对应dao
            ├── es_dao.py //es对应dao
            └── neo4j_dao.py  //neo4j对应dao
        ├── data
            ├── aiops_data_2020 //存放demo数据
            └── hadoop_data.py  //存放demo数据
        ├── demo
            ├── aiops_2020_data_test.py //aiops数据故障根因诊断并存储入口
            └── hadoop_data_test.py  //hadoop数据故障根因诊断并存储入口
        ├── service //项目核心代码
            ├── module_tools  //功能实现封装的各个模块工具类
                ├── diagnosis_faultservice.py  //故障服务进一步诊断工具类
                ├── generate_solutions.py  //修复方案生成工具类
                ├── identify_faulrservice.py  //故障服务识别工具类
                ├── input_data.py  //输入数据处理工具类
                └── save_result.py  //数据存储工具类
            ├── fault_diagnosis_service  //故障根因诊断服务入口
            ├── generate_solutions_service  //修复方案生成服务入口
            └── web_service  //交互模块查询服务入口
        ├── utils
            ├── data_tools.py  
            ├── graph.py  
            ├── jaccard_api.py 
            ├── pageRank.py 
            ├── pcalg.py 
            └── prcess_aiops2020_data_original.py //可将aiops 2020数据处理为本项目所需的数据，作为aiops_2020_data_test.py数据源
        ├── app.py //flask接口启动
        └── requirements.txt 
### 输入数据格式
项目所需数据包括原始指标数据、原始日志数据、系统部署数据、调用数据、异常检测模块检测出的异常指标数据和异常日志数据下面分别对所需数据格式介绍

- 原始指标数据

字段  | 说明 | 类型|
---- | ----- | ------
timestamp|采集时间(s)|秒级时间戳string
metricId|指标唯一标识|string
metricName|指标名称|string
value|指标采集值|float
units|单位|string
metricBelongTo| 指标所属|string
metricBelongLevel|指标所属层级|host/container/service

timestamp  | metricId | metricName| value | units | metricBelongTo | metricBelongLevel
 ---- | ----- | ------  | ------ | ------ | ------ | ------ 
 '1614688922'  | '29162' | 'CPU iowait time'| 0.717773 | '%'| 'fuguangbo-0002'| 'host'
 
 - 原始日志数据
 
 字段  | 说明 | 类型|
---- | ----- | ------
timestamp|采集时间(s)|秒级时间戳string
logId|日志唯一标识|string
logMessage|日志条目信息|string
logLevel|日志等级|string
logBelongTo|日志所属|string
logBelongLevel| 日志所属层级|host/container/service

timestamp  | logId | logMessage| logLevel | logBelongTo | logBelongLevel
 ---- | ----- | ------  | ------ | ------ | ------ 
 1614688885  | 'hadoop-root-datanode-hadoop-slave2.log' | org.apache.hadoop.hdfs.server... | INFO | 'DataNode'| 'service'
 
 - 部署数据
 
 字段  | 说明 | 类型|
---- | ----- | ------
serviceInstanceId|服务实例唯一标识|string
serviceName|服务名称|string
hostId|主机唯一标识|string
hostName|主机名称|string
containerId|容器唯一标识|string
containerName|容器名称|string

serviceInstanceId  | serviceName | hostId| hostName | containerId | containerName
 ---- | ----- | ------  | ------ | ------ | ------ 
 'NameNode'  | 'NameNode' | 'hadoop-master'| 'hadoop-master' | 'fuguangbo-0002'| 'fuguangbo-0002'

- 调用链数据
 
 字段  | 说明 | 类型|
---- | ----- | ------
id|当前调用SpanId|string
pid|父调用SpanId|string
serviceId|服务实例唯一标识|string
serviceName|服务名称|string
serviceType|服务类别|string
startTime|调用开始时间|string
traceId|调用链唯一标识|string

id  | pid | serviceId| serviceName | serviceType | startTime| traceId
 ---- | ----- | ------  | ------ | ------ | ------ | ------ 
 '136.60.16146924705200712'  | -1 | ''DataNode'| 'DataNode' | 'Local'| '1614692470520'|'136.60.16146924705200713'

- 异常指标数据
 
 字段  | 说明 | 类型|
---- | ----- | ------
startTime|异常开始时间|string
endTime|异常结束时间|string
metricId|指标唯一标识|string
metricName|指标名称|string
value|指标值|float
units|单位|string
metricBelongTo|指标所属|string
metricBelongLevel|指标所属层级|host/container/service

startTime | endTime | metricId| metricName | value | units| metricBelongTo|metricBelongLevel
 ---- | ----- | ------  | ------ | ------ | ------ | ------ | ------ 
'2021-03-02 21:31:02'|'2021-03-02 21:31:02' | '29162'| 'CPU iowait time' | '0.912974| 'fuguangbo-0002'|'host'

- 异常日志数据
 
 字段  | 说明 | 类型|
---- | ----- | ------
startTime|异常开始时间|string
endTime|异常结束时间|string
logId|日志唯一标识|string
logExceptionSegment|日志异常片段|string
logBelongTo|日志所属|float
logBelongLevel|日志所属层级|host/container/service

startTime | endTime | logId| logExceptionSegment | logBelongTo | logBelongLevel
 ---- | ----- | ------  | ------ | ------ | ------ 
'2021-03-02T13:15:51.452Z'|'2021-03-02T13:15:51.452Z' |'hadoop-root-datanode-hadoop-slave2.log'| java.net.NoRouteToHostException...| 'DataNode'|'service'

### 运行效果
- 故障根因诊断运行效果分两个部分：打印结果和存储结果
故障根因诊断打印结果：

![截图](https://github.com/yymgithub/AIOsp-Fault-Diagnosis/tree/main/effect_images/1.png?raw=true)

>故障服务列表是在多个异常服务中识别出的故障服务列表，key为服务Id <br>
>XXX服务故障根因列表是该故障服务的根因指标、日志列表，key为指标或日志名称
具体存储结果可依据数据库SQl查看
- web接口返回值为Json
- 修复方案生成直接生成修复方案存储到mysql