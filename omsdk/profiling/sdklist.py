import os
import io
import logging
import threading
import json
import time
from omsdk.sdkconsole import iConsoleRegistry, iConsoleDriver, iConsoleDiscovery
from omsdk.sdkprint import pretty, LogMan
from omsdk.sdkproto import PCONSOLE
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


#logging.basicConfig(level=logging.DEBUG,
#    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


class TT:
    def __init__(self, i):
        self.ipaddr = i

class Results:
    def __init__(self):
        self.npass = 0
        self.nfailed = 0
        self.passlock = threading.Lock()
        self.faillock = threading.Lock()
    def passed(self, obj):
        with self.passlock:
            self.npass = self.npass + 1
    def failed(self, obj):
        with self.faillock:
            self.nfailed = self.nfailed + 1
    def printx(self):
        print("Number Passed: " + str(self.npass))
        print("Number Failed: " + str(self.nfailed))

class ListProc:
    NumThreads=20
    def __init__(self, sd, listfile, creds):
        self.listfile = listfile
        self.myentitylistlock = threading.Lock()
        self.sd = sd
        self.creds = creds
        # SDK Infrastructure
        self.entitylist = []
        self.success = {}
        self.failed = {}
        self.slist = []
        self.simulate = True
        if not os.path.isfile(self.listfile):
            print("Unable to find file")
        else:
            with open(self.listfile, "r") as mylist:
                for line in mylist:
                    self.slist.append(line.rstrip())
            try:
                os.mkdir(os.path.join(".", "output"))
            except Exception:
                pass

            try:
                os.mkdir(os.path.join(".", "output", "scalable"))
            except Exception:
                pass

            try:
                os.mkdir(os.path.join(".", "output", "detailed"))
            except Exception:
                pass

    def _process(self, slist, func):
        self.threadlist = []
        P = int(len(slist)/self.NumThreads)
        if P <= 0:
            P = 1
        rlist = [slist[i:i+P] for i in range(0,len(slist),P)]
        print("Number of threads: " + str(len(rlist)))
        counter = 0
        results = Results()
        for i in rlist:
            counter=counter +1
            thr = threading.Thread(name=str(counter), \
                          target=func, args=(i,counter,results,))
            self.threadlist.append(thr)
            thr.start()
        for t in self.threadlist:
            t.join()
        results.printx()
        return self

    def classify(self):
        return self._process(self.slist, self._classify)

    def scalable(self):
        return self._process(self.entitylist, self._scalable)

    def detailed(self):
        return self._process(self.entitylist, self._detailed)

    def _classify(self, d, c, results):
        t1 = time.time()
        counter = 0
        for i in d:
            counter = counter + 1
            if self.simulate:
                entity = TT(i)
            else:
                entity = self.sd.get_driver("iDRAC", i, self.creds)
            if not entity is None:
                with self.myentitylistlock:
                    self.entitylist.append(entity)
                results.passed(entity)
            else:
                results.failed(entity)
        print("Time for " + str(c) + " thread = " + str(time.time()-t1))

    def _scalable(self, d, c, results):
        t1 = time.time()
        for entity in d:
            try:
                if self.simulate:
                    eb = [ entity.ipaddr ]
                else:
                    entity.get_partial_entityjson_str("System")
                    eb = entity.get_json_device()
                with open(os.path.join(".", "output", "scalable", entity.ipaddr), 'w') as f:
                    json.dump(eb, f)
                    f.flush()
                results.passed(eb)
            except Exception as e:
                results.failed(eb)
        print("Time for " + str(c) + " thread = " + str(time.time()-t1))

    def _detailed(self, d, c, results):
        t1 = time.time()
        for entity in d:
            try:
                if self.simulate:
                    eb = [ entity.ipaddr ]
                else:
                    entity.get_entityjson()
                    eb = entity.get_json_device()
                with open(os.path.join(".", "output", "detailed", entity.ipaddr), 'w') as f:
                    json.dump(eb, f)
                    f.flush()
                results.passed(eb)
            except Exception as e:
                results.failed(eb)
        print("Time for " + str(c) + " thread = " + str(time.time()-t1))

