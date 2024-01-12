import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import pickle
import io



def main():

    pd.options.mode.chained_assignment = None  # default='warn'

    with open('playerLinks', 'rb') as pickle_file:
        playerLinks = pickle.load(pickle_file)

    trainingData = pd.DataFrame()
    for link in playerLinks:
        htmlStr = 'https://www.baseball-reference.com' + link
        try:
            response = requests.get(htmlStr)

            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find_all('table', attrs={'id' : 'batting_standard'})

            df_player = pd.read_html(io.StringIO(str(table)))[0]
            # print(link)
            rookie_season = get_rookie_season(df_player)
            war = get_War(soup)
            df_player['id'] = link
            rookie_season["WAR"] = war

            trainingData = pd.concat([trainingData, rookie_season.to_frame().T], ignore_index=True) # add this to the dataframe
            time.sleep(3.1)

            print(link)
        except:
            time.sleep(3.1)
            print('pitcher')
            
            
    trainingData.to_csv('data.csv', index=False)

def get_War(soup):
  highlights = soup.find("div", attrs={'class' : 'stats_pullout'})
  values = highlights.find('span', attrs={'class' : 'poptip', 'data-tip' : '<strong>Wins Above Replacement</strong><br>A single number that presents the number of wins the player added<br>to the team above what a replacement player (think AAA or AAAA) would add.<br>Scale for a single-season: 8+ MVP Quality, 5+ All-Star Quality, 2+ Starter,<br>0-2 Reserve, < 0 Replacement Level  <br>Developed by Sean Smith of BaseballProjection.com'})

  return float(values.find_next_sibling('p').get_text(strip=True))

def get_rookie_season(df_player):
  df_player = df_player[df_player["Lg"].isin(["AL", 'NL'])] # this filters out the minor league rows
  df_player["G"] = pd.to_numeric(df_player["G"]) # convert games to integer
  df_player = df_player[df_player["G"] >= 40] # filter to seasons over 40 games (rookie qualification)

  return df_player.iloc[0] # get the first 40 game season

def link_generation():
    playerLinks = []

    for letter in 'abcdefghijklmnopqrstuvwxyz': #abcdefghijklmnopqrstuvwxyz
        response = requests.get(f"https://www.baseball-reference.com/players/{letter}/") # get content from the page with a last names
        time.sleep(3.1)
        soup = BeautifulSoup(response.content, "html.parser")

        contentBlock = soup.find("div",
                            attrs={
                                "class": "section_content",
                                "id": "div_players_"
                                })
        allPlayers = contentBlock.find_all('p') # this is where the player information is contained

        for player in allPlayers:
            dates = re.search(r'\(\d{4}-(\d{4})\)', str(player)) # this regular expression extracts the last year a player played
            endDate = int(dates.group(1))
            # print(endDate)
            if endDate < 2023 and endDate >= 1940: # filter down the list
                playerLinks.append(player.find("a")['href']) # get the link to the player webpage

    print(len(playerLinks))

    with open('playerLinks', 'wb') as pickle_file:
        pickle.dump(playerLinks, pickle_file)


if __name__ == '__main__':
    main()