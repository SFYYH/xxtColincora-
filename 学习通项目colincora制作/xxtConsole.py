import json
import re
import threading
from queue import Queue
from urllib import parse
from pyDes import des, PAD_PKCS5
import binascii
import os
import requests
import sys
import time
from lxml import etree
global video_url_list
video_url_list = []
class_list = []
#密码的des加密
def des_pwd(msg, key):
    des_obj = des(key, key, pad=None, padmode=PAD_PKCS5)
    secret_bytes = des_obj.encrypt(msg, padmode=PAD_PKCS5)
    return binascii.b2a_hex(secret_bytes)

# 视频任务enc校验计算
def encode_enc(clazzid: str, duration: int, objectId: str, otherinfo: str, jobid: str, userid: str, currentTimeSec: str):
    import hashlib
    data = "[{0}][{1}][{2}][{3}][{4}][{5}][{6}][0_{7}]".format(clazzid, userid, jobid, objectId, int(currentTimeSec) * 1000, "d_yHJ!$pdA~5", duration * 1000, duration)
    #print(data)
    return hashlib.md5(data.encode()).hexdigest()

#登录函数 手机号登录
def sign_in(uname: str, password: str):
    sign_in_url = "https://passport2.chaoxing.com/fanyalogin"
    des_obj = des("u2oh6Vu^", "u2oh6Vu^", pad=None, padmode=PAD_PKCS5)
    secret_bytes = des_obj.encrypt(password, padmode=PAD_PKCS5)
    sign_in_data = {"fid": "-1",
                "uname": uname,
                "password": binascii.b2a_hex(secret_bytes).decode("utf-8"),
                "t": "true",
                "forbidotherlogin": "0",
                "validate": ""}
    sign_in_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '196',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'JSESSIONID=17ADF7A739E6254D0B6090E2BA84E045; route=2751c02f853f6479988f0b3d8a5cb9ce; fid=2867; source=""; createSiteSource=""',
        'Host': 'passport2.chaoxing.com',
        'Origin': 'https://passport2.chaoxing.com',
        'Referer': 'https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https://i.chaoxing.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    sign_in_rsp = requests.post(url=sign_in_url, data=sign_in_data, headers=sign_in_headers)
    print(des_pwd(password, "u2oh6Vu^").decode('utf-8'))
    return sign_in_rsp

#用户登录后合并cookie
def step_1():
    #判断登录状态
    sign_sus=False
    while sign_sus==False:
        #如果密码错误，清屏重新开始输入账号密码
        os.system("cls")
        username=input("请输入你的手机号：")
        password=input("请输入你的密码：")
        sign_in_rsp=sign_in(username,password)
        sign_in_json=sign_in_rsp.json()
        # print(sign_in_json)
        if sign_in_json['status']==False:
            print(sign_in_json.get('msg2'),",请按回车重新输入账号密码！")
        else:
            sign_sus=True
            print("恭喜你登陆成功！")
    #整合cookie 全局通用
    global cookieStr,uid,global_headers
    uid=sign_in_rsp.cookies['_uid']
    cookieStr=''
    for item in sign_in_rsp.cookies:
        cookieStr=cookieStr+item.name+'='+item.value+';'
    global_headers={
        'Cookie':cookieStr,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }

#读取课程内容
def step_2():
    class_url="http://mooc1-2.chaoxing.com/visit/courses"
    class_rsp=requests.get(url=class_url,headers=global_headers)
    #判断是否可以访问课程页面
    if class_rsp.status_code==200:
        class_html=etree.HTML(class_rsp.text)
        os.system("cls")
        print("处理成功！你当前已经开启的课程如下所示:\n")
        i=0
        #存课程的字典
        global course_dict
        course_dict={}
        for class_item in class_html.xpath("/html/body/div/div[2]/div[3]/ul/li[@class='courseItem curFile']"):
            #做个异常抛出，如果错误略过,因为等待开课的课程由于尚未对应链接，所以缺少a标签。
            try:
                class_item_name=class_item.xpath("./div[2]/h3/a/@title")[0]
                i+=1
                print(class_item_name)
                #字典装课程的名字和连接
                course_dict[i]=[class_item_name,"https://mooc1-2.chaoxing.com{}".format(class_item.xpath("./div[1]/a[1]/@href")[0])]
            except:
                pass
        print("-----------------------------")
    else:
        print("获取课程信息失败，请联系作者Q3300519161进行反馈！！！")

