import time

from services.constants import GENERAL_ERROR
from services.day_crawler import DayCrawler
from services.slack import Slack
import sys

if __name__ == '__main__':
    try:
        time.sleep(3)
        DayCrawler()._start_crawling()
        time.sleep(3)

    except Exception as e:
        print(str(e))
       # Slack().send_message_to_slack(GENERAL_ERROR, str(e))

