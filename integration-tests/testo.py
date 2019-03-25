from selenium import webdriver
from django.test import LiveServerTestCase
from selenium.webdriver.firefox.options import Options
from django.urls import reverse
import os
from selenium.webdriver.common.keys import Keys


class SeleniumTestCase(LiveServerTestCase):
    def setUp(self):
        options = Options()
        options.headless = False
        self.selenium = webdriver.Firefox(options=options)
        super(SeleniumTestCase, self).setUp()


    def tearDown(self):
        self.selenium.quit()
        super(SeleniumTestCase, self).tearDown()

    def test_login(self):
        selenium = self.selenium
        selenium.get(os.getenv('REDIRECT_URI') + reverse('classy:index'))
        username = selenium.find_element_by_id('username')
        password = selenium.find_element_by_id('password')

        print(username, password)

        username.send_keys(os.getenv('TEST_ACCOUNT_USERNAME'))
        password.send_keys(os.getenv('TEST_ACCOUNT_PASSWORD'))

        submit = selenium.find_element_by_name('login')

        submit.send_keys(Keys.RETURN)

        selenium.get(os.getenv('REDIRECT_URI'))
        

        print(selenium.page_source)

        assert 'Welcome' in selenium.page_source