#获取url重定向后的新地址和cpi
def url_302(oldUrl:str):
    # 302跳转，requests库默认追踪headers里的location进行跳转，使用allow_redirects=False
    course_302_rsp=requests.get(url=oldUrl,headers=global_headers,allow_redirects=False)
    new_url=course_302_rsp.headers.get("Location")
    if new_url==None:#如果重定向后的地址是空那么就让新的地址等于原来的地址
        new_url=oldUrl
    result=parse.urlparse(new_url)
    new_url_data=parse.parse_qs(result.query)
    try:
        cpi=new_url_data.get("cpi")[0]
    except:
        print("获取cpi失败!")
        cpi=None
    return {"new_url":new_url,"cpi":cpi}

#获取所有课程信息的html——resp源码
def course_get(url:str):
    course_headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    }
    course_rsp=requests.get(url=url,headers=course_headers)
    course_html=etree.HTML(course_rsp.text)
    return course_html

#通过递归读取章节
def recursive_course(course_unit_list,chapter_mission,level):
    #单元列表——章节————div层次
    for course_unit in course_unit_list:
        h3_list=course_unit.xpath("./h3")
        for h3_item in h3_list:
            # 如果是openlock说明已经完成了,orange表示任务点未完成
            chapter_status=__list_get(h3_item.xpath("./a/span[@class='icon']/em/@class"))
            #根据任务点判断是否完成
            if chapter_status=="orange":
                print("--"*level,__list_get(h3_item.xpath("./a/span[@class='articlename']/@title")),"     ",__list_get(h3_item.xpath("./a/span[@class='icon']/em/text()")))
                chapter_mission.append("https://mooc1-2.chaoxing.com{}".format(__list_get(h3_item.xpath("./a/@href"))))
            else:
                print("--" * level, __list_get(h3_item.xpath("./a/span[@class='articlename']/@title")), "      ", "已完成课程")
        chapter_item_list=course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course(chapter_item_list.course_unit_list, chapter_mission, level+1)

#thread 线程池操作
# thread
def createQueue(urls):
    urlQueue = Queue()
    for url in urls:
        urlQueue.put(url)
    return urlQueue


class spiderThread(threading.Thread):
    def __init__(self, threadName, urlQueue, cpi):
        super(spiderThread, self).__init__()
        self.threadName = threadName
        self.urlQueue = urlQueue
        self.cpi = cpi

    def run(self):
        while True:
            if self.urlQueue.empty():
                break
            chapter = self.urlQueue.get()
            deal_misson([chapter], self.cpi, 0)
            time.sleep(0.2)


def createThread(threadCount, urlQueue, cpi):
    threadQueue = []
    for i in range(threadCount):
        spiderThreading = spiderThread("threading_{}".format(i), urlQueue=urlQueue, cpi=cpi)  # 循环创建多个线程，并将队列传入
        threadQueue.append(spiderThreading)  # 将线程放入线程池
    return threadQueue


