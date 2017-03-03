# -*- coding:utf8 -*-
#这个文件主要用于当网站被屏蔽掉后的验证码识别操作

from PIL import Image
import pytesser.pytessers as pytesser
import requests
import main



VURL = "http://wenshu.court.gov.cn/Html_Pages/VisitRemind.html" #验证码登录界面url
PURL = "http://wenshu.court.gov.cn/User/ValidateCode" #获取验证码图片url
PICNAME = "vertify.jpg"

def pic_download(url=PURL,pic_name=PICNAME):
	#验证码图片下载
	pic = requests.get(url)
	if pic.status_code == 200:
	    open(pic_name, 'wb').write(pic.content)

def vertify_pic(pic_name=PICNAME):
	#验证码图片识别
	image = Image.open(pic_name)
	text = pytesser.image_to_string(image).strip()
	return text

def handle_error():
	url = "http://wenshu.court.gov.cn/Content/CheckVisitCode"
	spider = main.CaseSpider("","")
	spider.referer = "http://wenshu.court.gov.cn/Html_Pages/VisitRemind.html"
	pic_download(url=PURL,pic_name=PICNAME)
	text = vertify_pic(pic_name=PICNAME)
	formdata = {
		"ValidateCode": text
	}
	print ("The vertify code:",text)
	response = requests.post(url,headers=spider.headers,data=text)
	print ("1:success; 2:fialed,your code is:",response.text)
	if response.status_code==200:
		return 0
	return -1




if __name__ == '__main__':
	handle_error()
