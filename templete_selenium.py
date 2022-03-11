# -*- coding: utf-8 -*-
import time
from util.user_agent import ua
import random
import re
import traceback
import requests
from lxml import etree
import time
from tqdm import tqdm
from selenium import webdriver
import json
 
def load():
    with open('yuemei.json', encoding='utf-8') as f:
        return json.load(f)

def write_to_json(ips):
    with open('yuemei.json', 'w', encoding='utf-8') as f:
        json.dump(ips, f, indent=4, ensure_ascii=False)

    
def detail(url):
    detail_dict = {}
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument(random.choice(ua))
    option.add_argument('--no-sandbox')
    option.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=option)
    driver.get(url)
    name = driver.find_element_by_xpath('/html/body/div[9]/div/h1').text  # 名称： 玻尿酸丰耳垂
    brief_introduction = driver.find_element_by_xpath('/html/body/div[9]/div/p').text  # 简介
    safe_degree = driver.find_element_by_xpath('/html/body/div[9]/div/div/div[1]/span[2]/i').get_attribute(
        'style')  # 安全度
    complex_degree = driver.find_element_by_xpath('/html/body/div[9]/div/div/div[2]/span[2]/i').get_attribute(
        'style')  # 复杂度
    pain_degree = driver.find_element_by_xpath('/html/body/div[9]/div/div/div[2]/span[2]/i').get_attribute(
        'style')  # 疼痛度
    operation_means = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[1]/i[2]').text  # 操作方式
    operation_duration = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[2]/i[2]').text  # 操作时长
    keep_duration = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[3]/i[2]').text  # 维持时间
    anesthesia_type = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[4]/i[2]').text  # 麻醉方式
    pain = driver.find_element_by_xpath('/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[5]/i[2]').text  # 疼痛感
    be_in_hospital = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[6]/i[2]').text  # 是否住院
    recover_duration = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[3]/i[2]').text  # 恢复时间
    operation_times = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[8]/i[2]').text  # 治疗次数
    operators = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[9]/i[2]').text  # 操作人员资质
    to_hospital_times = driver.find_element_by_xpath(
        '/html/body/div[10]/div[1]/div[1]/div[1]/div[1]/span[10]/i[2]').text  # 到院次数

    # save as dict
    detail_dict['name'] = name
    detail_dict['brief_introduction'] = brief_introduction
    detail_dict['safe_degree'] = safe_degree
    detail_dict['complex_degree'] = complex_degree
    detail_dict['pain_degree'] = pain_degree
    detail_dict['operation_means'] = operation_means
    detail_dict['operation_duration'] = operation_duration
    detail_dict['anesthesia_type'] = anesthesia_type
    detail_dict['pain'] = pain
    detail_dict['be_in_hospital'] = be_in_hospital
    detail_dict['recover_duration'] = recover_duration
    detail_dict['operation_times'] = operation_times
    detail_dict['operators'] = operators
    detail_dict['to_hospital_times'] = to_hospital_times
    return detail_dict
    
    
def overall(url, continue_run):
    if continue_run:
        root_dict = load()
    else:
        root_dict = {}
    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    option.add_argument(random.choice(ua))
    option.add_argument('--no-sandbox')
    option.add_argument('--headless')
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=option)
    driver.get(url)
    root_table = driver.find_element_by_xpath('/html/body/div[8]/div[2]/ul')
    children = root_table.find_elements_by_xpath("./*")  # 获得所有子节点
    for r_node in children:
        first_layer = r_node.find_element_by_xpath('./a/div/div[2]').text  # 玻尿酸
        root_dict[first_layer] = {}
        second_table = r_node.find_elements_by_xpath('./div/*')
        for s_node in second_table:
            second_layer = s_node.find_element_by_xpath('./div[1]/a').text  # 填充塑形
            root_dict[first_layer][second_layer] = {}
            third_table = s_node.find_elements_by_xpath('./div[2]/*')
            for t_node in third_table:
                try:
                    url = t_node.get_attribute("href")
                    third_layer = t_node.find_element_by_xpath('./span/i').text  # 玻尿酸耳垂
                    root_dict[first_layer][second_layer][third_layer] = detail(url)
                except:
                    third_layer = ''
                    url = ''
                z = 0
                while z <= 10:
                    try:
                        ######采集代码##########
                        d = detail(url)
                        print(third_layer + '——————————正常运行——————————')
                        break
                    except :
                        z += 1
                        time.sleep(0.2)
                        d = ''
                root_dict[first_layer][second_layer][third_layer] = d
                write_to_json(root_dict)
                time.sleep(0.2)
            
if __name__ == '__main__':
    url = 'https://www.yuemei.com/parts.html'  # 项目大全页
    continue_run = 0
    overall(url, continue_run)  # 项目大全页 解析
