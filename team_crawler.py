__author__ = 'group11'

import logging
import robotparser
import urllib
from bs4 import BeautifulSoup
import csv
import time
import re
import sys
import traceback

# some constants defined here
SITE_HOME = "http://www.basketball-reference.com"
TEAM_START_URL = SITE_HOME + "/teams/"
TEAM_BASIC_CSV = 'data/team_basic_profile_info.csv'
TEAM_STATS_CSV = 'data/team_stats.csv'
PLAYER_SALARIES_CSV = 'data/player_salary.csv'

# as per the terms and agreements of basketball-reference.com it is mandatory to adhere to robots.txt
robot = robotparser.RobotFileParser()
robot.set_url(SITE_HOME + "/robots.txt")
robot.read()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/howba_assignment1_team_crawler.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_team_info():
    logger.info("Started getting team basic info")
    return_urls = []
    if robot.can_fetch("*", TEAM_START_URL):
        request = urllib.urlopen(TEAM_START_URL)
        soup = BeautifulSoup(request.read())
        active_teams = soup.find_all('table', {'id': 'active'})
        active_rows = active_teams[0].find_all('tr', attrs={'class': 'full_table'})
        all_teams = []
        header = ['url', 'name', 'lg', 'from', 'to', 'years', 'games', 'wins', 'losses', 'wlpercent', 'playoffs', 'div', 'conf', 'champ','defunct']
        for active_row in active_rows:
            data = active_row.find_all('td')
            row_data = []
            for d in data:
                if d.find('a'):
                    row_data.append(d.find('a')['href'])
                    return_urls.append(d.find('a')['href'])
                    row_data.append(d.text)
                else:
                    row_data.append(d.text)
            row_data.append('0')
            all_teams.append(row_data)
        defunct_teams = soup.find_all('table', {'id': 'defunct'})
        defunct_rows = defunct_teams[0].find_all('tr', attrs={'class': 'full_table'})
        for defunct_row in defunct_rows:
            data = defunct_row.find_all('td')
            row_data = []
            for d in data:
                if d.find('a'):
                    row_data.append(d.find('a')['href'])
                    return_urls.append(d.find('a')['href'])
                    row_data.append(d.text)
                else:
                    row_data.append(d.text)
            row_data.append('1')
            all_teams.append(row_data)
        with open(TEAM_BASIC_CSV, 'wb') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerow(header)
            a.writerows(all_teams)
    logger.info("Completed getting team basic info")
    return return_urls


def get_team_stats(urls):
    logger.info("Started getting team statistics")
    header = ['url', 'Season', 'Lg', 'Team', 'W', 'L', 'W/L%', 'Finish',	'SRS', 'Pace', 'Rel_Pace', 'ORtg', 'Rel_ORtg', 'DRtg', 'Rel_DRtg', 'Playoffs', 'Coaches', 'Top_WS','top_ws_url']
    with open(TEAM_STATS_CSV, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(header)
    alllinks = []
    for url in urls:
        request = urllib.urlopen(SITE_HOME + url)
        logger.debug("Scrapping url: " + url)
        try:
            html = request.read()
            soup = BeautifulSoup(html)
            active_teams = soup.find_all('table', {'class': 'sortable  stats_table'})
            tags = active_teams[0].find_all(href=re.compile('/teams/[a-zA-Z]+/\d\d\d\d.html'))
            links = [tag['href'] for tag in tags]
            uniquelinks = set(links)
            for link in uniquelinks:
                alllinks.append(link)
            active_rows = active_teams[0].find_all('tr')
            all_teams = []
            for active_row in active_rows[1:]:
                data = active_row.find_all('td')
                row_data = [url]
                i = 0
                for d in data:
                    if i == 16:
                        ws_url = d.find('a')['href']
                        row_data.append(d.text.encode('utf-8').strip())
                        row_data.append(ws_url)
                    else:
                        row_data.append(d.text.encode('utf-8').strip())
                    i += 1
                all_teams.append(row_data)
            with open(TEAM_STATS_CSV, 'a') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(all_teams)
        except:
            logger.error("Exception while scrapping: "+url)
            logger.error(sys.exc_info()[0])
            logger.error(traceback.format_exc())
            continue
        time.sleep(1)
    logger.info("Completed getting team statistics")
    return alllinks


def get_team_salary(urls):
    logger.info("Started getting player salaries from team seasons")
    header = ['team_url', 'season', 'rank', 'url', 'name', 'salary']
    with open(PLAYER_SALARIES_CSV, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(header)
    for url in urls:
        logger.debug("Scrapping url: " + url)
        try:
            request = urllib.urlopen(SITE_HOME + url)
            html = request.read()
            soup = BeautifulSoup(html)
            salary_table = soup.find_all('table', {'id': 'salaries'})
            try:
                rows = salary_table[0].find_all('tr')
            except:
                continue        # For some seasons the salary info is not available
            pat = re.compile(r'<title>(\d\d\d\d-\d\d)')   # Getting season from title
            season = re.findall(pat, html)
            all_items = []
            for row in rows[1:]:
                data = row.find_all('td')
                row_data = [url[:len(url)-9], season[0]]
                i = 0
                for d in data:
                    if i == 1:
                        if d.find('a'):
                            row_data.append(d.find('a')['href'])
                        else:
                            row_data.append('')
                    row_data.append(d.text.encode('utf-8').strip())
                    i += 1
                all_items.append(row_data)
            with open(PLAYER_SALARIES_CSV, 'a') as fp:
                a = csv.writer(fp, delimiter=',')
                a.writerows(all_items)
            time.sleep(1)
        except:
            logger.error("Exception while scrapping: "+url)
            logger.error(sys.exc_info()[0])
            logger.error(traceback.format_exc())
            continue
        logger.info("Completed getting player salaries from team seasons")

team_urls = get_team_info()
season_urls = get_team_stats(team_urls)
get_team_salary(season_urls)