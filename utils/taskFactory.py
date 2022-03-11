#!/usr/bin/python
# coding:utf8
from concurrent.futures import *


class TaskFactory:

    def __init__(self):
        self.max_executor = 50
        self.running = 0
        # self.executor = ThreadPoolExecutor(max_workers=self.max_executor)
        self.executor = ProcessPoolExecutor(max_workers=self.max_executor)

    def add_task(self, func, *args, **kw):
        fu = self.executor.submit(func, *args, **kw)
        return fu

    def get_executor_result(self, executor, timeout=100, name="default"):
        try:
            ans = executor.result(timeout=timeout)
            return ans
        except Exception as e:
            print("{},{}".format(name, e))
            return None


task_factory = TaskFactory()
