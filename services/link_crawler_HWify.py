import re
import sys
import time
import os
import pyperclip
from services.constants import N_QUESTIONS_CRAWLE_SUCCESSFULLY, NO_QUESTION_YET, GENERAL_ERROR
from services.slack import Slack
from bs4 import BeautifulSoup
from repository.Model.Question import Question
from repository.question_repository import QuestionRepository
import pyautogui
import webbrowser
import subprocess
from services import image_service
from util.mysql_db_manager import MySqlDBManager
from services.constants import chrome_path
from services.constants import firefox_path
from services.constants import search_url
from services.constants import main_url
from services.constants import storagePath
from services.constants import cookiePath
from services.constants import sessionPath

question_repository = QuestionRepository()
mysql_db_manager = MySqlDBManager('admin',
                                  'QuizPlus123',
                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                  'chegg_general_crawler',
                                  '3306')


class HWifyCrawler:
    def _start_crawling(self):
        flag = 0
        pyautogui.screenshot("web.png")
        dx, dy = self.set_resoution()
        time.sleep(1)
        while True:
            # Comment: Here the first K not-crawled questions retrived which is better than hitting everytime on DB to get first not crawled
            questions = question_repository.get_first_not_answer_retrived_k_questions(mysql_db_manager, 1000)
            try:
                for question in questions:
                    flag = 1
                    # get url from Database and copy it
                    webbrowser.get(chrome_path).open("https://homeworkify.net/")
                    time.sleep(5)
                    # go to 700 850 to the window of search URL
                    pyautogui.moveTo(dx * 700, dy * 850, 1)
                    pyautogui.typewrite(question.url)
            except Exception as e:
                print(str(e))
                Slack().send_message_to_slack(GENERAL_ERROR, str(e))
                sys.exit()
            if flag == 0:
                print("Sorry But there is no question yet, wait the crawling process")
                Slack().send_message_to_slack(NO_QUESTION_YET, " ")





    def set_resoution(self):
        dx, dy = image_service.get_resolution()
        return dx, dy
