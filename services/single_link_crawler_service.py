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
chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s '

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
        while True:
            # Comment: Here the first K not-crawled questions retrived which is better than hitting everytime on DB to get first not crawled
            questions = question_repository.get_first_not_answer_retrived_k_questions(mysql_db_manager, 1000)
            try:
                for question in questions:
                    flag = 1
                    webbrowser.get(chrome_path).open_new_tab(question.url)
                    time.sleep(5)

                    html = self._save_web_page(dx, dy)

                    count_captch_tries = 0
                    while self._is_captcha(html, dx, dy):
                        pyautogui.hotkey('ctrl', 'w')
                        time.sleep(1)
                        webbrowser.open_new_tab(question.url)
                        html = self._save_web_page(dx, dy)
                        if count_captch_tries == 4 and html.find("verify you are a human") != -1:
                            Slack().send_message_to_slack(GENERAL_ERROR, "Falied in solving recaptcha")
                            sys.exit()
                        count_captch_tries = count_captch_tries + 1

                    question_html = self._get_question_html(html)
                    answer = self._get_answer(html)

                    if str(answer) != 'None':  # there is no problem with this question
                        print("same result! ")
                        state = "no failure"
                        question_repository.set_question_info(mysql_db_manager, question, answer, question_html,
                                                              html, state)
                        pyautogui.hotkey('ctrl', 'w')
                        Slack().send_message_to_slack("Crawled Successfully", question.url)
                        time.sleep(60 * 10)

                    elif html.find("ACCOUNT_IN_DETENTION") != -1:
                        reason = "SUBSCRIPTION FAILURE!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                        print(reason)
                        # question_repository.set_broken(mysql_db_manager, question, reason)
                        Slack().send_message_to_slack(GENERAL_ERROR, reason)
                        sys.exit()

                    elif str(answer) == 'None' and html.find("chegg") != -1:
                        problem = "there is something wrong maybe with sign-in or the answer itself"
                        print(problem)
                        Slack().send_message_to_slack(GENERAL_ERROR, problem)
                        pyautogui.hotkey('ctrl', 'w')
                        sys.exit()

                    elif str(answer) == 'None' and html.find("chegg") == -1:
                        problem = "unknown"
                        print(problem)
                        Slack().send_message_to_slack(GENERAL_ERROR, problem)
                        pyautogui.hotkey('ctrl', 'w')
                        sys.exit()

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
            html = pyautogui.hotkey('ctrl', 'a')
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



