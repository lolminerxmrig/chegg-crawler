from services.answer_crawler import AnswerCrawler
from services.check_updates import CheckUpdates

if __name__ == '__main__':
    try:
        CheckUpdates()._start_crawling()

    except Exception as e:
        print(str(e))
       # Slack().send_message_to_slack(GENERAL_ERROR, str(e))
