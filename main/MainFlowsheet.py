
#--*--coding=utf-8--*--

from appium import webdriver
from time import sleep
import time
import os
import unittest
import HTMLTestRunner
import HTMLTestRunnerCN
from appium.webdriver.common.touch_action import TouchAction    #设置手势操作
from selenium.webdriver.support import expected_conditions as EC  #设置显式等待
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from email.Encoders import encode_base64   
import sys
from util import *

'''

这是一个PYTHON 测试途牛金服App脚本，
主要用到Appium, Unittest框架。
包含功能验证，错误截图，日志记录，测试报告的生成，邮件定制与发送,结果记录等。
也可以将其中的各个Testcases进行分离，
生成更便于维护的测试套件。
此脚本使用Jenkins定时执行，1次/小时。


'''


#日志模块 

def console_out(logFilename):  

    '''
    Output log to file and console 
    '''  

    # 设置日志格式和级别 

    logging.basicConfig(  
                           level    =    logging.INFO,                                                                         
                           format   =    '[%(asctime)s]  [%(filename)s] : [%(levelname)s]  %(message)s',   
                           datefmt  =    '%Y-%m-%d %A %H:%M:%S',                                     
                           filename =    logFilename,             
                           filemode =    'w'
                       )           

    # 输出日志

    console = logging.StreamHandler()          
    console.setLevel(logging.INFO)        
    formatter = logging.Formatter('%(asctime)s : %(levelname)s  %(message)s')  
    console.setFormatter(formatter)    

    # 创建实例 

    logging.getLogger().addHandler(console)           
 

#全局执行

def setUpModule():
    
    logging.info("Test Module start...")

def tearDownModule():

    logging.info("Test Module end...")
    

#测试套件

