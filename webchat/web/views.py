# Create your views here.
from django.shortcuts import render
from django.shortcuts import HttpResponse
import requests
import re
import time
import json
import copy
from bs4 import BeautifulSoup
VERIFY_TIME =None
verifi_uuid =None
LOGIN_COOKIE_DICT = {}
TICKET_COOKIE_DICT= {}
TICKET_DATA_DICT = {}
USER_INIT_DATA = {}
PAYLOAD_DATA = {}
TIPS=1
def webchat(request):
    #获取验证码的url
    verificode_url = "https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_={0}"
    verifi_reponse =requests.get(url=verificode_url)
    #print(verifi_reponse.text)
    #时间戳
    global VERIFY_TIME
    VERIFY_TIME = str(time.time())
    verificode_url.format(VERIFY_TIME)
    global verifi_uuid
    #匹配二维码另一个值
    verifi_uuid=re.findall('uuid = "(.*)";',verifi_reponse.text)[0]
    return render(request,"webchat.html",{"code":verifi_uuid,
                                          })
def long_pooling(request):
    """二维码长轮询获取登陆"""
    """
    1、status=408什么也没有操作
    2、status=201微信扫了码但是没有操作
    3、status=200代表扫码成功并确认登陆
    """
    #返回的json状态和数据
    ret = {"status":408,"data":None}
    #二维码长轮询url
    try:
        #TIPS=0是没有过于频繁的轮询.刚开始是为1
        global TIPS
        #请求的地址，uuid=verifi_uuid,后面那个值是随机生产时间戳
        base_pooling_url = "https://login.wx.qq.com/cgi-bin/mmwebwx-bin/login?loginicon=true&uuid={0}&tip={1}&r=-1322669031&={2}"
        pooling_url= base_pooling_url.format(verifi_uuid,TIPS,VERIFY_TIME)
        reponse_login = requests.get(url=pooling_url)
        #print("pooling_reponse.text",pooling_reponse.text)
        #扫码一直没有点击登陆，状态码是201,获取返回头像数据
        if "window.code=201" in reponse_login.text:
            #获取头像图片地址
            TIPS = 0
            #获取图片地址
            avatar = re.findall("userAvatar = '(.*)';",reponse_login.text)[0]
            #print("avatar",avatar)
            #更新状态和内容
            ret["status"] = 201
            ret["data"] = avatar
        #print("reponse_login",reponse_login.text)
        elif "window.code=200" in reponse_login.text:
            #登陆时候获取的cookies
            LOGIN_COOKIE_DICT.update(reponse_login.cookies.get_dict())
            #登陆成功返回一个重定向地址，这个地址请求可以获取用户信息ticket
            redirect_uri = re.findall('redirect_uri="(.*)";',reponse_login.text)[0]
            redirect_uri+="&fun=new&version=v2&lang=zh_CN"
            #print("redirect_uri",redirect_uri)

            #获取ticket和添加ticket的cookie
            reponse_ticket = requests.get(url=redirect_uri,cookies=LOGIN_COOKIE_DICT)
            TICKET_COOKIE_DICT.update(reponse_ticket.cookies.get_dict())
            #print("reponse_ticket:",reponse_ticket.text)
            #找出ticket里的值
            soup=BeautifulSoup(reponse_ticket.text,"html.parser")
            for tag in soup.find():
                #print(tag.name,tag.string)
                #把数据存入到dict中，为了下次请求的时候使用
                TICKET_DATA_DICT[tag.name]=tag.string
            #print("TICKET_DATA_DICT",TICKET_DATA_DICT)
            ret["status"] = 200
    except Exception as e:
        print(e)
    return HttpResponse(json.dumps(ret))

def index(request):
    """微信登陆的页面初始化,获取用户的基本信息"""
    #user_init_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?pass_ticket=%s&r=%s" %(TICKET_DATA_DICT["pass_ticket"],int(time.time()))
    user_init_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=-631178899"
    global PAYLOAD_DATA
    PAYLOAD_DATA = {
        "BaseRequest":{
            "DeviceID":"e379444626462097",
            "Sid":TICKET_DATA_DICT["wxsid"],
            "Skey":TICKET_DATA_DICT["skey"],
            "Uin":TICKET_DATA_DICT["wxuin"]}
    }
    cookie_all = {}
    #因为不知道用哪个cookie所以上面两个都给加上了
    cookie_all.update(LOGIN_COOKIE_DICT)
    cookie_all.update(TICKET_COOKIE_DICT)
    #返回的内容是用户的信息
    reponse_init=requests.post(url=user_init_url,json=PAYLOAD_DATA,cookies=cookie_all)
    reponse_init.encoding="utf-8"
    #用户信息转成dict
    reponse_init_data = json.loads(reponse_init.text)
    #print("reponse_init",reponse_init.text)
    # print("------------------------------------------")
    # for k,v in reponse_init_data.items():
    #     print(k,v)
    #把数据都保留在这个全局变量中
    USER_INIT_DATA.update(reponse_init_data)
    #print("USER_INIT_DATA:",USER_INIT_DATA)


    return render(request,"index.html",{"data":reponse_init_data,})

