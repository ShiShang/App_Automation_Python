
#--*--coding=utf-8--*--
import os
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from email.Encoders import encode_base64  

'''

Util脚本，包含邮件发送以及邮件内容的处理。

'''


#指定一个错误报错处理，用于页面无法加载的情况。

class ErrorException(Exception):  
    pass  

#发送邮件设置

class Send_Email:

    def __init__(cls,file_path):
        cls.file_path=file_path
        cls.from_address="jenkinsrobot@sohu.com"                           #发件地址
        cls.to_address=["shifawu@tuniu.com",]                              #收件地址

    def new_file(cls):
        list=os.listdir(cls.file_path)
        list.sort(key=lambda fn:os.path.getmtime(cls.file_path+"\\"+fn))   #按时间排序
        cls.file_new1=os.path.join(cls.file_path,list[-1])                 #选取最新一个文件夹
    
    def send_mail(cls,contents=""):

        #附件Logging文件

        list=os.listdir(cls.file_path)
        list.sort(key=lambda fn:os.path.getmtime(cls.file_path+"\\"+fn))
        for i in range(len(list)):
            if list[i].endswith("log"):
                log_name=list[i]
            if list[i].endswith("jpg"):
                jpg_name=list[i]
        cls.file_log=os.path.join(cls.file_path,log_name)                  #获取log地址
        cls.jpg_name=os.path.join(cls.file_path,jpg_name)                  #获取截图地址
        #log_path1=os.path.join(cls.file_path,cls.file_log)

        for i in range(len(list)):
            if "report" in list[i]:
                report_name=list[i]
        cls.file_new=os.path.join(cls.file_path,report_name)               #获取report地址

        with open(cls.file_new,"rb") as f:
            mail_body=f.read()
        msg=MIMEMultipart() 
        msg['Subject']=u"APP端UI主流程自动化测试报告"                      #邮件标题
        msg['From'] =cls.from_address                                      #发件地址
        msg['To'] = ','.join(cls.to_address)                               #收件地址
       
        with open(cls.file_log,'rb') as f:                                 #添加日志附件
            log_body=f.read()
        att1=MIMEText(log_body,"base64","")
        att1["Content-Disposition"] = 'attachment; filename="Logging.log"' #日志名称

        with open(cls.jpg_name,'rb') as f:                                 #添加图片附件
            pic_body=f.read() 
        att2=MIMEText(pic_body,"base64","")                                #图片名称
        att2["Content-Disposition"] = 'attachment; filename="Error-Screenshot.jpg"'

        msg.attach(att2)
        msg.attach(att1)
        if not contents:
            contents=mail_body
            msg.attach(MIMEText(contents,"html","gbk"))
        else:
            msg.attach(MIMEText(contents,"html","gbk"))

        smtp=smtplib.SMTP()
        smtp.connect('smtp.sohu.com')
        smtp.login(cls.from_address,"shi@123456")
        smtp.sendmail(cls.from_address,cls.to_address,msg.as_string())
        smtp.quit()

#生成简化邮件模板内容

class EmailContent:

    def __init__(self):

		#为了显示TC中文，先写一个DICT

        self.DICT={
        "LogIn":u"登陆",
        "ShouYe_Number_Display": u"首页_数字显示", 
        "ShouYe_Link_Switch":u"首页_链接跳转",
        "DingQiLiCai":u"定期理财页面",
        "NiuBianXian":u"牛变现页面",
        "WoDe_Number_Display":u"我的页面_数字显示",
        "LogOut":u"登出",
        "WoDe_Link_Switch":u"我的页面_链接跳转",
        "TuNiuBao_Order":u"途牛宝下单",
		"JiJinLiCai":u"基金理财",
        "NiuBianXian_Order":u"牛变现下单",
        "JiJinLiCai_Order":u"基金理财下单",
        "DingQiLiCai_Order":u"定期理财下单",
         }

    #获取passcase内容文档

    def getLoadPassResults(self, pass_test_cases):
    	
    	load_pass_results=""   
        for i in pass_test_cases:
            load_pass_results=load_pass_results+"""<tr><td colspan='2'><font face='微软雅黑'> %s </font></td>
                                               <td colspan='2'><b><font face='微软雅黑'><span style='color:green'> Pass </span></font></b></td></tr>
                                            """ % self.DICT[i]
        return load_pass_results

    #获取failedcase内容文档

    def getLoadFailedResults(self, failed_test_cases):
    	
    	load_failed_results=""
        for i in failed_test_cases:
            load_failed_results=load_failed_results+"""<tr><td colspan='2'><font face='微软雅黑'> %s </font></td>
                                               <td colspan='2'><b><font face='微软雅黑'><span style='color:red'> Failed </span></font></b></td></tr>
                                            """ % self.DICT[i]
        return load_failed_results
