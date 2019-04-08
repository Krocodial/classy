from selenium import webdriver
from django.test import TestCase
from selenium.webdriver.firefox.options import Options
from django.urls import reverse
import os, time
from selenium.webdriver.common.keys import Keys
import requests
from requests.auth import HTTPBasicAuth
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select

class DataTestCase(TestCase):
    def setUp(self):
        self.classifications = ['UNCLASSIFIED', 'PUBLIC', 'CONFIDENTIAL', 'PROTECTED A', 'PROTECTED B', 'PROTECTED C']
        options = Options()
        options.headless = False
        selenium = webdriver.Firefox(options=options)
        domain = os.getenv('REDIRECT_URI')

        #Log the dev-tester account in and establish the session
        selenium.get(domain + reverse('classy:index'))
        username = selenium.find_element_by_name('username')
        password = selenium.find_element_by_name('password')
        username.send_keys(os.getenv('TEST_ACCOUNT_USERNAME'))
        password.send_keys(os.getenv('TEST_ACCOUNT_PASSWORD'))
        selenium.find_element_by_name('login').click()
        self.selenium = selenium
        self.domain = domain


    def tearDown(self):
        self.selenium.quit()

    def test_login(self):

        selenium = self.selenium
        domain = self.domain

        selenium.get(domain + reverse('classy:index'))
        time.sleep(5)
        assert 'Welcome dev-tester' in selenium.page_source

    
    def test_no_data_permissions(self):

        browser = self.selenium
        domain = self.domain
        
        browser.get(domain + reverse('classy:data'))

        browser.find_element_by_link_text('Advanced Search').click()

        datasource = browser.find_element_by_name('data_source')
        schema = browser.find_element_by_name('schema')
        table = browser.find_element_by_name('table')
        column = browser.find_element_by_name('column')

        datasource.send_keys('dbq01')
        schema.send_keys('DBSNMP')

        schema.submit()
        time.sleep(5)

        assert '<td>DBSNMP</td>' not in browser.page_source

    def test_data_permissions(self):

        browser = self.selenium
        domain = self.domain

        browser.get(domain + reverse('classy:data'))
        browser.find_element_by_link_text('Advanced Search').click()

        datasource = browser.find_element_by_name('data_source')
        schema = browser.find_element_by_name('schema')
        table = browser.find_element_by_name('table')
        column = browser.find_element_by_name('column')

        datasource.send_keys('dbq01')
        schema.send_keys('backup')
        table.send_keys('bkup_gnrl_invc_txn')
        column.send_keys('data')

        column.submit()
        time.sleep(5)

        assert '<td>DATA</td>' in browser.page_source

    def test_data_modification(self):
        browser = self.selenium
        domain = self.domain

        for clas in self.classifications:

            browser.get(domain + reverse('classy:data'))
            browser.find_element_by_link_text('Advanced Search').click()

            ds = browser.find_element_by_name('data_source')
            sc = browser.find_element_by_name('schema')
            ta = browser.find_element_by_name('table')
            co = browser.find_element_by_name('column')

            ds.send_keys('maltest4.database')
            sc.send_keys('DBSNMP')
            ta.send_keys('CNLDATA')
            co.send_keys('TAGS')

            co.submit()
            time.sleep(3)

            browser.find_element_by_xpath("//table[@id='data-table']/tbody/tr[1]/td[1]/button").click()
            time.sleep(1)
            select = Select(browser.find_element_by_xpath("//select[@id='1']"))
            select.select_by_visible_text(clas)
            browser.find_element_by_id('subby').click()
            browser.find_element_by_id('finSubby').click()
            time.sleep(1)
            assert 'Success!</strong> Changes submitted' in browser.page_source


            browser.get(domain + reverse('classy:data'))
            browser.find_element_by_link_text('Advanced Search').click()

            ds = browser.find_element_by_name('data_source')
            sc = browser.find_element_by_name('schema')
            ta = browser.find_element_by_name('table')
            co = browser.find_element_by_name('column')

            ds.send_keys('maltest4.database')
            sc.send_keys('DBSNMP')
            ta.send_keys('CNLDATA')
            co.send_keys('TAGS')

            co.submit()
            time.sleep(3)

            browser.find_element_by_xpath("//table[@id='data-table']/tbody/tr[1]/td[1]/button").click()
            time.sleep(1)
            select = Select(browser.find_element_by_xpath("//select[@id='1']"))

            assert select.first_selected_option.text == clas

    '''
    def test_mass_data_modification(self): 
        browser = self.selenium
        domain = self.domain

        for clas in self.classifications:
            browser.get(domain + reverse('classy:data'))
        
            q = browser.find_element_by_id('id_query')

            q.send_keys('')
            q.submit()

            time.sleep(2)

            row1 = browser.find_element_by_xpath("//table[@id='data-table']/tbody/tr[1]")
            row2 = browser.find_element_by_id('2')
            row3 = browser.find_element_by_id('3')

            ActionChains(browser).key_down(Keys.CONTROL).click(row1).click(row2).click(row3).key_up(Keys.CONTROL).perform()

            browser.find_element_by_id('edito').click()
            select = Select(browser.find_element_by_xpath("//select[@id='newC']"))
            select.select_by_visible_text(clas)
            browser.find_element_by_id('changeC').click()
            time.sleep(1)
            browser.find_element_by_id('subby').click()
            browser.find_element_by_id('finSubby').click()

            assert 'Success!</strong> Changes submitted' in browser.page_source


            browser.get(domain + reverse('classy:data'))
        
            q = browser.find_element_by_id('id_query')

            q.send_keys('')
            q.submit()

            row1 = browser.find_element_by_xpath("//tr[@id='1']/td[6]").text
            row2 = browser.find_element_by_xpath("//tr[@id='2']/td[6]").text
            row3 = browser.find_element_by_xpath("//tr[@id='3']/td[6]").text

            assert row1 == row2 == row3 == clas
        #ActionChains(browser).key_down(Keys.CONTROL).click(row).key_up(Keys.CONTROL).perform()
    '''