def contact_list(request):
    """
    用户所有联系人列表
    :param request:
    :return:
    """
    contact_list_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact?r={0}&seq=0&skey={1}"
    contact_list_url = contact_list_url.format(int(time.time()),TICKET_DATA_DICT["skey"])
    cookie_all = {}
    # 因为不知道用哪个cookie所以上面两个都给加上了
    cookie_all.update(LOGIN_COOKIE_DICT)
    cookie_all.update(TICKET_COOKIE_DICT)
    reponse_contact = requests.get(url=contact_list_url,cookies=cookie_all)
    reponse_contact.encoding="utf-8"
    contact_data_dict = json.loads(reponse_contact.text)
    # for k,v in contact_data_dict.items():
    #     print(k)

    return render(request,"contact.html",{"data":contact_data_dict,})

def send_message(request):
    """
    发送消息
    :param request:
    :return:
    """
    to_user_id = request.POST.get("user_id")
    send_msg = request.POST.get("user_msg")
    from_user_id=USER_INIT_DATA["User"]["UserName"]
    send_message_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg?lang=zh_CN&pass_ticket={0}"
    send_message_url = send_message_url.format(TICKET_DATA_DICT["pass_ticket"])
    payload_data = copy.deepcopy(PAYLOAD_DATA)
    payload_data["Msg"]={
        "ClientMsgId":int(time.time()),
        "Content":"%(content)s",
        "FromUserName":from_user_id,
        "LocalID":int(time.time()),
        "ToUserName":to_user_id,
        "Type":1,
    }
    payload_data["Scene"]=int(time.time())
    #字符串
    payload_data = json.dumps(payload_data)
    #进行格式化
    payload_data = payload_data %{"content":send_msg}
    #转换成字节
    payload_data_bytes = bytes(payload_data,encoding="utf-8")
    cookie_all = {}
    # 因为不知道用哪个cookie所以上面两个都给加上了
    cookie_all.update(LOGIN_COOKIE_DICT)
    cookie_all.update(TICKET_COOKIE_DICT)
    headers ={"Content-Type":"application/json"}
    reponse_message = requests.post(url=send_message_url,data=payload_data_bytes,headers=headers,cookies=cookie_all)
    return HttpResponse("ok")

def get_message(request):
    """
    获取消息
    :param request:
    :return:
    """
    #确认是否有信息url
    sync_check_url = "https://webpush.wx2.qq.com/cgi-bin/mmwebwx-bin/synccheck"
    sysc_data_list = []
    for item in USER_INIT_DATA["SyncKey"]["List"]:
        temp = "%s_%s"%(item["Key"],item["Val"])
        sysc_data_list.append(temp)

    sysc_data = "|".join(sysc_data_list)
    param_data = {
        "r":int(time.time()),
        "skey":TICKET_DATA_DICT["skey"],
        "sid":TICKET_DATA_DICT["wxsid"],
        "uin":TICKET_DATA_DICT["wxuin"],
        "deviceid":int(time.time()),
        "synckey":sysc_data
    }
    cookie_all = {}
    # 因为不知道用哪个cookie所以上面两个都给加上了
    cookie_all.update(LOGIN_COOKIE_DICT)
    cookie_all.update(TICKET_COOKIE_DICT)
    reponse_check_message = requests.get(url=sync_check_url,params=param_data,cookies=cookie_all)
   # print("reponse_check_message_text",reponse_check_message.text)
    #有selector:"2"代表有消息
    #接收消息
    if 'selector:"2"' in reponse_check_message.text:
        fetch_msg_url = "https://wx2.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid={0}&skey={1}&lang=zh_CN&pass_ticket={2}"
        fetch_msg_url = fetch_msg_url.format(TICKET_DATA_DICT["wxsid"],TICKET_DATA_DICT["skey"],TICKET_DATA_DICT["pass_ticket"])
        form_data ={
            "BaseRequest":{
                "DeviceID":int(time.time()),
                "Sid":TICKET_DATA_DICT["wxsid"],
                "Skey":TICKET_DATA_DICT["skey"],
                "Uin":TICKET_DATA_DICT["wxuin"]
            },
            "SyncKey":USER_INIT_DATA["SyncKey"],
            "rr":int(time.time())
        }
        response_fetch_msg = requests.post(url=fetch_msg_url,json=form_data)
        response_fetch_msg.encoding="utf-8"
        res_fetch_msg_dict = json.loads(response_fetch_msg.text)
        #返回的值更新了SyncKey
        USER_INIT_DATA["SyncKey"] = res_fetch_msg_dict["SyncKey"]
        #AddMsgList消息列表
        #Content消息的内容
        #FromUserName谁发来的
        #ToUserName发给谁
        for item in res_fetch_msg_dict["AddMsgList"]:
            print(item["Content"],"::::",item["FromUserName"],"----->",item["ToUserName"],)
        #print("res_fetch_msg_dict:",res_fetch_msg_dict)
    return HttpResponse("OK")