#看视频线程
class video_nomal_thread(threading.Thread):
    def __list_get(self, list: list):
        if len(list):
            return list[0]
        else:
            return ""

    def __init__(self, url):
        super(video_nomal_thread, self).__init__()
        self.url = url
        self.all_time = int(re.findall("duration=\\d+&", url)[0][9:-1])
        self.multimedia_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Cookie': cookieStr,
            'Host': 'mooc1.chaoxing.com',
            'Referer': 'https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2020-1105-2010',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Microsoft Edge";v="90"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.51'
        }
        self.clazzId = self.__list_get(re.findall("(?<=clazzId=)\\d+", self.url))
        self.duration = self.__list_get(re.findall("(?<=duration=)\\d+", self.url))
        self.objectId = self.__list_get(re.findall("(?<=objectId=)[0-9a-zA-Z]+", self.url))
        self.otherInfo = self.__list_get(re.findall("(?<=otherInfo=)[a-z0-9A-Z_-]+", self.url))
        self.jobid = self.__list_get(re.findall("(?<=jobid=)\\d+", self.url))
        self.uid = self.__list_get(re.findall("(?<=userid=)\\d+", self.url))

    def run(self) -> None:
        rsp = requests.get(url=self.url_replace(0), headers=global_headers)
        #print(rsp.status_code)
        cookieTmp = cookieStr
        for item in rsp.cookies:
            cookieTmp = cookieTmp + item.name + '=' + item.value + ';'
        self.multimedia_headers.update({"Cookie": cookieTmp})
        print("线程%s启动中，总任务时长%d秒" % (self.name, self.all_time))
        time_now = 60
        while time_now < self.all_time + 60:
            time.sleep(60)
            rsp = requests.get(url=self.url_replace(time_now), headers=self.multimedia_headers)
            print("线程%s运行中，当前时长:%d ,总时长:%d" % (self.name, time_now, self.all_time))
            time_now = time_now + 60

        rsp = requests.get(url=self.url_replace(self.all_time), headers=self.multimedia_headers)
        print("线程%s执行完成，任务状态:%s" % (self.name, rsp.text))

    def url_replace(self, now_time: int) -> str:
        enc_tmp = encode_enc(self.clazzId, int(self.duration), self.objectId, self.otherInfo, self.jobid, self.uid, str(now_time))
        url_tmp = re.sub("playingTime=\\d+", "playingTime=%d" % now_time, self.url)
        url_tmp = re.sub("enc=[0-9a-zA-Z]+", "enc=%s" % enc_tmp, url_tmp)
        return url_tmp

#返回列表头一个数值
def __list_get(list: list):
    if len(list):
        return list[0]
    else:
        return ""

#选取有任务点的课程，进行处理
def deal_course_select(url_class):
    #存的是重定向后的新地址和cpi
    new_url_dict=url_302(url_class)
    new_url=new_url_dict["new_url"]
    course_html=course_get(new_url)
    #为防止账号没有课程或者班级，需要做一个报错处理
    #chapter_misson每一个章节的会话
    chapter_mission=[]#章节数
    try:
        course_unit_list=course_html.xpath("//div[@class='units']")
        for course_unit in course_unit_list:
            #打印出有任务点的二级标题
            print(__list_get(course_unit.xpath("./h2/a/@title")))
            #递归读取章节
            recursive_course(course_unit.xpath("./div"),chapter_mission,1)
    except Exception as e:
        print("选取任务点出错 %s"%e)
    print("课程读取完成，共有%d个章节可一键完成"%len(chapter_mission))
    # print(chapter_mission)
    deal_misson(chapter_mission, new_url_dict["cpi"], 0)

#处理任务
def deal_misson(missons: list, class_cpi: str, mode: int):
    for chapter_mission_item in missons:
        result = parse.urlparse(chapter_mission_item)
        chapter_data = parse.parse_qs(result.query)
        clazzId = chapter_data.get('clazzid')[0]
        courseId = chapter_data.get('courseId')[0]
        chapterId = chapter_data.get('chapterId')[0]
        # workAnswerId=chapter_data.get('workAnswerId')[0]
        print(clazzId,courseId,class_cpi)
        kc_clazzId=clazzId
        kc_courseId=courseId
        kc_cpi=class_cpi
        print(courseId,clazzId,class_cpi)
        cardcount = int(read_cardcount(courseId, clazzId, chapterId, class_cpi))
        for num in range(cardcount):
            try:
                #print("num:", num)
                medias_url = "https://mooc1-2.chaoxing.com/knowledge/cards?clazzid={0}&courseid={1}&knowledgeid={2}&num={4}&ut=s&cpi={3}&v=20160407-1".format(clazzId, courseId, chapterId, class_cpi, num)
                medias_rsp = requests.get(url=medias_url, headers=global_headers)
                medias_HTML = etree.HTML(medias_rsp.text)
                medias_text = medias_HTML.xpath("//script[1]/text()")[0]
                pattern = re.compile(r"mArg = ({[\s\S]*)}catch")
                datas = re.findall(pattern, medias_text)[0]
                datas = json.loads(datas.strip()[:-1])
                if mode == 0:
                    # mode 0 deal misson
                    medias_deal(datas, clazzId, chapterId, courseId, chapter_mission_item)
                else:
                    # mode 1 download medias
                    # medias_download(datas["attachments"])
                    pass
                # print(workAnswerId)
                # print(result.query)
            except Exception as e:
                print(medias_url + " error", e)
                continue

