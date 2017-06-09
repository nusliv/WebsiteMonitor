To run the monitor-service, you need a conf.txt file in the PWD.


 Conf file format:
 It is in Json format

 log_file: path to your log file
 log_level: level of logging
 urls: list of urls to be checked
 interval: seconds to wait between each check
 maxHistoryLen: A history of status responses is maintailed per URL. This                 specifies the max length
 maxContinuousBad: If the number of continuous errors seen exceeds this
                   count. A critical error is logged.


 Example conf file:

{
  "log_level": "DEBUG", 
  "interval": 1, 
  "maxHistoryLen": 200, 
  "maxContinuousBad": 3, 
  "urls": [
    "localhost:12345"
  ], 
  "log_file": "/tmp/log.txt"
}
