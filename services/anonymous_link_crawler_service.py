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


class LinkCrawler:

    def _start_crawling(self):
        flag = 0
        index = 0
        pyautogui.screenshot("web.png")
        dx, dy = self.set_resoution()
        os.system("taskkill /im firefox.exe /f")
        time.sleep(2)
        if os.path.exists(storagePath):
            os.unlink(storagePath)

        if os.path.exists(sessionPath):
            os.unlink(sessionPath)

        if os.path.exists(cookiePath):
            os.unlink(cookiePath)
        subprocess.call([r'C:/Program Files/Mozilla Firefox/firefox.exe', '-new-tab', 'http://www.google.com/'])
        time.sleep(9)
        # add While true
        while True:
            # Comment: Here the first K not-crawled questions retrived which is better than hitting everytime on DB to get first not crawled
            questions = question_repository.get_first_not_answer_checked_k_questions(mysql_db_manager, 1000)
            try:
                for question in questions:
                    flag = 1

                    webbrowser.open_new_tab(question.url)
                    time.sleep(4)
                    html = self._save_web_page(dx, dy)
                    count_captch_tries = 0
                    while self._is_captcha(html, dx, dy):

                        os.system("taskkill /im firefox.exe /f")
                        if os.path.exists(storagePath):
                            os.unlink(storagePath)

                        if os.path.exists(sessionPath):
                            os.unlink(sessionPath)

                        if os.path.exists(cookiePath):
                            os.unlink(cookiePath)

                        time.sleep(5)
                        subprocess.call(
                            [r'C:/Program Files/Mozilla Firefox/firefox.exe', '-new-tab', 'http://www.google.com/'])
                        time.sleep(9)
                        webbrowser.open_new_tab(question.url)
                        time.sleep(4)
                        html = self._save_web_page(dx, dy)
                        if count_captch_tries == 4 and html.find("verify you are a human") != -1:
                            Slack().send_message_to_slack(GENERAL_ERROR, "Falied in solving recaptcha")
                            sys.exit()
                        if html.find("verify you are a human") == -1:
                            break
                        count_captch_tries = count_captch_tries + 1

                    pyautogui.hotkey('ctrl', 'w')

                    if html.find(
                            "This problem has been solved!</h2>") != -1:  # it has answer and we have to change the browser
                        question_repository.set_answer_checked_with_expert_answer(mysql_db_manager, question)


                    else:  # so I'll check if the result is from chegg or not + if the result is question or book manual or failure in chegg account

                        if html.find("This question hasn't been solved yet") != -1 or html.find(
                                "Study time, crunch time, anytime") != -1:  # add reason:no expert answer
                            question_repository.set_answer_checked_with_no_expert_answer(mysql_db_manager, question)

                    index += 1

            except Exception as e:
                print(str(e))
                Slack().send_message_to_slack(GENERAL_ERROR, str(e))
                sys.exit()
            if flag == 0:
                print("Sorry But there is no question yet, wait the crawling process")
                Slack().send_message_to_slack(NO_QUESTION_YET, " ")

            else:
                print("All question is crawled and contain answers")
                Slack().send_message_to_slack(N_QUESTIONS_CRAWLE_SUCCESSFULLY, " ")

    def set_resoution(self):
        dx, dy = image_service.get_resolution()
        return dx, dy

    def _is_captcha(self, html, dx, dy):
        found_captcha = False
        if html.find("human") == -1:
            return found_captcha

        while True:
            time.sleep(1)
            pyautogui.screenshot('my_screenshot11.png')

            if html.find("verify you are a human") != -1:
                Slack().send_message_to_slack("Recaptcha", "Solving Recaptcha")
                found_captcha = True
                pyautogui.moveTo(360, 375)
                pyautogui.mouseDown(button='left')

                while True:
                    im1 = pyautogui.screenshot()
                    color_px = im1.getpixel((478, 390))
                    if color_px[0] < 250 and color_px[1] < 250 and color_px[2] < 250:
                        break

                time.sleep(1)
                pyautogui.mouseUp(button='left')
                time.sleep(60)
                break


            else:
                Slack().send_message_to_slack("Recaptcha", "Solved Yess!!")
                print("solved")
                break
        # Not captcha page
        return found_captcha

    def _save_web_page(self, dx, dy):

        pyperclip.copy("")
        while True:
            print("clicking to get soruce html")
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'u')
            time.sleep(1)
            pyautogui.moveTo(dx * 400, dy * 420, 1)
            pyautogui.click(button='left')
           # html = pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(1)
            html = pyperclip.paste()
            if html.find("<html") != -1:
                break
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'w')

        return html

    def _get_answer(self, html):
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div", class_=["answer-given-body"])
        return div

    def _get_question_html(self, html):
        soup = BeautifulSoup(html, "html.parser")
        div1 = soup.find("div", class_=["question"])
        div2 = soup.find("div", class_=["hidden"])
        return str(div1) + "\n" + str(div2)

    def _subscription_is_failed(self, html):
        soup = BeautifulSoup(html, "html.parser")
        result = soup.find("div", class_=["question"])
        if result != "None":
            return True
        else:
            return False
