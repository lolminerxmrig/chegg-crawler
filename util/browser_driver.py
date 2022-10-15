from selenium import webdriver
import time
from random import randrange
import chromedriver_autoinstaller
class BrowserDriver:
    def __init__(self):
        self.driver = self._initialize_driver()

    def _initialize_driver(self):
        chromedriver_autoinstaller.install()
        driver = webdriver.Chrome()
        time.sleep(randrange(1,3))
        return driver

    def close_driver(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()