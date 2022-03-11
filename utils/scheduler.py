#!/usr/bin/env python
# -*- coding:utf8 -*-

import Queue
from data_access.redis_dao import redis_dao
from util import picklecompat


# update time time window
time_window = 3600*24*3
hot_entities_interval = 3600

# queue for spider to crawl
QUEUE_MAJOR_KEY = 'baike_queue_major'
QUEUE_SECONDARY_KEY = 'baike_queue_secondary'
QUEUE_THIRD_KEY = 'baike_queue_third'
# spider_queue = Queue.Queue()

# map for detect duplication
DUPE_FILTER_KEY = 'baike_dupe_filter'
# duplicate_map = {}

# map for entity detection
ENTITY_MAP_KEY = 'baike_entity_map'
# entity_map = {}

# mongo log collections name
MONGO_LOG_ENTITY = 'entity'
MONGO_LOG_TEMP = 'temp'


def push_queue_hot(keyword):
    redis_dao.push_fifo_queue('hot_keywords', keyword)

def push_queue_major(keyword):
    redis_dao.push_fifo_queue(QUEUE_MAJOR_KEY, keyword)


def pop_queue_major():
    return redis_dao.pop_fifo_queue(QUEUE_MAJOR_KEY)


def push_queue_secondary(keyword):
    redis_dao.push_fifo_queue(QUEUE_SECONDARY_KEY, keyword)


def pop_queue_secondary():
    return redis_dao.pop_fifo_queue(QUEUE_SECONDARY_KEY)


def push_queue_third(keyword):
    redis_dao.push_fifo_queue(QUEUE_THIRD_KEY, keyword)


def pop_queue_third():
    return redis_dao.pop_fifo_queue(QUEUE_THIRD_KEY)


def set_dupe_map(keyword, date):
    encoded_value = picklecompat.dumps(date)
    redis_dao.set_map(DUPE_FILTER_KEY, {keyword: encoded_value})


def get_dupe_map(keyword):
    data = redis_dao.get_map(DUPE_FILTER_KEY, keyword)
    if data:
        date = picklecompat.loads(data)
        return date


def set_entity_map(keyword, info_tuple):
    encoded_value = picklecompat.dumps(info_tuple)
    redis_dao.set_map(ENTITY_MAP_KEY, {keyword: encoded_value})


def get_entity_map(keyword):
    data = redis_dao.get_map(ENTITY_MAP_KEY, keyword)
    if data:
        info_tuple = picklecompat.loads(data)
        return info_tuple


def get_queue_length(files):
    major = redis_dao.get_queue_len(QUEUE_MAJOR_KEY)
    second = redis_dao.get_queue_len(QUEUE_SECONDARY_KEY)
    third = redis_dao.get_queue_len(QUEUE_THIRD_KEY)
    files.write("*********************************************************************")
    files.write("Major length:" + str(major)+"\n")
    files.write("Secondary length:" + str(second)+"\n")
    files.write("Third length:" + str(third)+"\n")
    files.write("*********************************************************************")
    print("*********************************************************************")
    print("Major length:" + str(major) + "\n")
    print("Secondary length:" + str(second) + "\n")
    print("Third length:" + str(third) + "\n")
    print("*********************************************************************")
    return major, second, third


