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
from services.slack import Slack
main_url = "https://www.chegg.com/homework-help/questions-and-answers"
day_repository = DayRepository()
main_category_repository = MainCategoryRepository()
sub_category_repository = SubCategoryRepository()
question_repository = QuestionRepository()
class CheckUpdates:

            def _start_crawling(self):
                index = 0
                if main_category_repository.is_empty(self.mysql_db_manager()):
                    # crawl main general
                    self._crawl_main_categories_general(index)

                # it's not empty and I'll crawl them deep if there is element not crawled
                # but first i'll check if there is any updates:
                self._check_updates_main(index)
                while (main_category_repository.get_first_not_crawled(self.mysql_db_manager()) != None):#must edit inside outside
                    main_category = main_category_repository.get_first_not_crawled(self.mysql_db_manager())
                    self._open_url(main_category.url)
                    time.sleep(3)
                    offline_url = self._save_web_page("sub_category", index)
                    print("im here 1")
                    self._check_updates_sub(offline_url, main_category)  # it will go to general
                    main_category_repository.set_crawled(self.mysql_db_manager(), main_category)
                    index += 1
                print("im here 2")
                self._crawl_sub_categories()  # it will go to deep

            def _crawl_main_categories_general(self, index):
                webbrowser.open_new(main_url)
                time.sleep(4)
                offline_url = self._save_web_page("main_category", index)
                main_catagories_ul = self._get_categories(offline_url)
                main_catagories = self._get_li(main_catagories_ul)
                for li in main_catagories:
                    # generate url
                    li = li.replace(" ", "-")
                    main_category_url = main_url + '/' + li.lower()
                    # store main cat. in table with attributes name, url...etc
                    mainCat = MainCategory(li, main_category_url)
                    new_main_category = [[mainCat.name, mainCat.url]]
                    main_category_repository.add_record(self.mysql_db_manager(), new_main_category)

            def _check_updates_main(self, index):
                webbrowser.open_new(main_url)
                time.sleep(4)
                offline_url = self._save_web_page("main_category", index)
                main_catagories_ul = self._get_categories(offline_url)
                main_catagories = self._get_li(main_catagories_ul)
                if main_catagories.__len__() != main_category_repository.get_count(self.mysql_db_manager()):
                    for li in main_catagories:
                        li = li.replace(" ", "-")
                        if not (main_category_repository.is_exist(self.mysql_db_manager(), li)):
                            print("new category will be added to database!")
                            main_category_url = main_url + '/' + li.lower()
                            # store main cat. in table with attributes name, url...etc
                            mainCat = MainCategory(li, main_category_url)
                            new_main_category = [[mainCat.name, mainCat.url]]
                            main_category_repository.add_record(self.mysql_db_manager(), new_main_category)

            def _crawl_sub_categories(self):
                index = 0
                # it's not empty and I'll crawl them deep if these is element not crawled
                # but first i'll check if there is any updates:
                while (sub_category_repository.get_first_not_crawled(self.mysql_db_manager()) != None):#must edit
                    sub_category = sub_category_repository.get_first_not_crawled(self.mysql_db_manager())
                    time.sleep(3)
                    self._open_url(sub_category.url)
                    name = sub_category.name[1:5]
                    time.sleep(0.5)
                    offline_url = self._save_web_page(name + "monthes", index)
                    self._crawl_days_general(offline_url, index, sub_category)  # it will go to general
                    time.sleep(1)
                    sub_category_repository.set_crawled(self.mysql_db_manager(), sub_category)
                    index += 1
                # self._crawl_days()  # it will go to deep

            def _check_updates_sub(self, offline_url, main_category):
                # now get the sub categories:
                time.sleep(3)
                sub_categories_ul = self._get_categories(offline_url)
                sub_categories = self._get_li_sub(sub_categories_ul)
                for sub in sub_categories:
                    # generate URLs to enter them
                    sub = sub.replace(" ", "-")
                    sub_categories_url = main_url + '/' + sub.lower() + "-archive"
                    if not(sub_category_repository.is_exist(self.mysql_db_manager(),sub)):
                       # store sub cat. in table with attributes name, url...etc
                      main_category_id = int(main_category_repository.get_id(self.mysql_db_manager(), main_category))
                      subCat = SubCategory(main_category_id, sub, sub_categories_url)
                      new_sub_category = [[subCat.main_category_id, subCat.name, subCat.url]]
                      sub_category_repository.add_record(self.mysql_db_manager(), new_sub_category)

            # def _crawl_days(self):
            #     index = 0
            #     # it's not empty and I'll crawl them deep if these is element not crawled
            #     while day_repository.get_first_not_crawled(self.mysql_db_manager()) is not None:
            #         day = day_repository.get_first_not_crawled(self.mysql_db_manager())
            #         time.sleep(3)
            #         self._open_url(day.url)
            #         offline_url = self._save_web_page("questions", index)
            #         self._crawl_questions(offline_url, day)  # it will crawl all question in day
            #         sub_category_repository.set_crawled(self.mysql_db_manager(), day)
            #         index += 1

            def _crawl_days_general(self, offline_url, index, sub_category):
                # get monthes and years
                reached_index = 0
                years_ul = self._get_years_lists(offline_url)
                all_monthes = self._get_mothes(years_ul)
                for month in all_monthes:
                    days_url = main_url + '/' + month
                    self._open_url(days_url)
                    name = sub_category.name[1:5]
                    time.sleep(0.5)
                    offline_url = self._save_web_page(name + "month", index)
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
                        if not(day_repository.is_exist_day(self.mysql_db_manager(),day_url)):
                            # store day
                            month, year, day_number = self.get_day_info(d['href'])
                            day = Day(sub_category_repository.get_id(self.mysql_db_manager(), sub_category),
                                      int(day_number),
                                      month, year,
                                      day_url)
                            new_day = [[day.sub_category_id, day.day_number, day.month, day.year, day.url]]
                            day_repository.add_record(self.mysql_db_manager(), new_day)


            # def _crawl_questions(self, offline_url, day):
            #     questions_list = []
            #     urls_list = []
            #     with open(offline_url, encoding="latin-1") as fp:
            #         soup = BeautifulSoup(fp, "html.parser")
            #     ul = soup.find("ul", class_="questions-list")
            #     for li in ul.findAll("a", href=True):
            #         question_url = "https://www.chegg.com" + li['href']
            #         if li.text.strip() != '' and self._search(urls_list, question_url) == False:
            #             questions_list.append(str(li.text.strip()))
            #             question_text = str(li.text.strip())
            #             urls_list.append(question_url)
            #             # store Question
            #             question = Question(question_url, day_repository.get_id(self.mysql_db_manager(), day),
            #                                 question_text)
            #             new_question = [[question.url, question.day_id, question.text]]
            #             question_repository.add_record(self.mysql_db_manager(), new_question)

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

            def mysql_db_manager(self):
                mysql_db_manager = MySqlDBManager('admin',
                                                  'QuizPlus123',
                                                  'quizplusdevtestdb.c4m3phz25ns8.us-east-1.rds.amazonaws.com',
                                                  'chegg_general_crawler',
                                                  '3306')
                return mysql_db_manager