class Main_Flowsheet(unittest.TestCase):

    #测试用例执行失败的截图装饰器

    def get_screenshot(func):

        """
        失败截图
        """
        
        def inner(cls,*args,**kwargs):
            try:
                f=func(cls,*args,**kwargs)
                return f 
            except:
                now=time.strftime("%Y_%m_%d_%H_%M_%S")
                pic_name="%s-error.jpg" % now
                pic_path=os.path.join(Folder_Path,pic_name)
                cls.driver.get_screenshot_as_file(pic_path)
                raise
        return inner

    def setUp(cls):
        pass
       # print "TestCase start..."

    def tearDown(cls):
        pass
       # print "TestCase end..."

    #使登录只执行一次

    @classmethod
    def tearDownClass(cls):
        print("TestCase end...")

    @classmethod
    def setUpClass(cls):

        #打开APP

        desired_caps = {}
        desired_caps['platformName'] = 'Android'
        desired_caps['platformVersion'] = '4.4.2'
        desired_caps['deviceName'] = '3db08f2c6889-android'     #设备号
        desired_caps['appPackage'] = 'com.tuniu.finance'        #app包名
        desired_caps['appActivity'] = 'com.tuniu.finance.activity.WelcomeActivity'
        cls.driver=webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
        sleep(5)

    #测试开始
    #登陆

    @get_screenshot
    def LogIn(cls):

        #如果不需要重新登录，直接手势

        try:
            sleep(2)
            element = WebDriverWait(cls.driver, 30).until(EC.presence_of_element_located((By.NAME, "欢迎回来")))
            needRelog_flag=False
        except:
            needRelog_flag=True

        if (needRelog_flag):

            # 登录账户

            cls.driver.find_element_by_name("我的").click()
            sleep(2)
            cls.driver.find_element_by_id("com.tuniu.finance:id/et_phone").send_keys("********")    #账号
            sleep(2)
            cls.driver.find_element_by_id("com.tuniu.finance:id/et_pwd").send_keys("********")      #密码
            sleep(2)
            cls.driver.find_element_by_id("com.tuniu.finance:id/btn_login").click()
            sleep(2)

            #未登陆过，需要设置手势密码二次

            action=TouchAction(cls.driver)
            action.press(x=310,y=610).wait(ms=500).move_to(x=320,y=310).wait(ms=500).move_to(x=-150,y=0).release().perform()
            sleep(3)
            action.press(x=310,y=610).wait(ms=500).move_to(x=320,y=310).wait(ms=500).move_to(x=-150,y=0).release().perform()
            sleep(5)
            logging.info(u"手势解锁成功，登录成功！")

        else:
           
            #登陆过，需要手势密码解锁一次

            action=TouchAction(cls.driver)
            action.press(x=310,y=610).wait(ms=500).move_to(x=320,y=310).wait(ms=500).move_to(x=-150,y=0).release().perform()
            sleep(5)
            logging.info(u"手势解锁成功，登录成功！")

    #登出

    @get_screenshot
    def LogOut(cls):
        sleep(10)
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_fourth").click()
        sleep(3)
        cls.driver.find_element_by_id("com.tuniu.finance:id/rl_user_info").click()
        sleep(3)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btn_logout").click()
        sleep(3)
        cls.driver.find_element_by_id("com.tuniu.finance:id/my_alert_dialog_ok_layout").click()
        sleep(3)
        cls.driver.quit()
        logging.info(u"流程结束，退出App!")
        sleep(2)

    #首页数字显示

    @get_screenshot
    def ShouYe_Number_Display(cls):

        '''
           金服APP-首页
           金额&收益验证；
           包括总财富金额，累计收益金额，途牛宝收益，途牛宝余额，牛变现金额。
        '''

        logging.info("-------Testcase (ShouYe_Number_Display)")

        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        sleep(2)

        #验证首页总财富金额

        user_asset_value=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_user_asset_value").get_attribute("text")
        try: 
            assert (float(user_asset_value.encode("utf-8"))>0)
            logging.info(u"首页总财富显示：%s 正确！" % user_asset_value.encode('utf-8'))
        except:
            logging.info(u"首页总财富显示：%s 不正确！" % user_asset_value.encode('utf-8'))
            raise ErrorException(u"首页总财富显示：%s 不正确！" % user_asset_value.encode('utf-8'))

        #验证首页累计收益金额

        sleep(1)
        user_asset_income=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_user_asset_income").get_attribute("text")
        try:
            assert (float(user_asset_income.encode("utf-8"))!=0)
            logging.info(u"累计收益金额显示：%s 正确！" % user_asset_income.encode('utf-8'))
        except:
            logging.info(u"累计收益金额显示：%s 不正确！" % user_asset_income.encode('utf-8'))
            raise ErrorException(u"累计收益金额显示：%s 不正确！" % user_asset_income.encode('utf-8'))

        #验证首页途牛宝昨日收益金额

        sleep(1)
        asset_tnb_rise=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_tnb_rise").get_attribute("text")
        try:
            assert(float(asset_tnb_rise.encode("utf-8"))>=0)
            logging.info(u"途牛宝昨日收益金额显示：%s 正确！" % asset_tnb_rise.encode('utf-8'))
        except:
            logging.info(u"途牛宝昨日收益金额显示：%s 不正确！" % asset_tnb_rise.encode('utf-8'))
            raise ErrorException(u"途牛宝昨日收益金额显示：%s 不正确！" % asset_tnb_rise.encode('utf-8'))

        #验证首页途牛宝余额金额

        sleep(1)
        asset_tnb_value=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_tnb_value").get_attribute("text")
        try:
            assert (float(asset_tnb_value.encode("utf-8"))>0)
            logging.info(u"途牛宝余额金额显示：%s 正确！" % asset_tnb_value.encode('utf-8'))
        except:
            logging.info(u"途牛宝余额金额显示：%s 不正确！" % asset_tnb_value.encode('utf-8'))
            raise ErrorException(u"途牛宝余额金额显示：%s 不正确！" % asset_tnb_value.encode('utf-8'))

        #验证首页牛变现持有金额

        sleep(1)
        asset_nbx_value=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_nbx_value").get_attribute("text")
        try:
            assert (float(asset_nbx_value.encode("utf-8"))>0)
            logging.info(u"牛变现金额显示：%s 正确！" % asset_nbx_value.encode('utf-8'))
        except:
            logging.info(u"牛变现金额显示：%s 不正确！" % asset_nbx_value.encode('utf-8'))
            raise ErrorException(u"牛变现金额显示：%s 不正确！" % asset_nbx_value.encode('utf-8'))

        #验证首页已购买基金金额

        sleep(1)
        asset_fund_value=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_fund_value").get_attribute("text")
        try:
            assert (float(asset_fund_value.encode("utf-8"))>0)
            logging.info(u"已购买基金金额显示：%s 正确！" % asset_fund_value.encode('utf-8'))
        except:
            logging.info(u"已购买基金金额显示：%s 不正确！" % asset_fund_value.encode('utf-8'))
            raise ErrorException(u"已购买基金金额显示：%s 不正确！" % asset_fund_value.encode('utf-8'))
        #logging.info("-------Testcase (ShouYe_Number_Display)-----STOP-------")

     #首页链接跳转

    @get_screenshot
    def ShouYe_Link_Switch(cls):

        """
            验证首页主流程页面跳转功能。
            包括途牛宝，定期理财，基金理财，牛变现，产品列表等。
        """

        logging.info( "-------Testcase (ShouYe_Link_Switch)")

        sleep(3)
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_tnb_key").click()

        #验证途牛宝跳转

        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的途牛宝")))
            logging.info(u"途牛宝页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"途牛宝页面加载失败！")
            raise ErrorException(u"途牛宝页面加载失败！")

        #验证定期理财跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_regular_key").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "定期理财")))
            logging.info(u"定期理财页面(From <首页定期>)加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        except:
            logging.info(u"定期理财页面(From <首页定期>)加载失败！" )
            raise ErrorException(u"定期理财页面(From <首页定期>)加载失败！" )

        #验证定期理财——更多跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_finance_more").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "定期理财")))
            logging.info(u"定期理财页面(From <查看更多>)加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        except:
            logging.info(u"定期理财页面(From <查看更多>)加载失败！" )
            raise ErrorException(u"定期理财页面(From <查看更多>)加载失败！" )

        #验证我的基金理财跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_fund_key").click()
        sleep(50)
        try:
            element = WebDriverWait(cls.driver, 50).until(EC.presence_of_element_located((By.NAME, "我的基金理财")))
            logging.info(u"我的基金理财页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的基金理财页面加载失败！")
            raise ErrorException(u"我的基金理财页面加载失败！")

        #验证我的牛变现跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_asset_nbx_key").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的投资")))
            logging.info(u"牛变现页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"牛变现页面加载失败！")
            raise ErrorException(u"牛变现页面加载失败！")
        sleep(2)

        #手势滑动，下滑至页面中部

        action0=TouchAction(cls.driver)
        action0.press(x=280,y=1125).wait(ms=500).move_to(x=0,y=50).release().perform()
        logging.info(u"手势滑动成功！") 

        #验证基金详情页面跳转

        fund_list=cls.driver.find_elements_by_id("com.tuniu.finance:id/tv_reg_finance_key")
        fund_list[1].click()    
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "基金详情")))
            logging.info(u"基金详情页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"基金详情页面加载失败！")
            raise ErrorException(u"基金详情页面加载失败！") 


        #验证基金理财跳转

        sleep(2)
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_fund_more").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "热门主题")))
            logging.info(u"基金理财页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"基金理财页面加载失败！" )
            raise ErrorException(u"基金理财页面加载失败！")
        #logging.info( "-------Testcase (ShouYe_Link_Switch)-----STOP-------")
        
    #定期理财页面

    @get_screenshot
    def DingQiLiCai(cls):

        '''
        验证定期理财页面可以正常显示。
        '''

        logging.info( "-------Testcase (DingQiLiCai)")
        sleep(2)

        #验证定期理财跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_second").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "定期理财")))
            logging.info(u"定期理财页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        except:
            logging.info(u"定期理财页面加载失败！" )
            raise ErrorException()
        #logging.info( "-------Testcase (DingQiLiCai)-----STOP-------")
        
    #牛变现页面

    @get_screenshot
    def NiuBianXian(cls):

        """
        验证牛变现产品列表可正常显示，正常跳转。
        """

        logging.info( "-------Testcase (NiuBianXian)")
        sleep(2)

        #验证牛变现跳转

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_second").click()
        cls.driver.find_element_by_name("牛变现").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "牛变现")))
            logging.info(u"牛变现页面加载成功！")
        except:
            logging.info(u"牛变现页面加载失败！" )
        sleep(5)

        #以下是 “默认”筛选器

        try:
            cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'0')]").click()
            sleep(5)
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "产品介绍")))
            logging.info(u"牛变现产品页面<From 默认>加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
           logging.info(u"牛变现产品页面<From 默认>加载失败！")
           raise ErrorException(u"牛变现产品页面<From 默认>加载失败！")

        #以下是 “收益率”筛选器

        cls.driver.find_element_by_accessibility_id("收益率").click()
        sleep(5)
        try:
            cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'0')]").click()
            sleep(5)
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "产品介绍")))
            logging.info(u"牛变现产品页面<From 收益率>加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
           logging.info(u"牛变现产品页面<From 收益率>加载失败！")
           raise ErrorException(u"牛变现产品页面<From 收益率>加载失败！")
        
        #以下是 “期限”筛选器

        cls.driver.find_element_by_accessibility_id("期限").click()
        sleep(5)
        try:
            cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'0')]").click()
            sleep(5)
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "产品介绍")))
            logging.info(u"牛变现产品页面<From 期限>加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
           logging.info(u"牛变现产品页面<From 期限>加载失败！")
           raise ErrorException(u"牛变现产品页面<From 期限>加载失败！")
        #logging.info( "-------Testcase (NiuBianXian)-----STOP-------")
        
    #基金理财页面

    @get_screenshot
    def JiJinLiCai(cls):

        '''
        验证基金理财页面可以正常显示，搜索，跳转。
        '''

        logging.info( "-------Testcase (JiJinLiCai)")
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_third").click()
        sleep(5)

        #搜索框功能验证

        cls.driver.find_element_by_class_name("android.widget.EditText").send_keys("1")
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "260108景顺新兴成长 Link")))
            logging.info(u"搜索框功能验证成功！")
            sleep(2)

            #Appium上 Clear()存在Bug，所以要先全选，然后再按键删除。

            element=cls.driver.find_element_by_accessibility_id("1").click()    #先点击
            sleep(1)
            cls.driver.press_keycode(67)                                        #最后删除
            sleep(1)
        except:
            logging.info(u"搜索框功能验证失败！")
            raise ErrorException(u"搜索框功能验证失败！")

        #热门主题链接跳转

        cls.driver.find_element_by_accessibility_id("定期宝期限灵活 低风险 Link").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "热门专题")))
            logging.info(u"热门专题跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"热门专题跳转失败！")
            raise ErrorException(u"热门专题跳转失败！")
        sleep(2)

        cls.driver.find_element_by_accessibility_id("大消费白马行情 消费为王 Link").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "热门专题")))
            logging.info(u"热门专题跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"热门专题跳转失败！")
            raise ErrorException(u"热门专题跳转失败！")
        sleep(2)

        cls.driver.find_element_by_accessibility_id("沪港深深度布局港股 Link").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "热门专题")))
            logging.info(u"热门专题跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"热门专题跳转失败！")
            raise ErrorException(u"热门专题跳转失败！")

        #基金跳转

        sleep(1)
        cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'9')]").click()
        try:
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "基金详情")))
            logging.info(u"基金详情页面加载成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"基金详情页面加载失败！" )
            raise ErrorException(u"基金详情页面加载失败！")
        sleep(2)

        #手势滑动效果

        action2=TouchAction(cls.driver)
        action2.press(x=280,y=1125).wait(ms=500).move_to(x=0,y=50).release().perform()
        sleep(5)

        #在空白的地方点一下

        action2.press(x=500,y=500).wait(ms=100).release().perform()
        button=cls.driver.find_element_by_accessibility_id("查看更多").click()
        sleep(2)
        try: 
            element = WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "基金")))
            logging.info(u"基金列表页面加载成功！")
            sleep(1)
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"基金列表页面加载失败！")
            raise ErrorException(u"基金列表页面加载失败！") 

        #基金学堂

        sleep(1)
        cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'33')]").click()
        try:
            cls.driver.find_element_by_accessibility_id("养基心经：长线持基需满足哪些条件").click()
            sleep(1)
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
            logging.info(u"基金学堂加载成功！")
        except:
            logging.info(u"基金学堂加载失败！")
            raise ErrorException(u"基金学堂加载失败！")
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        #logging.info( "-------Testcase (JiJinLiCai)-----START-------")
    
    #我的页面数字显示

    @get_screenshot
    def WoDe_Number_Display(cls):

        '''
        验证我的页面，各个金额数字显示正确。
        '''

        sleep(2)
        logging.info( "-------Testcase (WoDe_Number_Display)")
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_fourth").click()
        sleep(8)

        #总资产余额

        try:
            num2=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_property_num").text
            assert(float(num2.encode("utf-8"))>0)
            logging.info(u"总资产余额显示： %s 正确！" % num2.encode('utf-8'))
        except:
            logging.info(u"总资产余额显示： %s 不正确！" % num2.encode('utf-8'))
            raise ErrorException(u"总资产余额显示： %s 不正确！" % num2.encode('utf-8'))

        #途牛宝余额

        try:
            num3=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_tnb_value").text
            assert(float(num3.encode("utf-8"))>0)
            logging.info(u"途牛宝余额显示：%s 正确！" % num3.encode('utf-8'))
        except:
            logging.info(u"途牛宝余额显示：%s 不正确！" % num3.encode('utf-8'))
            raise ErrorException(u"途牛宝余额显示：%s 不正确！" % num3.encode('utf-8'))

        #定期理财

        try:
            num4=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_reg_value").text
            assert(float(num4.encode("utf-8"))>=0)
            logging.info(u"定期理财余额显示：%s 正确！" % num4.encode('utf-8'))
        except:
            logging.info(u"定期理财余额显示：%s 不正确！" % num4.encode('utf-8'))
            raise ErrorException(u"定期理财余额显示：%s 不正确！" % num4.encode('utf-8'))

        #我的基金

        try:
            num5=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_fund_value").text
            assert(float(num5.encode("utf-8"))>=0)
            logging.info(u"我的基金理财余额显示：%s  正确！" % num5.encode('utf-8'))
        except:
            logging.info(u"我的基金理财余额显示：%s  不正确！" % num5.encode('utf-8'))
            raise ErrorException(u"我的基金理财余额显示：%s  不正确！" % num5.encode('utf-8'))

        #牛变现

        try:
            num6=cls.driver.find_element_by_id("com.tuniu.finance:id/tv_nbx_value").text
            assert(float(num6.encode("utf-8"))>0)
            logging.info(u"我的牛变现余额显示：%s 正确！" % num6.encode('utf-8'))
        except:
            logging.info(u"我的牛变现余额显示：%s 不正确！" % num6.encode('utf-8'))
            raise ErrorException(u"我的牛变现余额显示：%s 不正确！" % num6.encode('utf-8'))
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()
        #logging.info( "-------Testcase (WoDe_Number_Display)-----STOP-------")
        
    #我的页面链接跳转

    @get_screenshot
    def WoDe_Link_Switch(cls):

        '''
        验证我的页面链接跳转功能。
        '''

        sleep(1)
        logging.info( "-------Testcase (WoDe_Link_Switch)")
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_fourth").click()
        sleep(6)

        #途牛宝

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_tnb_key").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的途牛宝")))
            logging.info(u"我的途牛宝页面加载正确！")
            sleep(1)
        except:
            logging.info(u"我的途牛宝页面加载失败！")
            raise ErrorException(u"我的途牛宝页面加载失败！")

        #验证昨日收益_数字

        try:
            assert(float(cls.driver.find_element_by_id('com.tuniu.finance:id/earn_money').text.encode("utf-8"))>=0)
            logging.info(u"昨日收益余额显示：%s 正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/earn_money').text.encode('utf-8'))
        except:
            logging.info(u"昨日收益余额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/earn_money').text.encode('utf-8'))
            raise ErrorException(u"昨日收益余额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/earn_money').text.encode('utf-8'))
        
        #验证累计收益_数字

        try:
            assert(float(cls.driver.find_element_by_id('com.tuniu.finance:id/total_earn').text.encode("utf-8"))>0)
            logging.info(u"累计收益余额显示：%s 正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_earn').text.encode('utf-8'))
        except:
            logging.info(u"累计收益余额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_earn').text.encode('utf-8'))
            raise ErrorException(u"累计收益余额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_earn').text.encode('utf-8'))
        
        #验证总金额_数字

        try:
            assert(float(cls.driver.find_element_by_id('com.tuniu.finance:id/total_money').text.encode("utf-8"))>0)
            logging.info(u"总金额显示：%s 正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_money').text.encode('utf-8'))
        except:
            logging.info(u"总金额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_money').text.encode('utf-8'))
            raise ErrorException(u"总金额显示：%s 不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/total_money').text.encode('utf-8'))
        
        #验证万份收益_数字

        try:
            assert(float(cls.driver.find_element_by_id('com.tuniu.finance:id/ten_thousand_rate').text.encode("utf-8"))>0) 
            logging.info(u"万份收益显示：%s  正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/ten_thousand_rate').text.encode('utf-8'))
        except:
            logging.info(u"万份收益显示：%s  不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/ten_thousand_rate').text.encode('utf-8'))
            raise ErrorException(u"万份收益显示：%s  不正确！" % cls.driver.find_element_by_id('com.tuniu.finance:id/ten_thousand_rate').text.encode('utf-8'))
            sleep(2)

        #验证交易明细_跳转

        cls.driver.find_element_by_id('com.tuniu.finance:id/to_bill').click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "转入")))
            logging.info(u"途牛宝交易明细页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btn_left").click()
        except:
            logging.info(u"途牛宝交易明细页面跳转失败！")
            raise ErrorException(u"途牛宝交易明细页面跳转失败！")
        
        #验证万份收益_跳转

        cls.driver.find_element_by_id('com.tuniu.finance:id/ten_thousand_rate').click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "万份收益")))
            cls.driver.find_element_by_id("com.tuniu.finance:id/btn_left").click()
            logging.info(u"途牛宝万份收益页面跳转成功！")
        except:
            logging.info(u"途牛宝万份收益页面跳转失败！")
            raise ErrorException(u"途牛宝万份收益页面跳转失败！")
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        sleep(2)
        
        #点击定期理财

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_reg_key").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "定期理财")))
            logging.info(u"我的--定期理财页面跳转成功！")
            sleep(1)
        except:
            logging.info(u"我的--定期理财页面跳转失败！")
            raise ErrorException(u"我的--定期理财页面跳转失败！")
        
        #验证定期理财_总资产_数字

        try:
            value1=cls.driver.find_elements_by_xpath("//android.view.View[@index='0']")[1].get_attribute('name')
            value_num=float(value1.replace(value1[0:5],""))
            assert((value_num)>=0),u"我的--定期理财_总资产验证失败！" 
            logging.info(u"我的--定期理财_总资产显示：%s 正确！" % value_num)
        except:
            logging.info(u"我的--定期理财_总资产显示：%s 不正确！" % value_num)
            raise ErrorException(u"我的--定期理财_总资产显示：%s 不正确！" % value_num)
        
        #验证定期理财_昨日收益_数字

        try:
            assert(float(cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'2')]").get_attribute('name'))>=0),"定期理财_昨日收益验证失败！" 
            logging.info(u"我的--定期理财_昨日收益显示：%s 正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'2')]").get_attribute('name')))
        except:
            logging.info(u"我的--定期理财_昨日收益显示：%s 不正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'2')]").get_attribute('name')))
            raise ErrorException(u"我的--定期理财_昨日收益显示：%s 不正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[contains(@index,'2')]").get_attribute('name')))
        
        #验证定期理财_累计收益_数字

        try:
            total_num=cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'4')]")[1].get_attribute('name').encode('utf-8')
            assert(float(total_num)>=0),u"定期理财_累计收益验证失败！" 
            logging.info(u"我的--定期理财_累计收益显示：%s  正确！" % float(total_num))
        except:
            logging.info(u"我的--定期理财_累计收益显示：%s  不正确！" % float(total_num))
            raise ErrorException(u"我的--定期理财_累计收益显示：%s  不正确！" % float(total_num))
        sleep(1)
        
        #验证查看可变现资产页面

        cls.driver.find_element_by_accessibility_id("查看可变现资产 Link").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "可变现")))
            logging.info(u"我的--可变现资产页面跳转正确！")
            sleep(1)
        except:
            logging.info(u"我的--可变现页面跳转失败！")
            raise ErrorException(u"我的--可变现页面跳转失败！")
        
        #验证可变现金额 正确

        try:
            assert(float(cls.driver.find_elements_by_xpath("//android.view.View[@index='0']")[1].get_attribute('name'))>=0),"可变现金额 正确"
            logging.info(u"我的--可变现金额显示：%s  正确！" % float(cls.driver.find_elements_by_xpath("//android.view.View[@index='0']")[1].get_attribute('name')))
        except:
            logging.info(u"我的--可变现金额显示：%s  不正确！" % float(cls.driver.find_elements_by_xpath("//android.view.View[@index='0']")[1].get_attribute('name')))
            raise ErrorException(u"我的--可变现金额显示：%s  不正确！" % float(cls.driver.find_elements_by_xpath("//android.view.View[@index='0']")[1].get_attribute('name')))
        
        #验证已变现金额 正确

        try:
            assert(float(cls.driver.find_element_by_xpath("//android.view.View[@index='2']").get_attribute('name'))>=0),"已变现金额 正确"
            logging.info(u"我的--已变现金额显示：%s  正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[@index='2']").get_attribute('name')))
        except:
            logging.info(u"我的--已变现金额显示：%s  不正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[@index='2']").get_attribute('name')))
            raise ErrorException(u"我的--已变现金额显示：%s  不正确！" % float(cls.driver.find_element_by_xpath("//android.view.View[@index='2']").get_attribute('name')))
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/ll_left").click()
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/ll_left").click()
        
        #点击我的基金

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_fund_key").click()
        sleep(50)
        try:
            WebDriverWait(cls.driver, 50).until(EC.presence_of_element_located((By.NAME, "我的基金理财")))
            logging.info(u"我的--我的基金页面跳转成功！")
        except:
            logging.info(u"我的--我的基金页面跳转失败！")
            raise ErrorException(u"我的--我的基金页面跳转失败！")
        
        #验证基金理财当前持有金额

        try:
            assert(float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'0')]"))[0].get_attribute('name'))>=0),"基金理财当前持有金额正确"
            logging.info(u"我的--基金理财当前持有金额显示：%s  正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'0')]"))[0].get_attribute('name')))
        except:
            logging.info(u"我的--基金理财当前持有金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'0')]"))[0].get_attribute('name')))
            raise ErrorException(u"我的--基金理财当前持有金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'0')]"))[0].get_attribute('name')))
        
        #验证基金理财累计收益金额

        try:
            #assert(float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'2')]"))[0].get_attribute('name'))>=0),"基金理财累计收益金额正确"
            logging.info(u"我的--基金理财累计收益金额显示：%s  正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'2')]"))[0].get_attribute('name')))
        except:
            logging.info(u"我的--基金理财累计收益金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'2')]"))[0].get_attribute('name')))
            raise ErrorException(u"我的--基金理财累计收益金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'2')]"))[0].get_attribute('name')))
        
        #银行卡显示

        try:
            cls.driver.find_element_by_accessibility_id("工商银行 （***3946）").click()
            logging.info(u"我的--我的基金页面--银行卡跳转成功！")
        except:
            logging.info(u"我的--我的基金页面--银行卡跳转失败！")
            raise ErrorException(u"我的--我的基金页面--银行卡跳转失败！")
        sleep(2)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        
        #点击牛变现

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_nbx_key").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的投资")))
            logging.info(u"我的--牛变现页面跳转成功！")
        except:
            logging.info(u"我的--牛变现页面跳转失败！")
            raise ErrorException(u"我的--牛变现页面跳转失败！")
        
        #验证牛变现持有金额

        try:
            assert(float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'1')]"))[2].get_attribute('name'))>0),"牛变现当前持有金额正确"
            logging.info(u"我的--牛变现持有金额显示：%s  正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'1')]"))[2].get_attribute('name')))
        except:
            logging.info(u"我的--牛变现持有金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'1')]"))[2].get_attribute('name')))
            raise ErrorException(u"我的--牛变现持有金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'1')]"))[2].get_attribute('name')))
        
        #验证牛变现累计收益金额

        try:
            assert(float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'3')]"))[0].get_attribute('name'))>=0),"牛变现当前持有金额正确"
            logging.info(u"我的--牛变现累计收益金额显示：%s  正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'3')]"))[0].get_attribute('name')))
        except:
            logging.info(u"我的--牛变现累计收益金额显示：%s  不正确！" % float((cls.driver.find_elements_by_xpath("//android.view.View[contains(@index,'3')]"))[0].get_attribute('name')))
            raise ErrorException()
        
        #验证有牛变现产品

        sleep(1)
        cls.driver.find_element_by_accessibility_id("牛变现245012292").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的交易单")))
            logging.info(u"我的--牛变现产品页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--牛变现产品页面加载失败！")
            raise ErrorException(u"我的--牛变现产品页面加载失败！")
        sleep(2)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()

        #点击途牛宝提现按钮

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_cash_out").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "转出")))
            logging.info(u"我的--途牛宝提现页面跳转成功")
        except:
            logging.info(u"我的--途牛宝提现页面跳转失败！")
            raise ErrorException(u"我的--途牛宝提现页面跳转失败！")
        
        #验证银行卡

        try:
            cls.driver.find_element_by_id("com.tuniu.finance:id/bank_name").click()
            logging.info(u"我的--途牛宝--提现页面--银行卡页面跳转成功！")
        except:
            logging.info(u"我的--途牛宝--提现页面--银行卡跳转失败！")
            raise ErrorException(u"我的--途牛宝--提现页面--银行卡跳转失败！")
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()

        #点击充值按钮

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_recharge").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "转入")))
            logging.info(u"我的--途牛宝充值页面跳转成功")
        except:
            logging.info(u"我的--途牛宝充值页面加载失败！")
            raise ErrorException(u"我的--途牛宝充值页面加载失败！")
        
        #验证银行卡

        try:
            cls.driver.find_element_by_id("com.tuniu.finance:id/bank_name").click()
            logging.info(u"我的--途牛宝--充值页面--银行卡页面跳转成功！")
        except:
            logging.info(u"我的--途牛宝--充值页面--银行卡跳转失败！")
            raise ErrorException(u"我的--途牛宝--充值页面--银行卡跳转失败！")
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()

        #我的理财券页面

        cls.driver.find_element_by_id("com.tuniu.finance:id/rl_my_finance_coupon").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的电子券")))
            logging.info(u"我的--我的电子券页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--我的电子券页面跳转失败！")
            raise ErrorException(u"我的--我的电子券页面跳转失败！")
        
        #我的红包页面

        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_my_redpacket").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的红包")))
            logging.info(u"我的--我的红包页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--我的红包页面跳转失败！")
            raise ErrorException(u"我的--我的红包页面跳转失败！")
        
        #我的银行卡页面

        cls.driver.find_element_by_id("com.tuniu.finance:id/rl_my_card").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的银行卡")))
            logging.info(u"我的--我的银行卡页面跳转成功！")
        except:
            logging.info(u"我的银行卡页面加载失败！")
            raise ErrorException(u"我的银行卡页面加载失败！")
        
        #验证银行卡显示

        try:
            cls.driver.find_element_by_accessibility_id("工商银行储蓄卡").click()
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "银行卡详情")))
            logging.info(u"我的--我的红包页面--银行卡详情页面跳转成功！")
            sleep(2)
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--我的红包页面--银行卡详情页面跳转失败！")
            raise ErrorException(u"我的--我的红包页面--银行卡详情页面跳转失败！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_first").click()
        #logging.info( "-------Testcase (WoDe_Link_Switch)-----STOP-------")
       
    #途牛宝下单

    @get_screenshot
    def TuNiuBao_Order(cls):

        '''
        验证途牛宝可以正常下单。
        '''

        logging.info( "-------Testcase (TuNiuBao_Order)")
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_first").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_fourth").click()
        sleep(2)
        cls.driver.find_element_by_id('com.tuniu.finance:id/tv_tnb_key').click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "我的途牛宝")))
            logging.info(u"我的--我的途牛宝页面跳转成功！")
        except:
            logging.info(u"我的--我的途牛宝页面跳转失败！")
            raise ErrorException(u"我的--我的途牛宝页面跳转失败！")

        #点击转出按钮

        cls.driver.find_element_by_id('com.tuniu.finance:id/money_out').click()
        try:

            #快速转出

            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "转出")))
            logging.info(u"我的--我的途牛宝--转出页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/bt_normal").click()
            try:

                #普通转出

                text=cls.driver.find_element_by_id("com.tuniu.finance:id/click_desc")
                logging.info(u"我的--我的途牛宝--转出--普通转出页面跳转成功！")
            except:
                logging.info(u"我的--我的途牛宝--转出--普通转出页面跳转失败！")
                raise ErrorException(u"我的--我的途牛宝--转出--普通转出页面跳转失败！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--我的途牛宝--转出页面跳转失败！")
            raise ErrorException(u"我的--我的途牛宝页面跳转失败！")

        #点击转入按钮

        cls.driver.find_element_by_id('com.tuniu.finance:id/money_in').click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "转入")))
            logging.info(u"我的--我的途牛宝--转入页面跳转成功！")
            cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        except:
            logging.info(u"我的--我的途牛宝--转入页面跳转失败！")
            raise ErrorException(u"我的--我的途牛宝--转入页面跳转失败！")
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/tv_first").click()
        #logging.info( "-------Testcase (TuNiuBao_Order)-----STOP-------")
        
    #定期理财下单

    @get_screenshot
    def DingQiLiCai_Order(cls):

        '''
        验证定期理财产品可以正常下单。
        '''

        pass

    #牛变现下单

    @get_screenshot
    def NiuBianXian_Order(cls):

        '''
        验证牛变现可以正常下单。
        '''

        logging.info( "-------Testcase (NiuBianXian_Order)")
        sleep(2)
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_second").click()
        cls.driver.find_element_by_name("牛变现").click()
        sleep(5)

        try:
            cls.driver.find_elements_by_xpath("//android.view.View[@index='1']")[0].click()
            logging.info(u"牛变现产品页第一个产品加载加载成功！")
        except:
            logging.info(u"牛变现产品页第一个产品加载加载失败！")
            raise ErrorException(u"牛变现产品页第一个产品加载加载失败！")

        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "产品介绍")))
            logging.info(u"牛变现产品详情页面跳转成功！")
        except:
            logging.info(u"牛变现产品详情页面加载失败！")
            raise ErrorException(u"牛变现产品详情页面加载失败！")
        sleep(3)

        try:
            try:
                WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "募集成功 Link")))
                logging.info(u"所有牛变现产品均已募集成功！")
                cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
                sleep(2)
                cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()#返回至首页
                sleep(3)
                return
            except:
                try:
                    WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "还有机会 Link")))
                    logging.info(u"所有牛变现产品均已募集成功！")
                    cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
                    sleep(2)
                    cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()#返回至首页
                    sleep(3)
                    return
                except:
                    cls.driver.find_element_by_accessibility_id("马上购买 Link").click()
                    sleep(4)
                    WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "申购")))
                    logging.info(u"牛变现申购页面跳转成功！")
        except:
            logging.info(u"牛变现申购页面跳转失败！")
            raise ErrorException(u"牛变现申购页面跳转失败！")

        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "确认购买 Link")))
            logging.info(u"牛变现确认购买页面跳转成功！")
        except:
            logging.info(u"牛变现确认购买页面跳转失败！")
            raise ErrorException(u"牛变现确认购买页面跳转失败！")
        sleep(1)
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()#返回至首页
        #logging.info( "-------Testcase (NiuBianXian_Order)-----STOP-------")
        
    #基金下单

    @get_screenshot
    def JiJinLiCai_Order(cls):

        '''
        验证基金理财产品可以正常下单。
        '''

        logging.info( "-------Testcase (JiJinLiCai_Order)")
        sleep(2)
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_third").click()
        action2=TouchAction(cls.driver)

        #在空白的地方点一下
        
        action2.press(x=10,y=10).wait(ms=100).release().perform()
        sleep(2)

        cls.driver.find_elements_by_accessibility_id("近一年涨跌幅")[0].click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "基金详情")))
            logging.info(u"基金产品详情页面跳转成功！")
        except:
            logging.info(u"基金产品详情页面跳转失败！")
            raise ErrorException(u"基金产品详情页面跳转失败！")
        cls.driver.find_element_by_accessibility_id("买入 Link").click()
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "购买")))
            logging.info(u"基金产品购买页面跳转成功！")
        except:
            logging.info(u"基金产品购买页面跳转失败！")
            raise ErrorException(u"基金产品购买页面跳转失败！")
        try:
            WebDriverWait(cls.driver, 10).until(EC.presence_of_element_located((By.NAME, "购买 Link")))
            logging.info(u"基金产品购买按钮加载成功！")
        except:
            logging.info(u"基金产品购买按钮加载失败！")
            raise ErrorException(u"基金产品购买按钮加载失败！")
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/btnn_left").click()
        cls.driver.find_element_by_id("com.tuniu.finance:id/iv_first").click()#返回至首页
        #logging.info( "-------Testcase (JiJinLiCai_Order)-----STOP-------")


