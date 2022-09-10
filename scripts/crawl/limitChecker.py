"""
Request limit checker for Etherscan and BscScan to avoid
breaching request limit imposed by these platforms when using
their free API.

File is a modification of
https://github.com/StefanosChaliasos/inline-assembly/blob/464892a71e1161e6812bedcd40eba1388157e97a/scripts/etherscan_crawler.py#L20
"""
import time


class LimitChecker:
    def __init__(self, requests_limit=5, time_limit=1, debug=False):
        self.total_requests = 0
        self.requests_limit = requests_limit
        self.time_limit = time_limit
        self.round_req = 0
        self.start_time = None
        self.debug = debug

    def start(self):
        self.start_time = time.time()

    def check(self):
        # if self.round_req == 4:
        #     time.sleep(self.time_limit)
        # self.round_req = 0
        # return
        elapsed_time = time.time() - self.start_time
        if self.round_req >= self.requests_limit and elapsed_time <= self.time_limit:
            if self.debug:
                print(f"Reached the request limit -- sleep {self.time_limit} sec")
            time.sleep(self.time_limit)
            self.start_time = time.time()
            self.round_req = 0
        elif elapsed_time >= self.time_limit:
            self.start_time = time.time()
        if self.round_req == self.requests_limit:
            self.round_req = 0
        self.round_req += 1
        self.total_requests += 1