#递归读取所有课程信息，并返回dict
def recursive_course_dict(course_unit_list,chapter_dict):
    for course_unit in course_unit_list:
        h3_list=course_unit.xpath("./h3")
        for h3_item in h3_list:
            #chapter_dict存的是 每一个章节里课程任务点的序号+课程名字+课程标题+课程url
            chapter_dict.updata({__list_get(h3_item.xpath("./a/span[@class='chapterNumber']/text()")+__list_get(h3_item.xpath("./a/span[@class='articlename']/span[@class='chapterNumber']/text()")))})
        chapter_item_list=course_unit.xpath("./div")
        if chapter_item_list:
            recursive_course_dict(course_unit_list, chapter_dict)

#获取所有的课程信息，并存储url
def deal_course_all(url_class):
    new_url_dict=url_302(url_class)
    new_url=new_url_dict["new_url"]
    course_html=course_get(new_url)
    i=0
    chapter_dict={}
    course_unit_list=course_html.xpath("//div[@class='units']")#课程中的大章节
    try:
        for course_unit in course_unit_list:
            recursive_course_dict(course_unit.xpath("./div"), chapter_dict)
        chapter_list=[]
        for chapter_item in chapter_dict:
            i=i+1
            try:
                #print("%d"%i,chapter_item)
                chapter_list.append(chapter_dict[chapter_item])
            except Exception as e:
                print("chapter处理错误",e)
    except Exception as e:
        print(e)
    while True:
        enter=input("请输入资源所在章节")

#  处理Audio任务
def misson_audio(objectId, otherInfo, jobid, name, reportUrl, clazzId):
    status_url = "https://mooc1-2.chaoxing.com/ananas/status/{}?_dc=1667628931806".format(objectId)
    misson_headers = {
        "Referer": "https://mooc1-2.chaoxing.com/ananas/modules/audio/index.html?v=2022-1028-1705"
    }
    misson_headers.update(global_headers)
    status_rsp = requests.get(url=status_url, headers=misson_headers)
    status_json = None
    try:
        status_json = json.loads(status_rsp.text)
    except Exception as e:
        print("该音频任务点信息读取错误", status_rsp.status_code, status_url)
        return
    duration = status_json.get('duration')
    dtoken = status_json.get('dtoken')
    #print(objectId, otherInfo, jobid, uid, name, duration, reportUrl)
    elses = "/{0}?clazzId={1}&playingTime={2}&duration={2}&clipTime=0_{2}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag=0&view=pc&enc={7}&rt=1&dtype=Audio&_t={8}".format(dtoken, clazzId, duration, objectId, otherInfo, jobid, uid, encode_enc(clazzId, duration, objectId, otherInfo, jobid, uid, duration), int(time.time() * 1000))
    reportUrl_item = reportUrl + str(elses)
    video_url_list.append(reportUrl_item)
    print("检测到一个音频节点，已添加到任务列表")
    # multimedia_rsp = requests.get(url=reportUrl_item, headers=misson_headers)
    return reportUrl_item

# 读取章节页数
def read_cardcount(courseId: str, clazzid: str, chapterId: str, cpi: str):
    url = 'https://mooc1-2.chaoxing.com/mycourse/studentstudyAjax'
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Content-Length': '87',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Origin': 'https://mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/mycourse/studentstudy?chapterId=357838590&courseId=214734258&clazzid=32360675&enc=ccf66103f539dfec439e4898b62c8024',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.60',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = "courseId={0}&clazzid={1}&chapterId={2}&cpi={3}&verificationcode=".format(courseId, clazzid, chapterId, cpi)
    rsp = requests.post(url=url, headers=headers, data=data)
    rsp_HTML = etree.HTML(rsp.text)
    card_count = 0
    try:
        card_count = rsp_HTML.xpath("//input[@id='cardcount']/@value")[0]
    except Exception as e:
        print("card count error", rsp.status_code, rsp.text, e)
    return card_count

