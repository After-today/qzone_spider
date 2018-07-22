# -*- coding: utf-8 -*-
"""
Created on Sat Jul 21 14:25:58 2018

@author: Administrator
"""
import requests
import time
import urllib
import pymysql
import json
import re
import threadpool

def get_g_tk():
    p_skey = cookie_dict['p_skey']
    h = 5381
    for i in p_skey:
        h += (h << 5) + ord(i)
        g_tk = h & 2147483647
    print('g_tk', g_tk)
    return g_tk
    
def get_friends_uin(g_tk):
    yurl = 'https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?'
    data = {
            'uin': 1525943131,
            'do': 1,
            'g_tk': g_tk
            }
    url = yurl + urllib.parse.urlencode(data)
    res=requests.get(url, headers = headers, cookies = cookie_dict)
    r = res.text.split('(')[1].split(')')[0]
    friends_list=json.loads(r)['data']['items_list']
    friends_uin=[]
    for f in friends_list:
        friends_uin.append(f['uin'])
    return friends_uin
    
def get_dynamic(uin):
    print(uin)
    conn = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db='my_sql', charset='utf8mb4')
    cursor = conn.cursor()
    yurl = 'https://user.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?'
    pos = 0
    while True:
        data = {
                'uin': uin,
                'pos':pos,
                'num':20,
                'replynum':100,
                'callback':'_preloadCallback',
                'code_version':1,
                'format':'jsonp',
                'need_private_comment':1,
                'g_tk': g_tk
                }
        url = yurl + urllib.parse.urlencode(data)
        res=requests.get(url,headers = headers, cookies = cookie_dict)
        r = re.findall('\((.*)\)',res.text)[0]
        dynamic = json.loads(r)
        pos += 20
        if 'msglist' in dynamic:
            msglist=dynamic['msglist']
            if msglist:
                for m in msglist:
                    name=m['name']
                    content=pymysql.escape_string(m['content'])
                    created_time=m['created_time']
                    standard_time=time.localtime(created_time)
                    standard_time = time.strftime("%Y-%m-%d %H:%M:%S", standard_time)
                    sql = "insert into qzone_spider(qq_number, name, created_time, content) values (%d, '%s', '%s', '%s')"
                    data = (uin, name, standard_time, content)
                    try:
                        cursor.execute(sql % data)
                    except Exception as e:
                        print(e)
                    conn.commit()
            else:
                print("没有更多的说说了╮(︶﹏︶)╭")
                break
        else:
            print("好友空间没有对我开放(｡･ˇ_ˇ･｡:)")
            access_denied.append(uin)
            break

            
if __name__ == '__main__':
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    
    with open('cookie_dict.txt', 'r') as f:
        cookie_dict=json.load(f)
        
    g_tk = get_g_tk()
    friends_uin = get_friends_uin(g_tk)
    
    #拒绝访问！！小本本记下来！！
    access_denied=[]

    #设置线程池容量，创建线程池
    pool_size = 10
    pool = threadpool.ThreadPool(pool_size)
    #创建工作请求
    reqs = threadpool.makeRequests(get_dynamic, friends_uin)
    #将工作请求放入队列
    [pool.putRequest(req) for req in reqs]
    #for req in requests:
    #    pool.putRequest(req)
    pool.wait()
    with open('access_denied.txt', 'w') as f:
        for a in access_denied:
            f.write(str(a)+'\n')
