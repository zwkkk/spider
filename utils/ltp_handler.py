#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
from pyltp import Segmentor
from pyltp import CustomizedSegmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
from pyltp import SementicRoleLabeller


class LTPHander():

    # 详细的ltp标签说明文档： https://ltp.readthedocs.io/zh_CN/latest/appendix.html
    # 模型下载网盘地址：随便选一个版本下载即可，不需要全部下载
    # https://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569&errno=0&errmsg=Auth%20Login%20Sucess&&bduss=&ssnerror=0&traceid=#list/path=%2Fltp-models

    def __init__(self, ltp_path, task_type='seg', seg_dict=''):
        '''
        task_type可选：
        - seg       分词
        - postag    词性标注
        - ner       命名实体识别
        - parser    依存分析
        - semantic  语义角色标注

        :param ltp_path: ltp模型存放的路径
        :param task_type: 任务的类型
        '''
        self.LTP_DATA_DIR = ltp_path
        # 分词，默认加载
        self._cws_model_path = os.path.join(self.LTP_DATA_DIR,'cws.model') # 分词模型路径，模型名称`cws.model`
        if seg_dict: # 引入用户字典
            self._segmentor = CustomizedSegmentor()
            self._segmentor.load_with_lexicon(self._cws_model_path, self._cws_model_path, seg_dict) # 加载模型
        else:
            self._segmentor = Segmentor()
            self._segmentor.load(self._cws_model_path)

        # 词性标注，默认加载
        self._pos_model_path = os.path.join(self.LTP_DATA_DIR, 'pos.model') # 词性标注模型路径，模型名称为`pos.model`
        self._postagger = Postagger()
        self._postagger.load(self._pos_model_path)
        # NER，只有调用ner时加载
        self._ner_model_path = os.path.join(self.LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`ner.model`
        self._recognizer = NamedEntityRecognizer() # 初始化实例
        if task_type == 'ner': self._recognizer.load(self._ner_model_path)
        # 依存分析，paser和semantic时加载
        self._par_model_path = os.path.join(self.LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
        self._parser = Parser() # 初始化实例
        if task_type == 'parser' or task_type == 'semantic': self._parser.load(self._par_model_path)
        # 语义角色标注，调用semantic时才加载
        self._srl_model_path = os.path.join(self.LTP_DATA_DIR, 'pisrl.model')  # 语义角色标注模型目录路径，模型名称为`pisrl.model`
        self._labeller = SementicRoleLabeller() # 初始化实例
        if task_type == 'semantic': self._labeller.load(self._srl_model_path)

    def __del__(self):
        self._segmentor.release()
        self._postagger.release()
        self._recognizer.release()
        self._parser.release()
        self._labeller.release()

    def segment(self, sent):
        words = self._segmentor.segment(sent)
        return list(words)

    def pos_tag(self, sent):
        words = self.segment(sent)
        postags = self._postagger.postag(words)
        return list(postags)

    def ner(self, sent):
        '''
        识别三种类型的命名实体：
        - Nh	人名
        - Ni	机构名
        - Ns	地名

        :param sent:
        :return: [(2, 3, '中国电信', 'Ni')]
                 [(开始index, 结束index, NE子串1, NE类型), (开始index, 结束index, NE子串2, NE类型), ……]
        '''
        words = self.segment(sent)
        postags = self.pos_tag(sent)
        netags = self._recognizer.recognize(words, postags)
        res = []

        for i in range(len(netags)):
            if netags[i] == 'O' or netags[i].startswith('I'):
                continue
            if netags[i].startswith('S'):
                ne_start = i
                ne_end = i
                ne_name = netags[i].split('-')[1]
                ne_words = ''.join(words[ne_start:ne_end+1])
                res.append((ne_start, ne_end, ne_words, ne_name))
            if netags[i].startswith('B'):
                ne_start = i
            if netags[i].startswith('E'):
                ne_end = i
                ne_name = netags[i].split('-')[1]
                ne_words = ''.join(words[ne_start:ne_end+1])
                res.append((ne_start, ne_end, ne_words, ne_name))

        # return list(netags)
        return res

    def parser(self, sent):
        '''
        Root节点索引为0，第一个词开始索引为1、2、3……
        arc.relation 表示依存弧的关系。
        arc.head 表示依存弧的父节点词的索引，

        :param sent:
        :return: [(arc.head，当前节点逻辑位置, 当前节点词, arc.relation), (arc.head，当前节点逻辑位置, 当前节点词, arc.relation), ……]
        '''
        words = self.segment(sent)
        postags = self.pos_tag(sent)
        arcs = self._parser.parse(words, postags)  # 句法分析
        # 打印结果
        # print "\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs)
        parser_words = ['ROOT'] + words

        res = [(arc.head, parser_words[arc.head], idx+1, parser_words[idx+1], arc.relation) for idx, arc in enumerate(arcs)]
        # res = [(arc.head, idx+1, arc.relation) for idx, arc in enumerate(arcs)]
        return res

    def semantic_labeller(self, sent):
        '''
        第一个词开始的索引依次为0、1、2……
        role.index 代表谓词的索引，
        role.arguments 代表关于该谓词的若干语义角色。
        arg.name 表示语义角色类型
        arg.range.start 表示该语义角色起始词位置的索引，
        arg.range.end 表示该语义角色结束词位置的索引。

        :param sent:
        :return: [(谓词1下标, 谓词1, [(arg.name, arg.range.start, arg.range.end, 对应字符串), (arg.name, arg.range.start, arg.range.end, 对应字符串), ……]),
                  (谓词2下标, 谓词2, [(arg.name, arg.range.start, arg.range.end, 对应字符串), (arg.name, arg.range.start, arg.range.end, 对应字符串), ……]),
                  (……, ……, ……)]
        '''
        words = self.segment(sent)
        postags = self.pos_tag(sent)
        arcs = self._parser.parse(words, postags)  # 句法分析
        roles = self._labeller.label(words, postags, arcs)  # 语义角色标注

        res = []
        for role in roles:
            args = [(arg.name, arg.range.start, arg.range.end, ''.join(words[arg.range.start:arg.range.end+1])) for arg in role.arguments]
            res.append((role.index, words[role.index], args))

        # 打印结果
        # for role in roles:
        #     print(role.index, " ".join(
        #         ["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments]))

        return res

# 207
# ltp_path = '/data/zhang_kai/project/ltp_models'
# 2080
# ltp_path = '/home/data/zhang_kai/ltp_models'
# k40
ltp_path = '/data/zhang_kai/data/ltp_models'

ltp_seg_handler = LTPHander(ltp_path, task_type='seg')
ltp_tag_handler = LTPHander(ltp_path, task_type='postag')

if __name__ == '__main__':
    sent = '饺子的做法'
    # sent = '周杰伦2008年参观了腾讯总部'
    # sent = '苹果的公司地址是加利福尼亚州吗'
    noun_candidate_set = set()
    seg_rst = ltp_seg_handler.segment(sent)
    tag_rst = ltp_tag_handler.pos_tag(sent)
    for i in range(len(seg_rst)):
        if tag_rst[i][0] == 'n':
            noun_candidate_set.add(seg_rst[i])
        print('{} : {}'.format(seg_rst[i], tag_rst[i]))
    print(noun_candidate_set)

    # ltp = LTPHander(ltp_path, task_type='seg', seg_dict='../data/user_seg_dict.txt')
    # print(ltp.segment(sent))
    #
    # ltp = LTPHander(ltp_path, task_type='postag',seg_dict='../data/user_seg_dict.txt')
    # print(ltp.pos_tag(sent))
    #
    # ltp = LTPHander(ltp_path, task_type='ner')
    # print(ltp.ner(sent))
    #
    # ltp = LTPHander(ltp_path, task_type='parser')
    # print(ltp.parser(sent))
    #
    # ltp = LTPHander(ltp_path, task_type='semantic')
    # print(ltp.semantic_labeller(sent))

