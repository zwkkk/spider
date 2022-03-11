# -*- coding: utf-8 -*-
import sys
import re
from util.ltp_handler import ltp_seg_handler
reload(sys)
sys.setdefaultencoding('utf-8')

# load stopwords
stopwords_set = set()
with open('data/stopwords.txt', 'r') as f:
    lines_list = f.readlines()
    for line in lines_list:
        stopwords_set.add(line.strip().decode('utf-8'))

punc_ch = u"[！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠《》｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…﹏]"
punc_en = u"[!\"#$%&\'()*+,;<=>?@[\\]^_`{|}~]"
punc_ch_pattern = re.compile(punc_ch)
punc_en_pattern = re.compile(punc_en)


def ltp_cut(sent):
    seg_list = ltp_seg_handler.segment(sent)

    fin_list = []
    for word in seg_list:
        if word in stopwords_set or word in {'', ' '}:
            continue
        else:
            fin_list.append(word)

    return " ".join(fin_list)


if __name__ == '__main__':
    # word = '的'
    # print(type(word))
    # if word in stopwords_set:
    #     print(True)
    print(ltp_cut('百度和阿里巴巴，相比谁的员工数更多'))