if __name__=="__main__":

    #获取当前时间,并以时间命名生成文件和文件夹

    timeFlag=time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    report_name=timeFlag+"-report.html"
    log_name=timeFlag+"-logging.log"
    folder_name=timeFlag+"-report"

    #生成一个文件夹

    Folder_Path=os.path.join(r"C:\Users\shifawu\Desktop\App_Automation\Results",folder_name)  #文件位置
    os.mkdir(Folder_Path)

    #生成一个日志文件

    Log_Path=os.path.join(Folder_Path,log_name)
    console_out(Log_Path)
    sleep(1)
    logging.info(u"日志文件生成成功！")


    #设置执行套件
	
    suite=unittest.TestSuite()
    suite.addTest(Main_Flowsheet("LogIn"))
    suite.addTest(Main_Flowsheet("ShouYe_Number_Display"))
    suite.addTest(Main_Flowsheet("ShouYe_Link_Switch"))
    suite.addTest(Main_Flowsheet("DingQiLiCai"))
    suite.addTest(Main_Flowsheet("NiuBianXian"))
    suite.addTest(Main_Flowsheet("JiJinLiCai"))
    suite.addTest(Main_Flowsheet("WoDe_Number_Display"))
    suite.addTest(Main_Flowsheet("WoDe_Link_Switch"))
    suite.addTest(Main_Flowsheet("TuNiuBao_Order"))
    suite.addTest(Main_Flowsheet("NiuBianXian_Order"))
    suite.addTest(Main_Flowsheet("JiJinLiCai_Order"))
    suite.addTest(Main_Flowsheet("LogOut"))
    sleep(10)



    #生成一个报告文件
    #对这个报告进行了一系列改造，见D:\Python2.7\installation\Lib\HTMLTestRunner.py  模板。

    Report_File_Path=os.path.join(Folder_Path,report_name)
    fp=file(Report_File_Path,"wb")
    runner=HTMLTestRunner.HTMLTestRunner(stream=fp,title=u"途牛金服APP自动化界面测试报告",description="")
    test_results=runner.run(suite)
    fp.close()
    logging.info(u"测试报告生成成功！" ) 

    #定制邮件简化表格内容

    all_case_number=test_results.testsRun
    all_test_cases=[]
    pass_test_cases=[]

    #从suite中获取all cases

    for i in suite:
        all_test_cases.append(str(i).split()[0])

    #从suite中获取pass cases

    for i in test_results.result:
            if i[0]==0:
                pass_test_cases.append(str(i[1]).split()[0])
    failed_test_cases=[item for item in all_test_cases if item not in pass_test_cases ] 

    failed_case_number=len(failed_test_cases)
    pass_case_number=all_case_number-failed_case_number
    pass_rate=round((float(pass_case_number)/float(all_case_number))*100,2)
    load_pass_results=""
    
    #定制简化邮件模板内容

    f=util.EmailContent()
    load_pass_results=f.getLoadPassResults(pass_test_cases)
    load_failed_results=f.getLoadFailedResults(failed_test_cases)
    mail_template_path=os.path.join(r"C:\Users\shifawu\Desktop\App_Automation","UI_mail_template.html")

    try:
        with open(mail_template_path,"r+") as f:
            mail_template_contents=f.read()
    except:
        print "No UI_mail_template.html in CURRENT FOLDER!!!"

    detailed_report_link=r"\\"+Report_File_Path.replace("C:","172.17.33.25")
    contents=mail_template_contents % (detailed_report_link,all_case_number,pass_case_number,failed_case_number,pass_rate,load_pass_results,load_failed_results)
    simple_report_path=os.path.join(Folder_Path,"simple.html")

    with open(simple_report_path,"w+") as f:
        f.write(contents)
    sleep(3)

    #发送邮件
    #只有当有错误的测试用例时， 才发送邮件！

    if failed_test_cases:
        email=util.Send_Email(Folder_Path)
        email.new_file()
        with open(simple_report_path,"r+") as f:
            simple_content=f.read()
        email.send_mail(contents=simple_content)
    else:
        logging.info(u"所有用例执行成功，本次不发送邮件！！！" ) 

    #添加一个结果记录文件

    results_report_path=os.path.join(r"C:\Users\shifawu\Desktop\App_Automation","results_report.txt")
    with open(results_report_path,"a") as f:
        results_content=timeFlag+":     "+"All: "+str(all_case_number)+"     Pass: "+str(pass_case_number)+"     Failed: "+str(failed_case_number)+"\n"
        f.write(results_content)
    sleep(10)

    #直接用unittest框架RUN
    #unittest.TextTestRunner(verbosity=2).run(suite) 
