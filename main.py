# -*- coding: utf-8 -*-
from time import sleep
import random
import json
from lxml import html
from collections import defaultdict
import requests
import urllib
import codeReco


FNAME = 'judgment.txt' #数据存放地址
PAGEINDEX = 'index.txt' #存放下一次应该访问的页码
def fwrite(f_name,data):
	#讲记录写入文件
	if data==None:return -1
	with open(f_name, 'a+') as fl:
		fl.write(json.dumps(data,ensure_ascii=False))
	return 0

def page_index(f_name,model,index=1):
	if model=='r':
		with open(f_name, 'r') as fl:
			line = fl.readline()
		return int(line.strip())
	elif model=='w':
		with open(f_name, 'w') as fl:
			line = fl.write(index)
	


class CaseSpider(object):
	"""
	案件爬虫类
	"""
	def __init__(self, atype, item, index=1, page_num=20, f_name=FNAME):
		super(CaseSpider, self).__init__()
		self.url = 'http://wenshu.court.gov.cn/List/ListContent'
		self.referer = "案件类型:{atype}".format(atype=atype)
		self.index = index	#页码
		self.page_num = page_num #每一页文书数量
		self.count = 0 #文书总条目数
		self.atype = atype
		self.item = item
		self.f_name = f_name
		self.referer = urllib.parse.quote("http://wenshu.court.gov.cn/List/List?sorttype=1&conditions=searchWord+1+AJLX++{referer}".format(referer=self.referer))
		self.headers = {
				'Host':"wenshu.court.gov.cn",
				'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
				'Accept':"*/*",
				'Accept-Language':"zh-CN,zh;q=0.8",
				'Accept-Encoding':"gzip, deflate",
				'Referer':self.referer,
				'Content-Type':"application/x-www-form-urlencoded; charset=UTF-8",
				'Connection':"keep-alive"
			}
		self.formdata = {
				'Param':'案件类型:{atype},关键词:{item}'.format(atype=self.atype,item=self.item),
				'index':self.index,
				'Page':self.page_num,
				'Order':'法院层级',
				'Direction':'asc',
			}
		self.page_num = 0
		
	def start_requests(self):
	    #获取文书总数
		try:
			# print("-----",self.headers,"++++",self.formdata)
			response = requests.post(self.url, headers=self.headers, data=self.formdata)
			# print (response)
			data = json.loads(json.loads(response.text))
			self.count = int(data[0]['Count'])
			return 0
		except Exception as e:
			print ('Error:count get failed!')
			print ('detail:',e)
			return -1



	def parse_item(self,doc_id):
		#获取文书正文
		try:
			url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID={id}'.format(id=doc_id)
			print ("success: ",url)
			response = requests.post(url)
			doc = html.document_fromstring(response.text)
			content = doc.xpath('//text()')
			content = "".join(content[1:len(content)-1])
			# print (content)
			return content,response.url
		except Exception as e:
			print ("Error:item parse failed!")
			print ("detail:",e)
			return "",""
	    

	def parse_page(self,index,page_num):
		#获取文书页面列表页面的基础信息
		try:
			self.index = page_num
			self.page_num = page_num
			response = requests.post(self.url, headers=self.headers,data=self.formdata)
			data = json.loads(json.loads(response.text))
			for i in range(1,len(data)):
			    item = defaultdict()
			    id = data[i]['文书ID']
			    case = data[i]
			    item['content'],item['url'] = self.parse_item(id)
			    item['title'] = case.get('案件名称')
			    item['date'] = case.get('裁判日期')
			    item['document_code'] = case.get('案号')
			    item['court'] = case.get('法院名称')
			    item['type'] = case.get('案件类型')
			    item['source_crawl'] = 'wenshu.court.gov.cn'
			    fwrite(self.f_name, item)
			    sleep(random.random())
		except Exception as e:
			print ("Error:page parse failed!")
			print ("detail:",e)
			return -1


def test_page_index():
	#测试函数
	page_index(PAGEINDEX,'w','5')
	index = page_index(PAGEINDEX,'r')
	print (index)	    

def run():
	#爬虫实现
	spider = CaseSpider("刑事案件", "交通事故")
	code = spider.start_requests()
	i = 0
	while code:
		codeReco.handle_error() #验证码提交
		code = spider.start_requests()
		i += 1 #失败次数记录
		print ("Error:get count failed, try the {0} times".format(i))
		sleep(random.randint(0,i)) #失败次数与期望等待时间成正比
	page_num = 20
	pages = spider.count//20
	index = page_index(PAGEINDEX,'r')
	print ("begin with :",index)
	while index<=pages:
		flag = spider.parse_page(index,page_num)
		if(flag==-1):
			codeReco.handle_error()
			sleep(10) #ip被封，暂停2分钟
		else:
			print ("page:"+str(index)+" finished!")
			page_index(PAGEINDEX,'w',str(index+1))
			sleep(random.random()) #随机休眠一段时间
			index += 1

if __name__ == '__main__':
	run()
