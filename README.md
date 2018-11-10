# daily_reporter
发周报

# Usage

1.vim /daily_reporter.ini
```
[config]
SMTP_SERVER=smtp.exmail.qq.com
SMTP_SERVER_PORT=465
MINE_MAIL_ADDRESS=
PASSWORD=
RECEIVER=
CC=
PROJECT_PATHS=/Users/wjy/Documents/volantis/lith-ui,/Users/wjy/Documents/volantis/lith
TRELLO_KEY=
TRELLO_TOKEN=
TRELLO_COMPLETE_LIST_ID=
```

2.crontab -e 添加定时任务
```
LANG=de_DE.UTF-8
LANGUAGE=de
LC_CTYPE=de_DE.UTF-8
PYTHONIOENCODING=utf8
*/1 * * * * source /Users/wjy/.zshrc && python3 /Users/wjy/Documents/pdd/daily_reporter/daily_reporter.py 2>&1 | tee -a /Users/wjy/daily_reporter.log
```
