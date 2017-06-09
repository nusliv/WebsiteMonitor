import pprint, time, os
import httplib
import pdb
import logging
import sys
import json
import time
from collections import deque
from daemon import runner

class UrlStatus:
    """
    Hold the status of a URL
    """
    url = ""
    okCount = 0
    failCount = 0
    contBad = 0
    maxHistoryLen = 0
    maxContBad = 0
    history = deque()

    def __init__(self, url, maxHistoryLen, maxContBad):
        self.url = url
        self.maxHistoryLen = maxHistoryLen
        self.maxContBad = maxContBad

    def upateStatus(self, status):
        """
        Update the counters given the current status
        """
        self.history.append(status)
        if len(self.history) > self.maxHistoryLen:
            try:
                oldStatus = self.history.popleft()
            except Exception as e:
                logging.critical("History not maintained. Please check conf file")
                raise
            if oldStatus == 200:
                self.okCount-=1
            else:
                self.failCount-=1

        if status == 200:
            self.contBad = 0
            self.okCount+=1
        else:
            self.failCount+=1
            self.contBad+=1

    def getStatus(self):
        """
        Return string updating the status of the URL
        """
        if self.contBad > self.maxContBad:
            return (logging.CRITICAL, 'URL:{} is not responding'.format(self.url))
        else:
            return (logging.INFO, 'URL:{}: failCount:{}: okCount:{}:'.format(self.url, self.failCount, self.okCount))

class URLMonitor():
    """
    The daemon class to check URLs
    """
    def __init__(self, config):
	self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path =  '/tmp/foo.pid'
        self.pidfile_timeout = 5
        self.config = config

    def run(self):
        log_file = self.config['log_file']
        log_level = self.config['log_level'].lower()
        interval = int(self.config['interval'])
        maxHistoryLen = int(self.config['maxHistoryLen'])
        maxContBad = int(self.config['maxContinuousBad'])

	# Set logging level
	if log_level == 'debug':
	    logging.basicConfig(filename=log_file, level=logging.DEBUG)
	elif log_level == 'info':
	    logging.basicConfig(filename=log_file, level=logging.INFO)


        urls = [UrlStatus(url, maxHistoryLen, maxContBad) for url in self.config['urls']]

        # Run the checks
        while True:
            time.sleep(interval)
            self.checkUrl(urls)

    def checkUrl(self, urls):
        """
        Get status of each url in the list of urls
        """

        data = {}
        data['timestamp'] = time.time()
        for url in urls:
            # Treat connection problem as and error too
            try:
                conn = httplib.HTTPConnection(url.url)
                conn.request("HEAD", "/")
                res = conn.getresponse()
                status = res.status
            except:
                #Using 404 to indicate the server was not reachable
                status = 404 

            url.upateStatus(status)
            log_level, data['Status'] = url.getStatus()
            if log_level == logging.INFO:
                logging.info(data)
            elif log_level == logging.CRITICAL:
                logging.critical(data)

def main():

    conffile = 'conf.txt'

    # Read conf file
    try:
        with open(conffile, 'r') as f:
            config = json.load(f)
    except exception as e:
        print("Need conf.txt in current path")

    #Check if the format is correct
    try:
        log_file = config['log_file']
        log_level = config['log_level'].lower()
        interval = int(config['interval'])
        maxHistoryLen = int(config['maxHistoryLen'])
        maxContBad = int(config['maxContinuousBad'])
    except:
        print("Log file format is not correct")
        raise


    monitorService = URLMonitor(config)
    daemon_runner = runner.DaemonRunner(monitorService)
    daemon_runner.do_action()


if __name__ == "__main__":
    main()
