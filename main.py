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
from util.browser_driver import BrowserDriver
from util.mysql_db_manager import MySqlDBManager
from selenium.webdriver.common.by import By
from services.constants import chrome_path
from services.constants import firefox_path
from services.constants import search_url
from services.constants import main_url
from services.constants import storagePath
from services.constants import cookiePath
from services.constants import sessionPath
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

def set_resolution():
    dx, dy = image_service.get_resolution()
    return dx, dy


if __name__ == '__main__':
    dx, dy = set_resolution()
    print("1")
    #webbrowser.get(chrome_path).open("https://homeworkify.net/")
    #webbrowser.open_new("https://homeworkify.net/")
    # print("2")
    # time.sleep(2)
    # print("3")
    # pyautogui.moveTo(dx * 700, dy * 850, 1)
    #time.sleep(5)
    # print("4")
    # pyautogui.scroll(-600)
    # time.sleep(2)
    # driver = BrowserDriver().driver
    # driver.get("https://homeworkify.net/")
    # driver.get("chrome://extensions/")
    # driver.maximize_window()
    chrome_options=ChromeOptions()
    chrome_options.add_extension('ReCaptcha-Solver.crx')
    driver=webdriver.Chrome('./chromedriver',options=chrome_options)
    driver.get("https://homeworkify.net/")
    driver.maximize_window()
    pyautogui.moveTo(dx * 1800, dy * 50, 1)
    time.sleep(2)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.hotkey('down')
    time.sleep(0.5)
    pyautogui.hotkey('down')
    time.sleep(2)
    pyautogui.press('enter')



