"""
This script gets data od currency from the site https://trade.pdax.ph/
and uploads it to the google sheet document
"""

import gspread

from loguru import logger
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from time import gmtime, strftime, sleep

url = 'https://trade.pdax.ph/'
firefox_driver_path = 'firefox_driver/geckodriver'

# use creds to create a client to interact with the Google Drive API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# currency mapping
currency = {'BTC': '//*[@id="select_option_8"]',
            'ETH': '//*[@id="select_option_9"]',
            'XRP': '//*[@id="select_option_10"]',
            'BCH': '//*[@id="select_option_11"]',
            'LTC': '//*[@id="select_option_12"]',
            'USDT': '//*[@id="select_option_13"]'}


def get_data_from_site():
    """
    Gets data from the site: https://trade.pdax.ph/
    :return: dict
      example: {'BTC': '15,001.00000',
                'ETH': '1,123,040.00000',
                'XRP': '30,421.30977',
                'BCH': '23.20000',
                'LTC': '15,001.00000',
                'USDT': '5,252.48227'}
    """
    firefox_options = Options()
    # if disabled runs firefox in the memory
    firefox_options.add_argument("--headless")

    driver = webdriver.Firefox(executable_path=firefox_driver_path, options=firefox_options)
    driver.get(url)
    sleep(5)

    result = {}
    for key, value in currency.items():
        delay = 10  # seconds
        try:
            # select currency
            driver.find_elements_by_xpath(
                '/html/body/md-content/md-content/section/div[2]/section/div/div/section[1]/div/section/div/figure[1]/md-select/md-select-value/span[1]')[0].click()
            driver.find_elements_by_xpath(value)[0].click()
            # cost result
            cost_result = WebDriverWait(
                driver,
                delay).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '/html/body/md-content/md-content/section/div[2]/section/div/div/section[1]/div/div[1]/figure[1]/span[2]/strong')))
            cost_result = cost_result.text.split('₱')[-1]

            logger.info('{}: {}', key, cost_result)
            result[key] = cost_result
        except TimeoutException:
            logger.error("Loading took too much time!")
    return result


def upload_to_google(data):
    """
    Uploads data from the site to the google page

    :param data: dict
      example: {'BTC': '15,001.00000',
                'ETH': '1,123,040.00000',
                'XRP': '30,421.30977',
                'BCH': '23.20000',
                'LTC': '15,001.00000',
                'USDT': '5,252.48227'}
    :return: None
    """
    gc = gspread.service_account(filename='/home/runner/secrets/eliska-trade.json')

    # now_time_filename = strftime("%Y-%m-%d", gmtime())
    sh = gc.create('trade_pdax_ph')
    sh.share('turivniy@gmail.com', perm_type='user', role='writer')

    worksheet = sh.get_worksheet(0)
    now_time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    worksheet.update('A2', now_time)
    worksheet.update('B2', data['BTC'])
    worksheet.update('C2', data['ETH'])
    worksheet.update('D2', data['XRP'])
    worksheet.update('E2', data['BCH'])
    worksheet.update('F2', data['LTC'])
    worksheet.update('G2', data['USDT'])


if __name__ == '__main__':
    res = get_data_from_site()
    logger.info(res)
    upload_to_google(res)
