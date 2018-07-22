# -*- coding: utf-8 -*-
"""
Created on Sun Jul 22 11:07:23 2018

@author: Administrator
"""
from selenium import webdriver
import time
import json

qq_number = '********'
password = '********'

login_url = 'https://i.qq.com/'
driver = webdriver.Chrome()
driver.get(login_url)
#进入登陆的ifame
driver.switch_to_frame('login_frame')
driver.find_element_by_xpath('//*[@id="switcher_plogin"]').click()
time.sleep(1)
driver.find_element_by_xpath('//*[@id="u"]').send_keys(qq_number)
driver.find_element_by_xpath('//*[@id="p"]').send_keys(password)
time.sleep(1)
driver.find_element_by_xpath('//*[@id="login_button"]').click()
time.sleep(1)
cookie_list = driver.get_cookies()
cookie_dict = {}
for cookie in cookie_list:
    if 'name' in cookie and 'value' in cookie:
        cookie_dict[cookie['name']] = cookie['value']

with open('cookie_dict.txt', 'w') as f:
    json.dump(cookie_dict, f)
