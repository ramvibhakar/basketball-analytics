__author__ = 'group11'

import logging
import robotparser
import urllib
from bs4 import BeautifulSoup, SoupStrainer
import csv
import string
import time
import re
import sys
import traceback

# some constants defined here
SITE_HOME = "http://www.basketball-reference.com"
PLAYER_START_URL = SITE_HOME + "/players/{0}"
PLAYER_BASIC_CSV = 'data/player_basic_profile_info.csv'
PLAYER_STATS_CSV = 'data/player_stats.csv'

# as per the terms and agreements of basketball-reference.com it is mandatory to adhere to robots.txt
robot = robotparser.RobotFileParser()
robot.set_url(SITE_HOME + "/robots.txt")
robot.read()

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs/howba_assignment1.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# This function returns the list of player URL's from the start URL
# and writes the basic player info into /data/player_basic_profile_info.csv


def get_player_basic_info():
    logger.info("Starting player basic info")
    # exclude 'x' as no player names start with 'x'
    player_starting_letters = string.lowercase[:23] + string.lowercase[24:26]

    return_urls = []
    header = ['url', 'name', 'from', 'to', 'pos', 'ht', 'wt', 'dob', 'college', 'active']

    with open(PLAYER_BASIC_CSV, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(header)

    if robot.can_fetch("*", PLAYER_START_URL):
        for i in xrange(0, len(player_starting_letters)):
            url = PLAYER_START_URL.format(player_starting_letters[i])
            logger.debug("Scrapping url: " + url)
            try:
                request = urllib.urlopen(url)
                table_strainer = SoupStrainer('table', {'id': 'players'})
                soup = BeautifulSoup(request.read(), parse_only=table_strainer)

                urls = soup.find_all(href=re.compile('/players/[a-zA-Z]/[^\.]*.html'))
                all_players_info = []
                for link in urls:
                    player_info = [link['href']]
                    return_urls.append(link['href'])
                    tr = link.parent.parent
                    active = False
                    if link.parent.name == 'strong':
                        tr = link.parent.parent.parent
                        active = True
                    td = tr.find_all('td')
                    for data in td:
                        player_info.append(data.text)
                    player_info.append(active)
                    all_players_info.append(player_info)
                with open(PLAYER_BASIC_CSV, 'a') as fp:
                    a = csv.writer(fp, delimiter=',')
                    a.writerows(all_players_info)
                time.sleep(1)
            except:
                logger.error("Exception while scrapping: "+url)
                logger.error(sys.exc_info()[0])
                logger.error(traceback.format_exc())
                continue
    logger.info("Completed player basic info")
    return return_urls


def get_player_statistics(urls):

    logger.info("Starting player statistics")
    header = ['player_url', 'Season', 'Age', 'Tm_url', 'Tm', 'Lg', 'Pos', 'G', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

    with open(PLAYER_STATS_CSV, 'w') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerow(header)

    if robot.can_fetch("*", PLAYER_START_URL):
        for url in urls:
            try:
                logger.debug("Scrapping url: " + url)
                request = urllib.urlopen(SITE_HOME + url)
                table_strainer = SoupStrainer('table', {'id': 'totals'})
                soup = BeautifulSoup(request.read(), parse_only=table_strainer)

                rows = soup.find_all('tr')
                all_player_stats = []
                for row in rows[1:]:
                    cells = row.find_all('td')
                    player_stat = [url]
                    i = 0
                    for cell in cells:
                        if i == 2:
                            if cell.find('a'):
                                season_link =cell.find('a')['href']
                                pat = re.compile('(/teams/[a-zA-Z]+/)[\d\d\d\d.html]?')
                                team_link_wo_season = re.findall(pat, season_link)
                                if team_link_wo_season:
                                    player_stat.append(team_link_wo_season[0])
                                else:
                                    player_stat.append('')
                            else:
                                player_stat.append('')
                        player_stat.append(cell.text.encode('utf-8').strip())
                        i += 1
                    all_player_stats.append(player_stat)
                with open(PLAYER_STATS_CSV, 'a') as fp:
                    a = csv.writer(fp, delimiter=',')
                    a.writerows(all_player_stats)
                time.sleep(1)
            except:
                logger.error("Exception while scrapping: "+url)
                logger.error(sys.exc_info()[0])
                logger.error(traceback.format_exc())
                continue
        logger.info("Completed player statistics")

player_pages = get_player_basic_info()
get_player_statistics(player_pages)

