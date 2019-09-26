# aliyun-support-tools
##脚本使用说明
### 命令执行参数
* --domain : 域名，只支持单个查询。
* --start : 获取日志开始时间
* --end : 获取日志结束时间
* --access : Aliyun账号的Access Key
* --secure : Aliyun账号的secure key
### 注意事项
此脚本最多支持1000个日志文件的拉取，及开始时间与结束时间之间不要超过40天，超过40天会有日志遗漏。
### 脚本的执行逻辑
####1.通过Aliyun的API接口DescribeCdnDomainLogs获取指定域名的原始访问日志的下载地址，返回格式如下：
```
{
	"DomainLogModel":{
		"PageNumber":1,
		"TotalCount":3,
		"PageSize":100,
		"DomainLogDetails":{
			"DomainLogDetail":[
				{
					"LogName":"gc.ggter.com_2015_05_23_1100_1200.gz",
					"LogPath":"cdnlog.cn-hangzhou.oss.aliyun-inc.com/gc.xxx.com/2015_05_23/gc.ggter.com_2015_05_23_1100_1200.gz?OSSAccessKeyId=3xmgf7JheOfOTUTf&Expires=1432539994&Signature=7Ly4ccKN3afzAGYyWDbxBcOcnxxxx",
					"EndTime":"2015-05-23T04:00:00Z",
					"StartTime":"2015-05-23T03:00:00Z",
					"LogSize":257
				},
				{
					"LogName":"gc.ggter.com_2015_05_23_1500_1600.gz",
					"LogPath":"cdnlog.cn-hangzhou.oss.aliyun-inc.com/gc.xxx.com/2015_05_23/gc.ggter.com_2015_05_23_1500_1600.gz?OSSAccessKeyId=3xmgf7JheOfOxxxx&Expires=1432539994&Signature=dMv7VqPqZHXVbKPmorGIvylC6xxxx",
					"EndTime":"2015-05-23T08:00:00Z",
					"StartTime":"2015-05-23T07:00:00Z",
					"LogSize":194
				},
				{
					"LogName":"gc.ggter.com_2015_05_23_2100_2200.gz",
					"LogPath":"cdnlog.cn-hangzhou.oss.aliyun-inc.com/gc.ggter.com/2015_05_23/gc.ggter.com_2015_05_23_2100_2200.gz?OSSAccessKeyId=3xmgf7JheOfOxxxx&Expires=1432539994&Signature=FpSQCbgNcxCBYIxKVoKC8mGxxxx",
					"EndTime":"2015-05-23T14:00:00Z",
					"StartTime":"2015-05-23T13:00:00Z",
					"LogSize":258
				}
			]
		},
		"DomainName":"example.com"
	},
	"RequestId":"1805F349-0A2B-41D9-B4AD-33632AFC27F1"
}
```
####2.可以通过直接访问logpath获取压缩文件路径，因此第二部分是将所有logpath传入cdn_pathfile_{timestamp}.log文件中
####3.将所有文件下载到指定目录下
####4.将所有文件解压并汇总到cdn_merge_{timestamp}.log中
