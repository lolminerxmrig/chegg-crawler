import re
import sys
import time
import pyperclip

from services.constants import N_QUESTIONS_CRAWLE_SUCCESSFULLY, NO_QUESTION_YET, GENERAL_ERROR
from services.slack import Slack
from bs4 import BeautifulSoup
from repository.Model.Day import Day
from repository.Model.MainCategory import MainCategory
from repository.Model.Question import Question
from repository.Model.SubCategory import SubCategory

from repository.day_repository import DayRepository
from repository.main_category_repository import MainCategoryRepository
from repository.question_repository import QuestionRepository
from repository.sub_category_repository import SubCategoryRepository
import pyautogui
import webbrowser
from services import image_service
from util.mysql_db_manager import MySqlDBManager
question_repository = QuestionRepository()
mysql_db_manager = MySqlDBManager('admin',
                                  'QuizPlus123',
                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                  'chegg_general_crawler',
                                  '3306')
class AnswerCrawler:

    def _start_crawling(self):
        search_url = "https://www.google.com/search?q=search&client=firefox-b-d&sxsrf=AOaemvJMXW5hlRoO20cjqYKhqMKLu-nkqw%3A1642458377329&ei=Ce3lYdTVE_3KytMP0NCMiAQ&ved=0ahUKEwiU_o2h6rn1AhV9pXIEHVAoA0EQ4dUDCA4&uact=5&oq=search&gs_lcp=Cgdnd3Mtd2l6EAMyBQgAEJECMgQIABBDMgsILhCABBCxAxCDATIFCAAQkQIyBwgAELEDEEMyBAgAEEMyCAgAEIAEELEDMggIABCABBCxAzIECAAQQzILCAAQgAQQsQMQgwE6BwgjELADECc6BAgjECc6CAgAELEDEIMBOgUIABCABDoICC4QsQMQgwE6DgguEIAEELEDEMcBEKMCOggILhCABBCxAzoECC4QQzoLCAAQgAQQsQMQyQNKBAhBGAFKBAhGGABQtw9Y3Rtg-iNoAXAAeACAAVSIAYgDkgEBNpgBAKABAcgBAcABAQ&sclient=gws-wiz"
        main_url = "https://www.chegg.com/homework-help/questions-and-answers"
        flag = 0
        index = 0
        webbrowser.open_new(main_url)
        time.sleep(3)
        pyautogui.screenshot("web.png")
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'w')
        dx, dy = self.set_resoution()

        #add While true
        while True:
            # Comment: Here the first K not-crawled questions retrived which is better than hitting everytime on DB to get first not crawled
            questions = question_repository.get_first_not_crawled_k_questions(mysql_db_manager, 1000)
            try:
                for question in questions:

                    flag = 1
                    pyperclip.copy(question.url)
                    time.sleep(2)
                    webbrowser.open_new(search_url)
                    time.sleep(1)
                    pyautogui.moveTo(dx * 300, dy * 135, 1)
                    time.sleep(.2)
                    pyautogui.click(button='left')
                    pyautogui.click(button='left')
                    time.sleep(.3)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(.5)
                    pyautogui.press('enter')
                    pyautogui.moveTo(dx * 200, dy * 300, 0.6)
                    pyautogui.click(button='left')
                    pyautogui.click(button='left')
                    time.sleep(2)
                    pyautogui.moveTo(dx * 300, dy * 70, 0.5)
                    time.sleep(1)
                    pyautogui.click(button='left')
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(1)
                    url = pyperclip.paste()
                    html = self._save_web_page(dx, dy)
                    question_html = self._get_question_html(html)
                    answer = self._get_answer(html)
                    question_chegg_id = url.split("-")[-1]  # get the question id from the url , it's in the final result of splitting with "-"
                    question_chegg_id = question_chegg_id.split("?")[0]

                    if str(answer) != 'None' and url.find(question.url) != -1:  # there is no problem with this question
                        print("same result! ")
                        state = "no failure"
                        #question_repository.set_reason(mysql_db_manager, question_chegg_id, state)
                        # question_repository.set_answer(self.mysql_db_manager(), question, answer)
                        # question_repository.set_page_html(self.mysql_db_manager(), question, html)
                        # question_repository.set_question_html(self.mysql_db_manager(), question, question_html)
                        #question_repository.set_processed(self.mysql_db_manager(), question)
                        question_repository.set_question_info(mysql_db_manager,question,answer,question_html,html,state)
                        time.sleep(3 * 60)
                    else: #so I'll check first if the result is from chegg or not + if the result is question or book manual or failure in chegg account
                        print("not the same result! ")
                        if html.find("chgg-menu-icon") == -1:#add reason:no chegg result in google
                            reason="no chegg result in google"
                            print(reason)
                            #question_repository.set_reason(mysql_db_manager,question_chegg_id,reason)
                            question_repository.set_broken(mysql_db_manager, question,reason)
                        elif str(answer) == 'None' and html.find("An expert answer will be posted here") != -1:# add reason:no expert answer
                            reason="no expert answer"
                            print(reason)
                            #question_repository.set_reason(mysql_db_manager, question_chegg_id,reason)
                            question_repository.set_broken(mysql_db_manager, question,reason)
                            time.sleep(3 * 60)

                        #elif html.find(" ") != -1: soultion manual

                        elif html.find("ACCOUNT_IN_DETENTION") != -1:
                            reason = "SUBSCRIPTION FAILURE!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                            print(reason)
                            question_repository.set_broken(mysql_db_manager, question,reason)
                            Slack().send_message_to_slack(GENERAL_ERROR, reason)
                            break
                            sys.exit()

                        else: # insert update, insert new question
                            reason = "the result is redirected to another question so it's added"
                            state="it's a redirected question"
                            #question_repository.set_reason(mysql_db_manager, question_chegg_id, reason)
                            question_repository.set_broken(mysql_db_manager, question, reason)
                            question2 = Question(question_chegg_id, url, "null", "null", str(answer), 2000,
                                                 str(question_html), str(html))
                            new_question = [
                                [question2.question_chegg_id, question2.url,
                                 question2.answer, question2.server_id,
                                 question2.question_html, question2.page_html,state]]
                            question_repository.add_question_crawled(mysql_db_manager, new_question, question)
                            time.sleep(3 * 60)
                    index += 1

            except Exception as e:
                print(str(e))
                Slack().send_message_to_slack(GENERAL_ERROR, str(e))
            if flag == 0:
                print("Sorry But there is no question yet, wait the crawling process")
                Slack().send_message_to_slack(NO_QUESTION_YET, " ")
            else:
                print("All question is crawled and contain answers")
                # Slack().send_message_to_slack(N_QUESTIONS_CRAWLE_SUCCESSFULLY, " ")

    def set_resoution(self):
        dx, dy = image_service.get_resolution()
        return dx, dy

    def _save_web_page(self,dx,dy):
        pyautogui.hotkey('ctrl', 'u')
        time.sleep(0.5)
        pyautogui.moveTo(dx * 400, dy * 420, 1)
        pyautogui.click(button='left')
        html = pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.2)
        html = pyperclip.paste()
        pyautogui.hotkey('ctrl',  'w')
        pyautogui.hotkey('ctrl', 'w')

        return html

    def _get_answer(self, html):
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find("div", class_=["answer-given-body"])
        return div

    def _get_question_html(self,html):
        soup = BeautifulSoup(html, "html.parser")
        div1 = soup.find("div", class_=["question"])
        div2 = soup.find("div", class_=["hidden"])
        return str(div1)+"\n"+str(div2)

    def _subscription_is_failed(self,html):
        soup = BeautifulSoup(html, "html.parser")
        result = soup.find("div", class_=["question"])
        if result !="None":
            return True
        else:
            return False



    # def mysql_db_manager(self):
    #      mysql_db_manager = MySqlDBManager('admin',
    #                                   'QuizPlus123',
    #                                   'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
    #                                   'chegg_general_crawler',
    #                                   '3306')
    #      return mysql_db_manager
