#!/usr/bin/env python
# -*- coding:utf8 -*-

import jieba


class JiebaUtil:

    def __init__(self):
        self.jieba_cut("分词测试")

    def jieba_cut(self, sentence, type=1):
        seg_list = []

        if type == 1:
            # 精确模式，默认
            seg_list = jieba.cut(sentence, cut_all=False)
        elif type == 2:
            # 全模式
            seg_list = jieba.cut(sentence, cut_all=True)
        elif type == 3:
            # 搜索引擎模式
            seg_list = jieba.cut_for_search(sentence)
        else:
            print ('cut parameter type out of range')

        return " ".join(seg_list)

jieba_util = JiebaUtil()

if __name__ == '__main__':
    print(jieba_util.jieba_cut('上海今天的天气如何'))
