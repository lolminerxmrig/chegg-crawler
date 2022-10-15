import re
import sys
import time
import pyperclip
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
from services.constants import GENERAL_ERROR
from util.mysql_db_manager import MySqlDBManager
from services.slack import Slack
main_url = "https://www.chegg.com/homework-help/questions-and-answers"
question_repository = QuestionRepository()
day_repository = DayRepository()
main_category_repository = MainCategoryRepository()
sub_category_repository = SubCategoryRepository()
mysql_db_manager = MySqlDBManager('admin',
                                  'QuizPlus123',
                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                  'chegg_general_crawler',
                                  '3306')
class DayCrawler:

    def _start_crawling(self):
        self._crawl_days()



    def _crawl_days(self):
        index = 0
        # it's not empty and I'll crawl them deep if these is element not crawled
        while True:
            # Comment: Here the first K not-crawled questions retrived which is better than hitting everytime on DB to get first not crawled
            days = day_repository.get_first_not_crawled_k_days(mysql_db_manager, 1000)
            try:
                for day in days:
                    self._open_url(day.url)
                    time.sleep(5)
                    # offline_url = self._save_web_page("questions", index)
                    pyautogui.hotkey('ctrl', 'u')
                    time.sleep(3)
                    pyautogui.click(button='left')
                    html = pyautogui.hotkey('ctrl', 'a')
                    time.sleep(2)
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(3)
                    pyautogui.hotkey('ctrl', 'c')
                    time.sleep(3)
                    html = pyperclip.paste()
                    time.sleep(2)
                    pyautogui.hotkey('ctrl', 'shift', 'w')
                    pyautogui.press('enter')
                    time.sleep(1)
                    self._crawl_questions(html, day)  # it will crawl all question in day
                    day_repository.set_crawled(mysql_db_manager, day)
                    index += 1

            except Exception as e:
                print(str(e))
                Slack().send_message_to_slack(GENERAL_ERROR, str(e))

    def _crawl_days_general(self, offline_url, index, sub_category):
        # get monthes and years
        reached_index = 0
        years_ul = self._get_years_lists(offline_url)
        all_monthes = self._get_mothes(years_ul)
        if day_repository.is_empty(mysql_db_manager) or day_repository.is_new_category(mysql_db_manager,sub_category):
            for month in all_monthes:
                days_url = main_url + '/' + month
                self._open_url(days_url)
                time.sleep(3)
                offline_url = self._save_web_page("month", index)
                self._store_days(offline_url, sub_category)
                index += 1
        else:
            month, year = day_repository.get_final_month(mysql_db_manager)
            reached = "-" + str(year) + "-" + str(month)
            regix = "^.*" + reached
            for i, month in enumerate(all_monthes):
                x = re.search(regix, month)
                if x:
                    reached_index = i
                    break

            all_monthes = all_monthes[reached_index + 1:]
            for month in all_monthes:
                days_url = main_url + '/' + month
                self._open_url(days_url)
                time.sleep(3)
                offline_url = self._save_web_page("month", index)
                self._store_days(offline_url, sub_category)
                index += 1

    def _store_days(self, offline_url, sub_category):
        day_list = []
        with open(offline_url) as fp:
            b = BeautifulSoup(fp, "html.parser")
        for tr in b.find_all('tr'):
            data = tr.find_all('a', href=True)
            for d in data:
                print(d['href'])
                day_url = main_url + "/" + d['href']
                day_list.append(day_url)
                # store day
                month, year, day_number = self.get_day_info(d['href'])
                day = Day(sub_category_repository.get_id(mysql_db_manager, sub_category), int(day_number),
                          month, year,
                          day_url)
                new_day = [[day.sub_category_id, day.day_number, day.month, day.year, day.url]]
                day_repository.add_record(mysql_db_manager, new_day)

    def _crawl_questions(self, html,day):
        questions_list = []
        urls_list = []
        soup = BeautifulSoup(html, "html.parser")
        ul = soup.find("ul", class_="questions-list")
        for li in ul:
            question_url = "https://www.chegg.com" + li.find("a", href=True)['href']
            question_text=li.find("div", class_="txt-body").text.strip()
            question_chegg_id=question_url.split("-")[-1]#get the question id from the url , it's in the final result of splitting with "-"
            day_id = day_repository.get_id(mysql_db_manager, day)
            question = Question(question_chegg_id, question_url, day_id, question_text, "null", 2000, "null", "null")
            new_question = [
                [question.question_chegg_id, question.url, question.day_id, question.question_text,
                 question.server_id]]
            question_repository.add_question_general(mysql_db_manager, new_question, question)

        #check if the question is added from answer crawler :
            # if(question_repository.is_exist_question(self.mysql_db_manager(), question_chegg_id)):
            #     question=question_repository.get_question_by_id(self.mysql_db_manager(),question_chegg_id)
            # else:
            #  #store Question
            #  question = Question(question_url, day_repository.get_id(self.mysql_db_manager(),day), question_text,2000,"null","null",question_chegg_id)
            #  new_question = [[question.url, question.day_id, question.question_text,question.server_id,question.question_html,question.page_html,question.question_chegg_id]]
            #  question_repository.add_record(self.mysql_db_manager(), new_question)



        # for li in ul.findAll("a", href=True):
        #     question_url = "https://www.chegg.com" + li['href']
        #     if li.text.strip() != '' and self._search(urls_list, question_url) == False and li.text.strip().__len__()>60:
        #         questions_list.append(str(li.text.strip()))
        #         question_text = str(li.text.strip())
        #         urls_list.append(question_url)
        #         # store Question
        #         question = Question(question_url, day_repository.get_id(self.mysql_db_manager(),day), question_text,2000,"null","null")
        #         new_question = [[question.url, question.day_id, question.question_text,question.server_id,question.question_html,question.page_html]]
        #         question_repository.add_record(self.mysql_db_manager(), new_question)

    def _search(self, urls_list, question_url):
        for i in range(len(urls_list)):
            if urls_list[i] == question_url:
                return True
        return False

    def set_resoution(self):
        dx, dy = image_service.get_resolution()
        return dx, dy

    def _open_url(self, url):
        print(url)
        pyperclip.copy(url)
        webbrowser.open_new(url)
        # dx,dy=self.set_resoution()
        # pyautogui.moveTo(dx*400, dy*55, 1)
        # pyautogui.click(button='left')
        #
        # time.sleep(1)
        # pyautogui.hotkey('ctrl', 'v')
        # pyautogui.press('enter', interval=0.1)
        time.sleep(1)

    def _save_web_page(self, string, index):
        time.sleep(5)
        pyautogui.hotkey('alt', 'f')
        pyautogui.press('down', presses=6, interval=0.1)
        time.sleep(1)
        # pyautogui.press('right', interval=0.1)
        pyautogui.press('enter')
        time.sleep(1)
        name = string + str(index)
        offline_url = "C:/Users/Administrator/Desktop/chegg_crawler/web_pages/" + name + '.html'
        pyautogui.typewrite(name + '.html')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(1)
        pyautogui.press('left')
        pyautogui.press('enter')
        time.sleep(3)
        pyautogui.hotkey('ctrl', 'shift', 'w')
        pyautogui.press('enter')
        time.sleep(1)
        return offline_url

    def _get_categories(self, offline_url):
        with open(offline_url) as fp:
            soup = BeautifulSoup(fp, "html.parser")
        ul = soup.find("ul", class_="subject-list")
        return ul

    def _get_li(self, ul):
        listItems = []
        for li in ul.findAll("li", recursive=True):
            print(li.contents[0].text)
            listItems.append(li.contents[0].text)
        return listItems

    def _get_li_sub(self, ul):
        listItems = []
        for li in ul.findAll("li", recursive=True):
            print(li.text)
            listItems.append(li.text)
        return listItems

    def _get_years_lists(self, offline_url):
        with open(offline_url) as fp:
            soup = BeautifulSoup(fp, "html.parser")
        ul = soup.find("ul", class_="year-list")
        return ul

    def _get_mothes(self, ul):
        listItems = []
        for li in ul.findAll("a", href=True):
            print(li['href'])
            listItems.append(li['href'])
        return listItems

    def get_day_info(self, day_string):
        day_string = day_string.replace('-', ' ')
        list = day_string.split()
        year = str(list[list.__len__() - 3])
        month = str(list[list.__len__() - 2])
        day = str(list[list.__len__() - 1])
        return month, year, day

    # def mysql_db_manager(self):
    #     mysql_db_manager = MySqlDBManager('admin',
    #                                       'QuizPlus123',
    #                                       'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
    #                                       'chegg_general_crawler',
    #                                       '3306')
    #     return mysql_db_manager
