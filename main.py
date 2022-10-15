from services.constants import GENERAL_ERROR
from services.crawler_service import  CrawlerService
from services.slack import Slack
from util.mysql_db_manager import MySqlDBManager

if __name__ == '__main__':
    try:
        CrawlerService()._start_crawling()

    except Exception as e:
        print(str(e))
       # Slack().send_message_to_slack(GENERAL_ERROR, str(e))
