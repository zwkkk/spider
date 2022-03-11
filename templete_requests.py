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
import json

# Opening JSON file
def load_file():
    with open('save.json', encoding='utf-8') as json_file:
        root_dict = json.load(json_file)
        return root_dict

def write_to_json(ips):
    with open('save.json', 'w', encoding='utf-8') as f:
        json.dump(ips, f, indent=4, ensure_ascii=False)
        
def detail(url):
    url = 'https://www.3ua.cn'+ url
    detail_id = '/'.join(url.split('/')[-2:])
    header = {"User-Agent": random.choice(ua).split('=')[-1][1:-1]}
    res = requests.get(url, headers=header)
    html = etree.HTML(res.text)
    
    detail_dict = {}

    name = html.xpath('//*[@id="/{}"]/h1/text()'.format(detail_id))[0] #项目名称：双眼皮
    professional_name = html.xpath('//*[@id="/{}"]/i[1]/em/text()'.format(detail_id))[0] # 专业名称：微创重睑术
    aka = html.xpath('//*[@id="/{}"]/i[2]/em/text()'.format(detail_id))[0] # 别名：韩式重睑术、韩式定点双眼皮、定点双眼皮
    brief_introduction = html.xpath('/html/body/div[4]/div/div[1]/div[1]/p/text()')[0] # 简介：
    # 手术
    tech_means = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[1]/dd/p[1]/i/text()')[0] # 技术手段：手术，一级手术
    cure = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[1]/dd/p[2]/i/text()')[0] # 疗程：一次手术
    #治疗
    suitable_population = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[2]/dd/p[2]/i/text()')[0] # 适宜人群：
    try:
        effect_lasts = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[2]/dd/p[3]/i/text()')[0] # 效果持续
    except:
        effect_lasts = ''
    length_of_treatment = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[2]/dd/p[4]/i/text()')[0] # 治疗时长
    anesthetic_mode = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[2]/dd/p[5]/i/text()')[0] # 麻醉方式
    # 康复
    take_out_time = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/dd/p[1]/i/text()')[0] # 拆线时间
    be_in_hospital = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/dd/p[2]/i/text()')[0] # 是否住院
    postoperative_rest = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/dd/p[3]/i/text()')[0] # 术后休息

    # 注意事项
    attention = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/div[1]/div[2]')[0]
    content = []
    for node in attention:
        txt = node.xpath('text()')[0].strip()
        content.append(txt)
    content = '\n'.join(content)
    # 优点 / 缺点
    pros_content = []
    cons_content = []
    pros = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/div[2]/div[1]')[0] # 优点
    for node in pros.xpath('p'):
        txt = node.xpath('text()')[0].strip()
        pros_content.append(txt)

    cons = html.xpath('/html/body/div[4]/div/div[1]/div[1]/dl[3]/div[2]/div[2]')[0] # 缺点
    for node in cons.xpath('p'):
        txt = node.xpath('text()')[0].strip()
        cons_content.append(txt)

    pros_content = '\n'.join(pros_content)
    cons_content = '\n'.join(cons_content)

    # save as dict
    detail_dict['name'] = name
    detail_dict['professional_name'] = professional_name
    detail_dict['aka'] = aka
    detail_dict['brief_introduction'] = brief_introduction
    detail_dict['tech_means'] = tech_means
    detail_dict['cure'] = cure
    detail_dict['suitable_population'] = suitable_population
    detail_dict['effect_lasts'] = effect_lasts
    detail_dict['length_of_treatment'] = length_of_treatment
    detail_dict['anesthetic_mode'] = anesthetic_mode
    detail_dict['take_out_time'] = take_out_time
    detail_dict['be_in_hospital'] = be_in_hospital
    detail_dict['postoperative_rest'] = postoperative_rest
    detail_dict['attention'] = content
    detail_dict['pros'] = pros_content
    detail_dict['cons'] = cons_content
    return detail_dict
    
    
def overall(url, continue_run):
    header = {"User-Agent": random.choice(ua).split('=')[-1][1:-1]}
    res = requests.get(url, headers=header)
    html = etree.HTML(res.text)
    root_table = html.xpath('/html/body/div[5]/div/ul')[0]
    if continue_run:
        root_dict = load_file()
    else:
        root_dict = {}
    for r_node in tqdm(root_table):
    #for r_node in tqdm(root_table[4:5]):
        r_layer = r_node.xpath('a/div/div[2]/text()')[0]  # 眼部
        print(r_layer)
        root_dict[r_layer] = {}
        first_table = r_node.xpath('div')[0]
        for f_node in first_table:
            first_layer = f_node.xpath('div[1]/a/text()')[0]  # 割双眼皮
            root_dict[r_layer][first_layer] = {}
            second_table = f_node.xpath('div[2]')[0]
            for s_node in second_table:
                second_layer = s_node.xpath('span/text()')[0]  # 定点双眼皮
                z=0
                while z <= 50000:
                    try:
                        ######采集代码########## 
                        d = detail(s_node.xpath('@href')[0])
                        print('{}: ——————————正常运行——————————'.format(second_layer))
                        break
                    except :
                        z += 1
                        time.sleep(2)
                root_dict[r_layer][first_layer][second_layer] = d
                write_to_json(root_dict)
                time.sleep(5)
            
if __name__ == '__main__':
    url = 'https://www.3ua.cn/parall/'  # 项目大全页
    continue_run = 0
    overall(url, continue_run)  # 项目大全页 解析
