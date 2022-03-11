#!usr/bin/python
# -*- coding: utf-8 -*-

import os
import json

dict_path = os.getcwd() + "/data/"

class TrieTree(object):
    def __init__(self):
        json_obj = self._load_from_txt()

        self.root = [False, set(), {}]
        self.load_dict(json_obj)

    def _load_from_txt(self):
        # txt_ls = ["book", "color", "film", "film_genre", "food", "food_material", "instrument", "music", "music_genre",
        #           "news_genre", "common_name", "sport", "tv", "occupation", "city", "country", "nationality", "talent",
        #           "actor", "singer", "sportsman", "tv_genre", "drink", "wine", "electronics", "quantifier",
        #           "pass_status", "domestic_universities", "fruit", "body", "city_oversea", "city", "animal_pets",
        #           "object_goods",
        #           "fail_status", "subtype", "friend", "POI", "indisposition"]
        txt_ls = ['node_name', 'property_name']
        json_obj = {}
        for dic in txt_ls:
            key, ls = self._read_from_txt(dic, dict_path + dic + ".txt")
            json_obj[key] = ls
        return json_obj

    def _read_from_txt(self, key, file_path):
        s = set()
        with open(file_path, "r") as infile:
            for line in infile:
                try:
                    s.add(line.strip().decode("utf-8"))
                except UnicodeDecodeError:
                    print(file_path, line, type(line))
        return (key, list(s))

    def load_dict(self, json_obj):
        temp = self.root
        for key in json_obj:
            for word in json_obj[key]:
                for char in word:
                    temp = temp[2].setdefault(char, [False, set(), {}])
                temp[0] = True  # 注意: 当匹配到某一级节点的dict中的key时， 此时是否有词匹配要看该key对应的节点第一个元素是否为True，
                # 词匹配的label也要从该key对应的节点（及下一层节点）去看
                temp[1].add(key)  # one match of word could correspond to multiple keys
                temp = self.root


    def add(self, dictionary):  # dic as defined in function_word.json
        """
        trie树在第一次初始化以后，可以继续调用这个方法来往trie树里面加入更多的条目
        :param dictionary: {"key1":[u"word1", u"word2"], "key2":[u"word3", u"word4"], ...}, sorry for the mix of unicode and bytecode str, will fix this in a later optimization
        :return: None, in-place update of trie tree in memory
        """
        self.load_dict(dictionary)

    # def trie_match(self, sent):
    #     """
    #     :param sent: The input unicode sentence string which is not segmented
    #     :return:
    #     """
    #     kwd_dict = {}
    #     idx = 0
    #     while idx < len(sent):
    #         word = u""
    #         word_candidate = u""
    #         temp = self.root
    #         if sent[idx] in temp[2]:  # if current char is in dict
    #             for char in sent[idx:]: # iterate over the chars in sent
    #                 if char in temp[2]: # if current char is in dict
    #                     temp = temp[2][char] # update temp to the next node in trie tree
    #                     word += char # store the matched sequence of chars so far
    #                 else:  # char not in temp[2], so the matching char sequence is broken
    #                     break
    #                 if temp[0]:  # only find one longest match
    #                     word_candidate = word  # word_candidate could be updated several times during the search process
    #                     detail = temp[1]  # detail could be updated several times during the search process
    #             if not word_candidate:  # not match found
    #                 idx += 1  # did not find match in trie tree, proceed to the next char
    #             else:  # match found
    #                 idx += len(word_candidate)
    #                 for key in detail:
    #                     if key not in kwd_dict:  # detail, word_candidate are both unicode string
    #                         kwd_dict[key] = [word_candidate]
    #                     else:
    #                         kwd_dict[key].append(word_candidate)
    #         else:  # first_char not in the dic temp[2]
    #             idx += 1  # proceed to the next char.
    #     return kwd_dict


    def trie_match(self, sent):
        """
        Find all matches in the sent against the trie tree
        :param sent: The input unicode sentence string which is not segmented 
        :return: {"key1":[u"match1", u"match2"], "key2":[u"match3", u"match4"], ...}
        """
        if isinstance(sent, str):
            sent = sent.decode("utf-8")

        kwd_dict = {}
        idx = 0
        while idx < len(sent):  # idx goes from 0 to len(sent) - 1 through each iteration
            word = u""
            word_candidates = []
            temp = self.root
            if sent[idx] in temp[2]:  # if current char is in dict
                for char in sent[idx:]:  # iterate over the chars in sent
                    if char in temp[2]:  # if current char is in dict
                        temp = temp[2][char]  # update temp to the next node in trie tree, 注意=左边的temp是下一层的node
                        word += char  # store the matched sequence of chars so far
                    else:  # char not in temp[2], so the matching char sequence is broken
                        break  # break out from the for loop
                    if temp[0]:
                        word_candidates.append([word, temp[1]])  # word_candidates hold all word matches
                if not word_candidates:  # not match found
                    idx += 1  # did not find match in trie tree, proceed to the next char
                else:  # match found
                    idx += len(sorted(word_candidates, key=lambda e: len(e[0]), reverse=False)[0][
                                   0])  # 下一次scan的开始位置为当次scan的开始位置加上当次scan匹配到的最长词的长度
                    for word, keys in word_candidates:  # 将结果写入kwd_dict， 因为每次while loop开始的时候， word_candidates会被置空
                        for key in keys:
                            if key not in kwd_dict:
                                kwd_dict[key] = [word]
                            else:
                                if word not in kwd_dict[key]:
                                    kwd_dict[key].append(word)
            else:  # current char not in the dic temp[2]
                idx += 1  # proceed to the next char.
        # 每个key对应的list按照元素的字符个数从大到小排序，方便关系抽取消歧过程直接提取最长匹配的arg2
        self._sort_dict_vals(kwd_dict)
        return kwd_dict

    def _sort_dict_vals(self, dic):
        """
        dict中每个key对应的list按照元素的字符个数从大到小排序, in-place sort
        :param dic: 
        :return: None
        """
        for key in dic.keys():
            dic[key].sort(key=lambda e: len(e), reverse=True)


trie_tree = TrieTree()

if __name__ == "__main__":

    # ret = trie_tree.get_resolution_type()
    # print(ret[u'狗尾草'])
    # print(ret[u'狗尾草'][0])
    # print(ret[u'狗尾草'][1])
    # print(ret[u'狗尾草'][2])

    # sentence = u"你会不会你会你能你会不会怎么你喜不喜欢吗是谁啥怎么样是什么会讲吗会说吗怎样的关系关系如何好看吗狗尾草吗?"

    res = TrieTree().trie_match(u"我是否有比较偏爱的歌手")
    # for key in res:
    #     print key, "=", res[key], type(key)
    #
    #     print ""
    # print "done"
