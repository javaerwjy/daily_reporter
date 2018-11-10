#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from email.utils import parseaddr, formataddr
from email.mime.text import MIMEText
from email.header import Header
from email import encoders
import subprocess
import smtplib
import time
import datetime
import os
import configparser

config = {}


def send_email(content, from_addr, to_addr, cc_addr, subject, password):
    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = u'<%s>' % from_addr
    msg['To'] = u'<%s>' % to_addr
    msg['Cc'] = cc_addr
    msg['Subject'] = subject

    smtp = smtplib.SMTP_SSL(config['SMTP_SERVER'], config['SMTP_SERVER_PORT'])
    smtp.set_debuglevel(1)
    smtp.ehlo(config['SMTP_SERVER'])
    smtp.login(from_addr, password)
    smtp.sendmail(from_addr, to_addr.split(',') +
                  cc_addr.split(','), msg.as_string())


def getMailContent():
    content = ""

    # 查询trello complete list
    url = "https://api.trello.com/1/lists/%s/cards?key=%s&token=%s" % (
        config['TRELLO_COMPLETE_LIST_ID'], config['TRELLO_KEY'], config['TRELLO_TOKEN'])
    response = requests.request("GET", url)
    json_obj = json.loads(response.text)
    cards = list(filter(filter_card, json_obj))

    if len(cards) > 0:
        content = content + "From Trello:"
        content = content + "<ul>"
        for card in cards:
            content = content + '<li>' + card['name'] + '</li>'
        content = content + "</ul>"

    # 查询git commit
    add_from_git = False
    for path in config['PROJECT_PATHS'].split(','):
        os.chdir(path)
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        git_cmd = 'git log --author=wangyuanjing --after="%s" --pretty=format:"%s"' % (
            yesterday, "%s")
        commit_lines = subprocess.getstatusoutput(git_cmd)[1]
        lines = list(filter(filter_commit, commit_lines.split('\n')))
        if len(lines) > 0:
            if not add_from_git:
                content = content + "From Git:"
                add_from_git = True
            content = content + "<ul>"
            for line in lines:
                if len(line) > 0:
                    content = content + '<li>' + line + '</li>'
            content = content + "</ul>"
    return content


def filter_commit(val):
    return 'Merge' not in val and len(val) > 0


def filter_card(val):
    date_str = val['dateLastActivity'][0:10] + val['dateLastActivity'][11:19]
    today = datetime.date.today().strftime("%Y-%m-%d")
    card_day = (datetime.datetime.strptime(
        date_str, '%Y-%m-%d%H:%M:%S') + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
    return today == card_day


def read_config(conf):
    config['SMTP_SERVER'] = conf.get("config", "SMTP_SERVER")
    config['SMTP_SERVER_PORT'] = conf.get("config", "SMTP_SERVER_PORT")
    config['MINE_MAIL_ADDRESS'] = conf.get("config", "MINE_MAIL_ADDRESS")
    config['PASSWORD'] = conf.get("config", "PASSWORD")
    config['RECEIVER'] = conf.get("config", "RECEIVER")
    config['CC'] = conf.get("config", "CC")
    config['PROJECT_PATHS'] = conf.get("config", "PROJECT_PATHS")
    config['TRELLO_KEY'] = conf.get("config", "TRELLO_KEY")
    config['TRELLO_TOKEN'] = conf.get("config", "TRELLO_TOKEN")
    config['TRELLO_COMPLETE_LIST_ID'] = conf.get(
        "config", "TRELLO_COMPLETE_LIST_ID")


if __name__ == '__main__':
    conf = configparser.SafeConfigParser()
    fp = r"/Users/wjy/Documents/pdd/daily_reporter/daily_reporter.ini"
    conf.read(fp)
    read_config(conf)
    content = getMailContent()
    if len(content) > 0:
        send_email(content, config['MINE_MAIL_ADDRESS'], config['RECEIVER'], config['CC'], "日报-望远镜-%s" %
                   time.strftime("%Y%m%d", time.localtime()), config['PASSWORD'])
