from services.constants import GENERAL_ERROR
from services.google_answer_crawler import GoogleCrawler
from services.anonymous_link_crawler_service import LinkCrawler
from services.slack import Slack

if __name__ == '__main__':
    try:
        LinkCrawler()._start_crawling()

    except Exception as e:

        print(str(e))
        Slack().send_message_to_slack(GENERAL_ERROR, str(e))
