# encoding=utf-8
import json
import random
import sys
import time
from hashlib import md5
from urllib import parse

import requests
import urllib3

urllib3.disable_warnings()

# --------------------------------------------------------------------------
phone = sys.argv[1]
pwd = sys.argv[2]
address = sys.argv[3]
lat = sys.argv[4]
lng = sys.argv[5]
district = sys.argv[6]
deviceToken = sys.argv[7]
jiShiKey = sys.argv[8]
#推送key
#sckey=pushKey.split("@")[0]
#jiShiKey = pushKey.split('@')[1]
# ---------------------------------------------------------------------------
session = requests.Session()
now = time.time() + 28800
date = time.strftime("%m{month}%d{day}", time.localtime(now)).format(month='月', day='日')

# Push
def Push(msg):
    print("推送消息:[", parse.unquote(msg),']')
   #Wxpush(msg)
    JiSHiPush(msg)

    return


# Wxpush()消息推送模块
def Wxpush(msg):
    url = f'https://sc.ftqq.com/{sckey}.send?text={date}{msg}'
    for _ in range(3):
        err = requests.get(url)
        print(err.json())
        if err.json()['data']['error'] == 'SUCCESS':
            print('消息推送成功')
            break


# 即时达推送
def JiSHiPush(msg):
    url = f'http://push.ijingniu.cn/send?key={jiShiKey}&head={date}{msg}&body={msg}'
    try:
        requests.post(url)
    except:
        pass


# 指点天下登录模块
def login():
    url = 'http://app.zhidiantianxia.cn/api/Login/pwd'
    encoded_pwd = md5('axy_{}'.format(pwd).encode()).hexdigest()
    global flag
    header = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '201',
        'Host': 'app.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.10.0'
    }
    data = {
        'phone': phone,
        'password': encoded_pwd,
        'mobileSystem': '10',
        'appVersion': '1.7.3',
        'mobileVersion': 'V1965A',
        'deviceToken': deviceToken,
        'pushToken': phone,
        'romInfo': 'vivo',
    }

    response = session.post(url=url, headers=header, data=data)
    if response.json()['status'] == 1:
        print('登录成功')
        flag = 1
    else:
        print(response.json()['msg'])
        msg = parse.quote_plus(response.json()['msg'])
        Push(msg)
        flag = 0
    return response.json()['data']


# 获取打卡信息模板ID
def get_templateID(token):
    url = 'http://zua.zhidiantianxia.cn/api/study/health/mobile/health/permission'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'user-agent': 'V1965A(Android/10) (com.axy.zhidian/1.7.3) Weex/0.18.0 1080x2241',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
    }
    response = session.get(url=url, headers=header)
    if response.status_code == 200:
        if response.json()['status'] == 1:
            template_id = response.json()['data']['templateId']
            isSubmitted = response.json()['data']['submitted']
            print("获取模板ID成功,模板ID为:", template_id, end='\n')
            return template_id, isSubmitted
        else:
            print("登录错误!")
            return -1


# 随机体温
def random_temperature():
    return str(round(random.uniform(36.2, 36.8), 1))


# 每日健康打卡模块
def sign_in(token):
    url = 'http://zua.zhidiantianxia.cn/api/study/health/apply'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'Content-Type': 'application/json',
        'user-agent': 'V1965A(Android/10) (com.axy.zhidian/1.7.3) Weex/0.18.0 1080x2241',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Content-Length': '695'
    }

    content = {
        "location": {"address": address, "code": "1", "lng": lng, "lat": lat},
        "temperature": random_temperature(),
        "health": "是",
        "observation": "否",
        "confirmed": "否",
        "haveCOVIDInPlaceOfAbode": "否",
        "goToHuiBei": "否",
        "contactIllPerson": "否",
        "haveYouEverBeenAbroad": "否",
        "familyPeopleNum": "4",
        "isFamilyHealth": "否",
        "isFamilyStatus": "否",
        "familyPeopleIsAway": "否",
        "hasYourFamilyEverBeenAbroad": "否",
        "leave": "否",
        "isYesterdayMove": "否",
        "admission": "是",
        "help": "否",
        "nowLocation": district
    }

    data = {
        "health": 0,
        "student": 1,
        "templateId": 4,
        "content": str(content)
    }
    template_id, isSubmitted = get_templateID(token)
    print(template_id, isSubmitted)
    time.sleep(3)
    template_url = f'http://zua.zhidiantianxia.cn/api/study/health/mobile/health/template?id={template_id}'
    if not isSubmitted:
        try:
            template_response = session.get(url=template_url, timeout=4)
            print(template_response.json())
        except:
            print('获取模板失败')
    else:
        print("今日已打卡")

    time.sleep(3)
    if not isSubmitted:
        data = json.dumps(data)
        response = session.post(url=url, headers=header, data=data)
        if response.json()['status'] == 1:
            msg = response.json()['msg'] + f'\n当前模板ID为{template_id}'  # 打卡成功
            Push(msg)

        else:
            msg = parse.quote_plus(response.json()['msg'])
            Push(msg)
            print(parse.unquote(msg))
    else:
        print('今天已经打过卡了~')


# 获取每日宿舍签到的signInId模块
def get_signInId(token):
    url = 'http://zua.zhidiantianxia.cn/applets/signin/my'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'user-agent': 'TAS-AN00(Android/5.1.1) (com.axy.zhidian/1.5.5) Weex/0.18.0 720x1280',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    data = {
        'page': '0',
        'size': '10'
    }
    try:
        signInId = session.get(url=url, headers=header, data=data).json()['data']['content'][0]['id']
        return signInId
    except:
        pass


# 22点宿舍签到模块
def sign_in_evening(token):
    url = 'http://zua.zhidiantianxia.cn/applets/signin/sign'
    header = {
        'axy-phone': phone,
        'axy-token': token,
        'Content-Type': 'application/json',
        'user-agent': 'V1965A(Android/10) (com.axy.zhidian/1.7.2) Weex/0.18.0 1080x2241',
        'Host': 'zua.zhidiantianxia.cn',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Content-Length': '146'
    }
    data = {
        "locale": address,
        "lat": lat,
        "lng": lng,
        "signInId": get_signInId(token)
    }
    data = json.dumps(data)
    response = session.post(url=url, headers=header, data=data)
    if response.json()['status'] == 1:
        print("签到成功")
    else:
        print("签到失败")
    msg = parse.quote_plus(response.json()['msg'])
    Push(msg)


if __name__ == "__main__":
    token = login()
    time.sleep(3)
    now_H = int(time.strftime("%H"))
    if flag == 1:
        if 14 <= now_H <= 15:  # 世界协调时间
            sign_in_evening(token)
        else:
            sign_in(token)
    else:
        pass
