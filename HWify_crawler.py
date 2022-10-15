from services.constants import GENERAL_ERROR
from services.google_answer_crawler import GoogleCrawler
from services.link_crawler_HWify import HWifyCrawler
from services.slack import Slack

if __name__ == '__main__':
    try:
        HWifyCrawler()._start_crawling()

    except Exception as e:

        print(str(e)+"TALA")
        #Slack().send_message_to_slack(GENERAL_ERROR, str(e))
