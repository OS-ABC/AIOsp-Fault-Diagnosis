import datetime
import time

import pytz


def is_number(number):
    """
    Check whether this is a number (int, long, float, hex) .

    Aruguments:
        number: {string}, input string for number check.
    """
    try:
        float(number)  # for int, long, float
    except ValueError:
        try:
            int(number, 16) # for possible hex
        except ValueError:
            return False

    return True

# UTCS时间转换为时间戳 2018-07-13T16:00:00Z
def utc_to_local(utc_time_str, utc_format='%Y-%m-%dT%H:%M:%S.%fZ'):
    local_tz = pytz.timezone('Asia/Chongqing')      #定义本地时区
    local_format = "%Y-%m-%d %H:%M:%S"              #定义本地时间format

    utc_dt = datetime.datetime.strptime(utc_time_str, utc_format)       #讲世界时间的格式转化为datetime.datetime格式
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)     #想将datetime格式添加上世界时区，然后astimezone切换时区：世界时区==>本地时区
    #time_str = local_dt.strftime(local_format)                         #将datetime格式转化为str—format格式
    #return int(time.mktime(time.strptime(time_str, local_format)))     #运用mktime方法将date—tuple格式的时间转化为时间戳;time.strptime()可以得到tuple的时间格式
    return int(time.mktime(local_dt.timetuple()))