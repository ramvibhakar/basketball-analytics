# Basketball-Analytics
Analytics with NBA player salaries with data from [basketball-reference.com](http://www.basketball-reference.com). This is part of [IS5126: Hands on with Business Analytics](http://www.comp.nus.edu.sg/~phantq/IS5126/)

## Requirements

* Python 2.7
* BeautifulSoup 4.0
* SQLite 3

## Step 1: Scrapping the data

To scrap the data from [basketball-reference.com](http://www.basketball-reference.com) run the following scripts

*  **py player_crawler.py** : To extract the information about the players. The starting URL is [http://www.basketball-reference.com/players/](http://www.basketball-reference.com/players/). The output is generated as csv files **data/player\_basic\_profile_info.csv** and **data/player\_stats.csv** 
*  **py team_crawler.py** : To extract the team information and player salaries. The starting URL is [http://www.basketball-reference.com/teams/](http://www.basketball-reference.com/teams/). The output csv files are **data/player\_salary.csv**, **data/team\_basic\_profile\_info.csv** and **data/player\_stats.csv** 