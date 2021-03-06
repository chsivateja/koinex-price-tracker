#!/usr/bin/python
from __future__ import print_function
import os, sys, logging
import socket

ROOT_FOLDER = os.path.realpath(os.path.dirname(__file__))
ROOT_FOLDER = ROOT_FOLDER[:ROOT_FOLDER.rindex('/')]

if ROOT_FOLDER not in sys.path:
    sys.path.insert(1, ROOT_FOLDER + '/')

from web_crawler import Crawler
from google_sheets_helper import GoogleSheetsHelper
from helper import Helper

log_file = 'koinex.log'
logging.basicConfig(filename=log_file,level=logging.ERROR)


def main():
    crawl = None
    try:
        helper = Helper()
        price_data = helper.get_koinex_price()
        sheet = GoogleSheetsHelper()
        price_alert_values = sheet.get_price_alerts()
        helper.update_price_alerts(price_alert_values)
        sheet.update_koinex_google_sheet(price_data)
        transaction_required = helper.save_price_data_in_redis(price_data)
        print(transaction_required)
        if transaction_required:
            for coin_data in transaction_required['buy_coins']:
                helper.send_slack_alert(coin_data['coin'], coin_data['price'])
            for coin_data in transaction_required['sell_coins']:
                helper.send_slack_alert(coin_data['coin'], coin_data['price'])
    except Exception as e:
        logging.error("Error")

    try:
        if crawl:
            crawl.driver.close()
    except:
        pass

if __name__ == '__main__':
    main()
