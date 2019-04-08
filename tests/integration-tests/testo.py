from selenium import webdriver
from django.test import TestCase
from selenium.webdriver.firefox.options import Options
from django.urls import reverse
import os, time
from selenium.webdriver.common.keys import Keys
import requests
from requests.auth import HTTPBasicAuth

class SeleniumTestCase(TestCase):
    def setUp(self):
        options = Options()
        options.headless = True
        self.selenium = webdriver.Firefox(options=options)
        super(SeleniumTestCase, self).setUp()
        



    def tearDown(self):
        self.selenium.quit()
        super(SeleniumTestCase, self).tearDown()

    def test_login(self):

        selenium = self.selenium
        selenium.get(os.getenv('REDIRECT_URI') + reverse('classy:index'))

        username = selenium.find_element_by_name('username')
        password = selenium.find_element_by_name('password')

        username.send_keys(os.getenv('TEST_ACCOUNT_USERNAME'))
        password.send_keys(os.getenv('TEST_ACCOUNT_PASSWORD'))

        submit = selenium.find_element_by_name('login')

        submit.click()

        assert 'Welcome dev-tester' in selenium.page_source

        selenium.get(os.getenv('REDIRECT_URI') + reverse('classy:data'))

        assert 'What would you like to search for?' in selenium.page_source


        
