
from services.answer_crawler import AnswerCrawler

if __name__ == '__main__':
    try:
        AnswerCrawler()._start_crawling()

    except Exception as e:
        print(str(e))
       # Slack().send_message_to_slack(GENERAL_ERROR, str(e))