# 判断媒体类型并处理
def medias_deal(data, clazzId, chapterId, courseId, chapterUrl):
    result_json = data["attachments"]
    #print(result_json)
    #href = "https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?courseid=" + courseId + "&clazzid=" + clazzId + "&cpi=" + cpi + "&ut=s"
    for media_item in result_json:
        if media_item.get("job") == None:
            continue
        media_type = media_item.get("type")
        jobid = media_item.get("jobid")
        if media_type == "video":
            objectId = media_item.get("objectId")
            otherInfo = media_item.get("otherInfo")
            name = media_item.get('property').get('name')
            if (media_item.get('property').get('module') == "insertaudio"):
                misson_audio(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=data["defaults"]["reportUrl"], clazzId=clazzId)
            else:
                url_video = misson_video(objectId=objectId, otherInfo=otherInfo, jobid=jobid, name=name, reportUrl=data["defaults"]["reportUrl"], clazzId=clazzId)
            # multimedia_headers = {
            #     'Accept': '*/*',
            #     'Accept-Encoding': 'gzip, deflate, br',
            #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            #     'Connection': 'keep-alive',
            #     'Content-Type': 'application/json',
            #     'Cookie': cookieStr,
            #     'Host': 'mooc1-1.chaoxing.com',
            #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
            #     'Sec-Fetch-Dest': 'empty',
            #     'Sec-Fetch-Mode': 'cors',
            #     'Sec-Fetch-Site': 'same-origin',
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
            # }
            # rsp = requests.get(url=url_video, headers=multimedia_headers)
            # print(rsp.text)
        elif media_type == "live":
            streamName = media_item.get("property").get("streamName")
            vdoid = media_item.get("property").get("vdoid")
            misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzId)
        elif media_type == "document":
            jtoken = media_item.get("jtoken")
            misson_doucument(jobid, chapterId, courseId, clazzId, jtoken)
        elif "bookname" in media_item["property"]:
            jtoken = media_item.get("jtoken")
            misson_book(jobid, chapterId, courseId, clazzId, jtoken)
        elif media_type == "read":
            jtoken = media_item.get("jtoken")
            misson_read(jobid, chapterId, courseId, clazzId, jtoken)
        # elif media_type==""

# 处理live任务，核心为获取视频token
def misson_live(streamName, jobid, vdoid, courseId, chapterId, clazzid):
    src = 'https://live.chaoxing.com/courseLive/newpclive?streamName=' + streamName + '&vdoid=' + vdoid + '&width=630&height=530' + '&jobid=' + jobid + '&userId={0}&knowledgeid={1}&ut=s&clazzid={2}&courseid={3}'.format(uid, chapterId, clazzid, courseId)
    rsp = requests.get(url=src, headers=global_headers)
    rsp_HTML = etree.HTML(rsp.text)
    token_url = rsp_HTML.xpath("//iframe/@src")[0]
    #print(token_url)
    token_result = parse.urlparse(token_url)
    token_data = parse.parse_qs(token_result.query)
    token = token_data.get("token")
    finish_url = "https://zhibo.chaoxing.com/live/saveCourseJob?courseId={0}&knowledgeId={1}&classId={2}&userId={3}&jobId={4}&token={5}".format(courseId, chapterId, clazzid, uid, jobid, token[0])
    finish_rsp = requests.get(url=finish_url, headers=global_headers)
    #print(finish_rsp.text)


# 处理document任务，核心为jtoken
def misson_doucument(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/pdf/index.html?v=2020-1103-1706',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/document?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc=1607066762782'.format(jobid, chapterId, courseid, clazzid, jtoken)
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    #print(multimedia_rsp.text)

# 处理book任务，核心为jtoken
def misson_book(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    #print(multimedia_rsp.text)

# 处理read任务，核心为jtoken
def misson_read(jobid, chapterId, courseid, clazzid, jtoken):
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    url = 'https://mooc1-2.chaoxing.com/ananas/job/readv2?jobid={0}&knowledgeid={1}&courseid={2}&clazzid={3}&jtoken={4}&_dc={5}'.format(jobid, chapterId, courseid, clazzid, jtoken, int(time.time() * 1000))
    multimedia_rsp = requests.get(url=url, headers=multimedia_headers)
    #print(multimedia_rsp.text)

#处理测验人物
def missio_task(jobid, chapterId, courseid, clazzid, jtoken):
    href="https://mooc2-ans.chaoxing.com/mooc2-ans/mycourse/studentcourse?courseid={0}&clazzid={1}".format(courseid,clazzid)
    multimedia_headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Connection': 'keep-alive',
        'Cookie': cookieStr,
        'Host': 'mooc1-2.chaoxing.com',
        'Referer': 'https://mooc1-2.chaoxing.com/ananas/modules/innerbook/index.html?v=2018-0126-1905',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.52',
        'X-Requested-With': 'XMLHttpRequest'
    }
    href_rsp=requests.get(url=href,headers=multimedia_headers)
    

# 处理video任务,校验为enc
def misson_video(objectId, otherInfo, jobid, name, reportUrl, clazzId):
    status_url = "https://mooc1-1.chaoxing.com/ananas/status/{}?k=&flag=normal&_dc=1600850935908".format(objectId)
    misson_headers = {
        "Referer": "https://mooc1.chaoxing.com/ananas/modules/video/index.html?v=2022-0329-1945"
    }
    misson_headers.update(global_headers)
    status_rsp = requests.get(url=status_url, headers=misson_headers)
    status_json = None
    try:
        status_json = json.loads(status_rsp.text)
    except Exception as e:
        print("该视频任务点信息读取错误", status_rsp.status_code, status_url)
        return
    duration = status_json.get('duration')
    dtoken = status_json.get('dtoken')
    print(name, duration, reportUrl)
    # multimedia_headers = {
    #     'Accept': '*/*',
    #     'Accept-Encoding': 'gzip, deflate, br',
    #     'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    #     'Connection': 'keep-alive',
    #     'Content-Type': 'application/json',
    #     'Cookie': cookieStr,
    #     'Host': 'mooc1-1.chaoxing.com',
    #     'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
    #     'Sec-Fetch-Dest': 'empty',
    #     'Sec-Fetch-Mode': 'cors',
    #     'Sec-Fetch-Site': 'same-origin',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
    # }

    elses = "/{0}?clazzId={1}&playingTime={2}&duration={2}&clipTime=0_{2}&objectId={3}&otherInfo={4}&jobid={5}&userid={6}&isdrag=0&view=pc&enc={7}&rt=1&dtype=Video&_t={8}".format(dtoken, clazzId, duration, objectId, otherInfo, jobid, uid, encode_enc(clazzId, duration, objectId, otherInfo, jobid, uid, duration), int(time.time() * 1000))
    reportUrl_item = reportUrl + str(elses)
    video_url_list.append(reportUrl_item)
    # multimedia_rsp = requests.get(url=reportUrl_item, headers=multimedia_headers)
    print("检测到一个视频节点，已添加到任务列表")
    return reportUrl_item

#自定义任务类，处理菜单任务
class Things():
    def __int__(self,username='nobody'):
        self.username=username
#完成单个课程,d
    def misson_1(self):
        os.system("cls")
        print("您所加入的课程如下：")
        for i in range(len(course_dict)):
            print("%d.%s" % (i + 1, course_dict[i + 1][0]))
        while True:
            enter = input("输入你要完成的课程序号(输入q回退主菜单)：")
            try:
                if enter == "q":
                    break
                else:
                    try:
                        input("请确认您要完成'%s'" % (course_dict[int(enter)][0]))
                    except:
                        print("'%s'并不是可识别的序号，请您重新检查后输入" % enter)
                        continue
                    global video_url_list
                    video_url_list = []
                    deal_course_select(course_dict[int(enter)][1])
                    if len(video_url_list) == 0:
                        input("\n任务已完成，回车返回主菜单")
                    else:
                        print("除视频与音频节点外任务已完成，接下来将对剩下的%d个节点进行处理" % len(video_url_list))
                        print("注意！！！当节点开启了防拖拽请选择常规速度完成，否则将会完成失败")
                        speed = input("请选择节点的完成方式 1.立即完成(1秒即可完成任务点) 2.常规速度完成(完成时间与视音频时间等长) :")
                        while speed != "1" and speed != "2":
                            print("请输入正常的序号")
                            speed = input("请选择节点的完成方式 1.立即完成(1秒即可完成任务点) 2.常规速度完成(完成时间与视音频时间等长) :")
                        if speed == "1":
                            for item in video_url_list:
                                multimedia_headers = {
                                    'Accept': '*/*',
                                    'Accept-Encoding': 'gzip, deflate, br',
                                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                                    'Connection': 'keep-alive',
                                    'Content-Type': 'application/json',
                                    'Cookie': cookieStr,
                                    'Host': 'mooc1-1.chaoxing.com',
                                    'Referer': 'https://mooc1-1.chaoxing.com/ananas/modules/video/index.html?v=2020-0907-1546',
                                    'Sec-Fetch-Dest': 'empty',
                                    'Sec-Fetch-Mode': 'cors',
                                    'Sec-Fetch-Site': 'same-origin',
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36 Edg/85.0.564.51'
                                }
                                rsp = requests.get(url=item.replace("isdrag=0", "isdrag=4"), headers=multimedia_headers)
                                #print(rsp.text)
                        else:
                            video_nomal_thread_pool = []
                            for video_item in video_url_list:
                                video_nomal_thread_pool.append(video_nomal_thread(video_item))
                            for item in video_nomal_thread_pool:
                                item.start()
                                time.sleep(1)
                            print("\n视频线程已全部启动\n")
                            for item in video_nomal_thread_pool:
                                item.join()
                        print("任务执行完成")

                    break
            except Exception as e:
                print("error:%s" % e)

    def misson_2(self):
        href="http://mooc1-2.chaoxing.com/visit/courses"
    def misson_6(self):
        os.system("cls")
        pass


#菜单制作
class Menu():
    def __init__(self):
        self.thing = Things()
        self.choices = {
            "1": self.thing.misson_1,
            # "2": self.thing.misson_2,
            "9": self.quit,
        }

    def display_menu(self):
        print("""
菜单：
1.完成单个课程中的所有任务节点(不包含测验)
        """)

    def run(self):
        while True:
            self.display_menu()
            choice = input("\n请输入您要进行的操作：")
            choice = str(choice).strip()
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print("{0}不是正确的序号，请检查后重新输入".format(choice))

    def quit(self):
        sys.exit(0)

def before_start() -> None:
    print("colincora,欢迎您的使用\n")
    print("程序改编自GITHUB开源程序\n")
    print("本人Q3300519161\n")

    print("\n且确认以下须知与功能介绍:")
    print("1.本项目支持一键完成的任务点不包括考试与测试")
    print("2.项目不能完全保证不被系统识别异常，请理性使用")
    print("3.所有功能均采用发送GET/POST请求包完成，效率更高且占用资源低")
    print("4.完成课程任务点中的视频任务点会在最后统一处理，由用户决定完成方式")
    print("5.其中快速完成可能会导致异常，而常规完成则会同步视频时长完成（需要保证软件保持开启状态）用于避免可能由时长带来的异常\n")
    print("""            _ _                           
   ___ ___ | (_)_ __   ___ ___  _ __ __ _ 
  / __/ _ \| | | '_ \ / __/ _ \| '__/ _` |
 | (_| (_) | | | | | | (_| (_) | | | (_| |
  \___\___/|_|_|_| |_|\___\___/|_|  \__,_|
                colincora
                                          """)
    input("\n回车确认后正式使用本软件:")

#主函数最后运行
if __name__ == '__main__':
    before_start()
    step_1()
    step_2()
    Menu().run()