# -*- coding: utf-8 -*-

'''
    Moviedrive Addon
    Copyright (C) 2023 heg, vargalex

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, sys, re, xbmc, xbmcgui, xbmcplugin, xbmcaddon, locale, base64
from bs4 import BeautifulSoup
import requests
import random
import urllib.parse
from resources.lib.modules.utils import py2_decode, py2_encode
import html

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

base_url = 'https://moviedrive.hu'

BR_VERS = [
    ['%s.0' % i for i in range(18, 43)],
    ['61.0.3163.79', '61.0.3163.100', '62.0.3202.89', '62.0.3202.94', '63.0.3239.83', '63.0.3239.84', '64.0.3282.186', '65.0.3325.162', '65.0.3325.181', '66.0.3359.117', '66.0.3359.139',
     '67.0.3396.99', '68.0.3440.84', '68.0.3440.106', '68.0.3440.1805', '69.0.3497.100', '70.0.3538.67', '70.0.3538.77', '70.0.3538.110', '70.0.3538.102', '71.0.3578.80', '71.0.3578.98',
     '72.0.3626.109', '72.0.3626.121', '73.0.3683.103', '74.0.3729.131'],
    ['11.0']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']

ind_ex = random.randrange(len(RAND_UAS))
r_u_a = RAND_UAS[ind_ex].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[ind_ex]))

movie_drive_headers = {
    'User-Agent': r_u_a,
}

movie_drive_session = requests.Session()
movie_drive_session.headers.update(movie_drive_headers)

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus
else:
    from xbmc import translatePath
    from urlparse import urlparse
    from urllib import quote_plus

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "hu_HU.UTF-8")
        except:
            try:
                locale.setlocale(locale.LC_ALL, "")
            except:
                pass
        self.base_path = py2_decode(translatePath(xbmcaddon.Addon().getAddonInfo('profile')))
        self.searchFileName = os.path.join(self.base_path, "search.history")

    def root(self):
        self.addDirectoryItem("Filmek", "only_movies", '', 'DefaultFolder.png')
        self.addDirectoryItem("Sorozatok", "only_series", '', 'DefaultFolder.png')
        self.addDirectoryItem("Kategóriák", "categories", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()

    def getCategories(self):
        page = movie_drive_session.get(f"{base_url}/filmek/")
        soup = BeautifulSoup(page.text, 'html.parser')

        cat_s = soup.find('div', class_='genre__dropdawn_menu')
        categories = cat_s.find_all('div', class_='genre__dropdawn_item sign__group--checkbox genre__checkbox')

        for category in categories:
            checkbox = category.find('input')
            value = checkbox['value'].strip()
            enc_value = urllib.parse.quote(value, safe=':/')
            enc_link = f'{base_url}/filmek/?tag={enc_value}'

            self.addDirectoryItem(f"{value}", f'items&url={enc_link}', '', 'DefaultFolder.png')

        self.endDirectory()

    def getItems(self, url):
        page = movie_drive_session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        cards = soup.find_all('div', class_='card')
        
        for card in cards:
            card_cover = card.find('a', class_='card__cover')
            card_link = card_cover['href']

            card_type = card_cover.find('span', class_='card__type')
            card_type_text = card_type.text

            if card_type_text == 'Film':
                card_type_text = f'{card_type_text:^10}'
            
            img = card_cover.find('img')
            img_src = img['src']
            
            card_content = card.find('div', class_='card__content')
            card_title = card_content.find('h3', class_='card__title')
            card_title_text = card_title.text
            card_rate = card_content.find('span', class_='card__rate')
            card_rate_text = card_rate.text
            
            ##### requ card_link
            page_2 = movie_drive_session.get(card_link)
            soup_2 = BeautifulSoup(page_2.text, 'html.parser')

            pontszam = soup_2.select_one('.card__rate').get_text(strip=True)

            kiadas_ev_element = None
            hossz_element = None
            
            for li in soup_2.select('.card__meta li'):
                text = li.get_text()
                if "Kiadás év:" in text:
                    kiadas_ev_element = li
                elif "Hossz:" in text:
                    hossz_element = li
            
            kiadas_ev = "xxxx"
            if kiadas_ev_element:
                kiadas_ev_text = kiadas_ev_element.find('span').next_sibling.strip()
                kiadas_ev_parts = kiadas_ev_text.split(" - ")
                if kiadas_ev_parts:
                    kiadas_ev = kiadas_ev_parts[0]
            
            hossz = "N/A"
            if hossz_element:
                hossz = hossz_element.find('span').next_sibling.strip()
            
            tartalom = soup_2.select_one('.card__description').get_text(strip=True)

            if card_type_text == 'Sorozat':
                self.addDirectoryItem(f'{card_type_text} | [B]{card_title_text} - {kiadas_ev}[/B]', f'get_series_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
            elif card_type_text:
                self.addDirectoryItem(f'{card_type_text} | [B]{card_title_text} - {kiadas_ev}[/B]', f'get_movie_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
        
        try:
            next_page = soup.find('li', class_='paginator__item--next').find('a')['href']
            next_page = html.unescape(next_page)
            next_page_number = next_page.split('&')[0]
            
            try:
                next_page_tag = next_page.split('&tag=')[1]
                enc_next_page_tag = urllib.parse.quote(next_page_tag, safe=':/')
                
                next_page_link = f'https://moviedrive.hu/filmek/{next_page_number}&tag={enc_next_page_tag}'
            except IndexError:
                next_page_link = f'https://moviedrive.hu/filmek/{next_page}'
            
            self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Moviedrive | getItems | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getOnlyMovies(self):
        page = movie_drive_session.get(f"{base_url}/filmek/?tag=&type=Film")
        soup = BeautifulSoup(page.text, 'html.parser')

        cards = soup.find_all('div', class_='card')
        
        for card in cards:
            card_cover = card.find('a', class_='card__cover')
            card_link = card_cover['href']
            
            card_type = card_cover.find('span', class_='card__type')
            card_type_text = card_type.text

            if card_type_text == 'Film':
                card_type_text = f'{card_type_text:^10}'
            
            img = card_cover.find('img')
            img_src = img['src']
            
            card_content = card.find('div', class_='card__content')
            card_title = card_content.find('h3', class_='card__title')
            card_title_text = card_title.text
            card_rate = card_content.find('span', class_='card__rate')
            card_rate_text = card_rate.text
            
            ##### requ card_link
            page_2 = movie_drive_session.get(card_link)
            soup_2 = BeautifulSoup(page_2.text, 'html.parser')

            pontszam = soup_2.select_one('.card__rate').get_text(strip=True)

            kiadas_ev_element = None
            hossz_element = None
            
            for li in soup_2.select('.card__meta li'):
                text = li.get_text()
                if "Kiadás év:" in text:
                    kiadas_ev_element = li
                elif "Hossz:" in text:
                    hossz_element = li
            
            kiadas_ev = "xxxx"
            if kiadas_ev_element:
                kiadas_ev_text = kiadas_ev_element.find('span').next_sibling.strip()
                kiadas_ev_parts = kiadas_ev_text.split(" - ")
                if kiadas_ev_parts:
                    kiadas_ev = kiadas_ev_parts[0]
            
            hossz = "N/A"
            if hossz_element:
                hossz = hossz_element.find('span').next_sibling.strip()
            
            tartalom = soup_2.select_one('.card__description').get_text(strip=True)            
            ###
            
            self.addDirectoryItem(f'[B]{card_title_text} - {kiadas_ev}[/B]', f'get_movie_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
        
        try:
            next_page = soup.find('li', class_='paginator__item--next').find('a')['href']
            next_page = html.unescape(next_page)
            next_page_link = f'https://moviedrive.hu/filmek/{next_page}'
            
            self.addDirectoryItem('[I]Következő oldal[/I]', f'movie_items&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Moviedrive | getOnlyMovies | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        
        self.endDirectory('movies')

    def getOnlySeries(self):
        page = movie_drive_session.get(f"{base_url}/filmek/?p=1&type=Sorozat")
        soup = BeautifulSoup(page.text, 'html.parser')

        cards = soup.find_all('div', class_='card')
        
        for card in cards:
            
            card_cover = card.find('a', class_='card__cover')
            card_link = card_cover['href']
            
            card_type = card_cover.find('span', class_='card__type')
            card_type_text = card_type.text

            if card_type_text == 'Film':
                card_type_text = f'{card_type_text:^10}'
            
            img = card_cover.find('img')
            img_src = img['src']
            
            card_content = card.find('div', class_='card__content')
            card_title = card_content.find('h3', class_='card__title')
            card_title_text = card_title.text
            card_rate = card_content.find('span', class_='card__rate')
            card_rate_text = card_rate.text
            
            ##### requ card_link
            page_2 = movie_drive_session.get(card_link)
            soup_2 = BeautifulSoup(page_2.text, 'html.parser')

            pontszam = soup_2.select_one('.card__rate').get_text(strip=True)

            kiadas_ev_element = None
            hossz_element = None
            
            for li in soup_2.select('.card__meta li'):
                text = li.get_text()
                if "Kiadás év:" in text:
                    kiadas_ev_element = li
                elif "Hossz:" in text:
                    hossz_element = li
            
            kiadas_ev = "xxxx"
            if kiadas_ev_element:
                kiadas_ev_text = kiadas_ev_element.find('span').next_sibling.strip()
                kiadas_ev_parts = kiadas_ev_text.split(" - ")
                if kiadas_ev_parts:
                    kiadas_ev = kiadas_ev_parts[0]
            
            hossz = "N/A"
            if hossz_element:
                hossz = hossz_element.find('span').next_sibling.strip()
            
            tartalom = soup_2.select_one('.card__description').get_text(strip=True)            
            ###            

            self.addDirectoryItem(f'[B]{card_title_text} - {kiadas_ev}[/B]', f'get_series_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
        
        try:
            next_page = soup.find('li', class_='paginator__item--next').find('a')['href']
            next_page = html.unescape(next_page)
            next_page_link = f'https://moviedrive.hu/filmek/{next_page}'
            
            self.addDirectoryItem('[I]Következő oldal[/I]', f'series_items&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Moviedrive | getOnlySeries | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        
        self.endDirectory('series')       

    def getMovieItems(self, url):
        page = movie_drive_session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        cards = soup.find_all('div', class_='card')
        
        for card in cards:
            card_cover = card.find('a', class_='card__cover')
            card_link = card_cover['href']
            
            card_type = card_cover.find('span', class_='card__type')
            card_type_text = card_type.text

            if card_type_text == 'Film':
                card_type_text = f'{card_type_text:^10}'
            
            img = card_cover.find('img')
            img_src = img['src']
            
            card_content = card.find('div', class_='card__content')
            
            card_title = card_content.find('h3', class_='card__title')
            card_title_text = card_title.text
            
            card_rate = card_content.find('span', class_='card__rate')
            card_rate_text = card_rate.text
            
            ##### requ card_link
            page_2 = movie_drive_session.get(card_link)
            soup_2 = BeautifulSoup(page_2.text, 'html.parser')

            pontszam = soup_2.select_one('.card__rate').get_text(strip=True)

            kiadas_ev_element = None
            hossz_element = None
            
            for li in soup_2.select('.card__meta li'):
                text = li.get_text()
                if "Kiadás év:" in text:
                    kiadas_ev_element = li
                elif "Hossz:" in text:
                    hossz_element = li
            
            kiadas_ev = "xxxx"
            if kiadas_ev_element:
                kiadas_ev_text = kiadas_ev_element.find('span').next_sibling.strip()
                kiadas_ev_parts = kiadas_ev_text.split(" - ")
                if kiadas_ev_parts:
                    kiadas_ev = kiadas_ev_parts[0]
            
            hossz = "N/A"
            if hossz_element:
                hossz = hossz_element.find('span').next_sibling.strip()
            
            tartalom = soup_2.select_one('.card__description').get_text(strip=True)            
            ###            

            self.addDirectoryItem(f'[B]{card_title_text} - {kiadas_ev}[/B]', f'get_movie_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
        
        try:
            next_page = soup.find('li', class_='paginator__item--next').find('a')['href']
            next_page = html.unescape(next_page)

            next_page_number = next_page.split('&')[0]
            next_page_link = f'https://moviedrive.hu/filmek/{next_page}'
            
            self.addDirectoryItem('[I]Következő oldal[/I]', f'movie_items&url={quote_plus(next_page_link)}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Moviedrive | getMovieItems | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getSeriesItems(self, url):
        page = movie_drive_session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        cards = soup.find_all('div', class_='card')

        for card in cards:
            card_cover = card.find('a', class_='card__cover')
            card_link = card_cover['href']
            
            card_type = card_cover.find('span', class_='card__type')
            card_type_text = card_type.text

            if card_type_text == 'Film':
                card_type_text = f'{card_type_text:^10}'
            
            img = card_cover.find('img')
            img_src = img['src']
            
            card_content = card.find('div', class_='card__content')
            card_title = card_content.find('h3', class_='card__title')
            card_title_text = card_title.text
            card_rate = card_content.find('span', class_='card__rate')
            card_rate_text = card_rate.text
            
            ##### requ card_link
            page_2 = movie_drive_session.get(card_link)
            soup_2 = BeautifulSoup(page_2.text, 'html.parser')

            pontszam = soup_2.select_one('.card__rate').get_text(strip=True)

            kiadas_ev_element = None
            hossz_element = None
            
            for li in soup_2.select('.card__meta li'):
                text = li.get_text()
                if "Kiadás év:" in text:
                    kiadas_ev_element = li
                elif "Hossz:" in text:
                    hossz_element = li
            
            kiadas_ev = "xxxx"
            if kiadas_ev_element:
                kiadas_ev_text = kiadas_ev_element.find('span').next_sibling.strip()
                kiadas_ev_parts = kiadas_ev_text.split(" - ")
                if kiadas_ev_parts:
                    kiadas_ev = kiadas_ev_parts[0]
            
            hossz = "N/A"
            if hossz_element:
                hossz = hossz_element.find('span').next_sibling.strip()
            
            tartalom = soup_2.select_one('.card__description').get_text(strip=True)
            ###            

            self.addDirectoryItem(f'[B]{card_title_text} - {kiadas_ev}[/B]', f'get_series_sources&url={card_link}', img_src, 'DefaultMovies.png', isFolder=True, meta={'title': card_title_text, 'plot': tartalom})
        
        try:
            next_page = soup.find('li', class_='paginator__item--next').find('a')['href']
            next_page = html.unescape(next_page)
            next_page_number = next_page.split('&')[0]
            next_page_link = f'https://moviedrive.hu/filmek/{next_page}'
            self.addDirectoryItem('[I]Következő oldal[/I]', f'series_items&url={next_page_link}', '', 'DefaultFolder.png')
        except AttributeError:
            xbmc.log(f'Moviedrive | getSeriesItems | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('series')

    def getMovieSources(self, url):
        page = movie_drive_session.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')

        embed_iframe = soup.find('iframe', {'id': 'player'})
        embed_src = embed_iframe['src']
        
        page_2 = movie_drive_session.get(embed_src)
        soup_2 = BeautifulSoup(page_2.text, 'html.parser')
        
        video_sources = re.findall(r"{src: '(.*?)', type: 'video/mp4', size: (\d+),}", str(soup_2))

        if video_sources:
            video_sources = [(quote_plus(link), int(size)) for link, size in video_sources]
            highest_size_source = max(video_sources, key=lambda x: x[1])
            highest_size_link, highest_size = highest_size_source

        else:
            xbmc.log(f'Moviedrive | getMovieSources | highest_size_link: No video sources found', xbmc.LOGINFO)

        poster_match = re.search(r"var poster = '(.*?)';", str(soup_2))
        if poster_match:
            poster_url = poster_match.group(1)
        else:
            xbmc.log(f'Moviedrive | getMovieSources | soup_2: No poster URL found', xbmc.LOGINFO)

        title_match = re.search(r"<span class='big-text'>(.*?)</span>", str(soup_2))
        if title_match:
            title = title_match.group(1)
        
        try:
            self.addDirectoryItem(f'[B]{highest_size}p - {title}[/B]', f'playmovie&url={highest_size_link}', poster_url, 'DefaultMovies.png', isFolder=False, meta={'title': title})
        except UnboundLocalError:
            xbmc.log(f'Moviedrive | getSeriesSources | name: No video sources found', xbmc.LOGINFO)
            notification = xbmcgui.Dialog()
            notification.notification("Moviedrive", "Törölt tartalom", time=5000)
        
        self.endDirectory('movies')

    def getSeriesSources(self, url):
        page = movie_drive_session.get(url)
        
        link_id = re.findall(r'id=(.*)', url)[0].strip()
        
        soup = BeautifulSoup(page.text, 'html.parser')

        evad_divs = soup.find_all('div', class_='evad')
        data = []
        
        previous_num_episodes = 0

        title = soup.select_one('.details__title').text.strip()
        
        rating = soup.select_one('.card__rate').text.strip()

        genre_elements = soup.select('.card__meta li:has(span:-soup-contains("Műfaj:")) a')
        genres = [genre.text.strip() for genre in genre_elements]
        
        cover = soup.find('div', class_='card__cover')
        if cover:
            img_cover = cover.find('img')
            if img_cover:
                poster = img_cover['src']
        
        big_cover = soup.find('div', class_='details__bg')
        if big_cover:
            big_poster = big_cover['data-bg']
        
        description = soup.select_one('.card__description--details').text.strip()

        series_details = {
            "Title": title,
            "Rating": rating,
            "Műfaj": genres,
            "Ismertető": description,
            "poster": poster,
            "big_poster": big_poster
        }
        
        data.append(series_details)
        
        for evad_div in evad_divs:
            button = evad_div.find('button')
            if button:
                onclick = button['onclick']
                season = button.find('span').text
                season_number = season.split()[0]

                link = onclick.split('`')[1]
        
                season_data = {
                    'Season': season_number,
                    'season_Link': link
                }

                season_link = link
                response_2 = movie_drive_session.get(season_link)
                soup_2 = BeautifulSoup(response_2.text, 'html.parser')

                season_number_clean = re.findall(r'(.*).', season_number)[0].strip()

                accordion = soup_2.find('div', class_='accordion')
                episode_buttons = accordion.find_all('button')

                epis = []
                start_episode_num = previous_num_episodes + 1

                for episode_button in episode_buttons:
                    episode_number = episode_button.text.strip()
                    embed_link = f"https://moviedrive.hu/embed/?type=sorozat&id={link_id}&ep={start_episode_num}"
                    ep_link = f"https://moviedrive.hu/sorozat/?id={link_id}&evad={season_number_clean}&ep={start_episode_num}"
        
                    episode_data = {
                        "episode": f"{title} - {season_number} ÉVAD {episode_number}",
                        "embed_link": embed_link,
                        "ep_link": ep_link
                    }
        
                    epis.append(episode_data)
                    start_episode_num += 1
        
                season_data['NumEpisodes'] = len(epis)
                season_data['episodes'] = epis

                previous_num_episodes += len(epis)
                
                data.append(season_data)
                
                plot = data[0]['Ismertető']
                
                try:
                    self.addDirectoryItem(f'[B]{season_data["Season"]} évad - {title}[/B]', f'episodes&url={quote_plus(season_link)}', poster, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': plot})
                except UnboundLocalError:
                    notification = xbmcgui.Dialog()
                    notification.notification("Moviedrive", "Törölt tartalom", time=5000)
                    xbmc.log(f'Moviedrive | getSeriesSources | name: No video sources found', xbmc.LOGINFO)

        self.endDirectory('series')

    def getEpisodes(self, url):
        page = movie_drive_session.get(url)
        
        link_id = re.findall(r'id=(.*)', url)[0].strip()
        
        soup = BeautifulSoup(page.text, 'html.parser')

        evad_divs = soup.find_all('div', class_='evad')
        data2 = []
        
        previous_num_episodes = 0

        title = soup.select_one('.details__title').text.strip()
        
        rating = soup.select_one('.card__rate').text.strip()

        genre_elements = soup.select('.card__meta li:has(span:-soup-contains("Műfaj:")) a')
        genres = [genre.text.strip() for genre in genre_elements]
        
        cover = soup.find('div', class_='card__cover')
        if cover:
            img_cover = cover.find('img')
            if img_cover:
                poster = img_cover['src']
        
        big_cover = soup.find('div', class_='details__bg')
        if big_cover:
            big_poster = big_cover['data-bg']
        
        description = soup.select_one('.card__description--details').text.strip()

        series_details = {
            "Title": title,
            "Rating": rating,
            "Műfaj": genres,
            "Ismertető": description,
            "poster": poster,
            "big_poster": big_poster
        }
        
        data2.append(series_details)

        for evad_div in evad_divs:
            button = evad_div.find('button')
            if button:
                onclick = button['onclick']
                season = button.find('span').text
                season_number = season.split()[0]

                link = onclick.split('`')[1]
        
                season_data = {
                    'Season': season_number,
                    'season_Link': link
                }
                
                season_link = link
                response_2 = movie_drive_session.get(season_link)
                soup_2 = BeautifulSoup(response_2.text, 'html.parser')

                season_number_clean = re.findall(r'(.*).', season_number)[0].strip()

                accordion = soup_2.find('div', class_='accordion')
                episode_buttons = accordion.find_all('button')

                episodes = []
                start_episode_num = previous_num_episodes + 1

                for episode_button in episode_buttons:
                    episode_number = episode_button.text.strip()
                    embed_link = f"https://moviedrive.hu/embed/?type=sorozat&id={link_id}&ep={start_episode_num}"
                    ep_link = f"https://moviedrive.hu/sorozat/?id={link_id}&evad={season_number_clean}&ep={start_episode_num}"
        
                    episode_data = {
                        "episode": f"{title} - {season_number} ÉVAD {episode_number}",
                        "embed_link": embed_link,
                        "ep_link": ep_link
                    }
        
                    episodes.append(episode_data)
                    start_episode_num += 1
        
                season_data['NumEpisodes'] = len(episodes)
                season_data['episodes'] = episodes

                previous_num_episodes += len(episodes)

                data2.append(season_data)

        
        poster_url = data2[0]['poster']
        plot = data2[0]['Ismertető']
        
        #find block with evad url in data2
        find_block = None
        
        for block in data2:
            if "season_Link" in block and block["season_Link"] == url:
                find_block = block
                break
        
        if find_block:
            for episode in find_block['episodes']:
                ep_name = episode['episode']
                embed_link = episode['embed_link']              
                
                #requests page_xx
                page_xx = movie_drive_session.get(embed_link)
                soup_xx = BeautifulSoup(page_xx.text, 'html.parser')

                video_sources = re.findall(r"{src: '(.*?)', type: 'video/mp4', size: (\d+),}", str(soup_xx))
                
                if video_sources:
                    video_sources = [(quote_plus(link), int(size)) for link, size in video_sources]
                    highest_size_source = max(video_sources, key=lambda x: x[1])
                    highest_size_link, highest_size = highest_size_source

                try:
                    self.addDirectoryItem(f'[B]{highest_size}p - {ep_name}[/B]', f'playmovie&url={highest_size_link}', poster_url, 'DefaultMovies.png', isFolder=False, meta={'title': ep_name, 'plot': plot})
                except UnboundLocalError:
                    notification = xbmcgui.Dialog()
                    notification.notification("Moviedrive", "Törölt tartalom", time=5000)
                    xbmc.log(f'Moviedrive | getEpisodes | name: No video sources found', xbmc.LOGINFO)                    

        else:
            xbmc.log(f'Moviedrive | getEpisodes | Block not found: {url}', xbmc.LOGINFO)

        self.endDirectory('episodes')

    def playMovie(self, url):
        xbmc.log(f'Moviedrive | playMovie | playing URL: {url}', xbmc.LOGINFO)

        play_item = xbmcgui.ListItem(path=url)
        play_item.setProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36")
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=play_item)

    def getSearches(self):
        self.addDirectoryItem('[COLOR lightgreen]Új keresés[/COLOR]', 'newsearch', '', 'DefaultFolder.png')
        try:
            file = open(self.searchFileName, "r")
            olditems = file.read().splitlines()
            file.close()
            items = list(set(olditems))
            items.sort(key=locale.strxfrm)
            if len(items) != len(olditems):
                file = open(self.searchFileName, "w")
                file.write("\n".join(items))
                file.close()
            for item in items:
                self.addDirectoryItem(item, f'items&url={base_url}/filmek/?q={item}', '', 'DefaultFolder.png')

            if len(items) > 0:
                self.addDirectoryItem('[COLOR red]Keresési előzmények törlése[/COLOR]', 'deletesearchhistory', '', 'DefaultFolder.png')
        except:
            pass
        self.endDirectory()

    def deleteSearchHistory(self):
        if os.path.exists(self.searchFileName):
            os.remove(self.searchFileName)

    def doSearch(self):
        search_text = self.getSearchText()
        if search_text != '':
            if not os.path.exists(self.base_path):
                os.mkdir(self.base_path)
            file = open(self.searchFileName, "a")
            file.write(f"{search_text}\n")
            file.close()
            self.getItems(f"{base_url}/filmek/?q={search_text}")

    def getSearchText(self):
        search_text = ''
        keyb = xbmc.Keyboard('', u'Add meg a keresend\xF5 film c\xEDm\xE9t')
        keyb.doModal()
        if keyb.isConfirmed():
            search_text = keyb.getText()
        return search_text

    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None, banner=None):
        url = f'{sysaddon}?action={query}' if isAction else query
        if thumb == '':
            thumb = icon
        cm = []
        if queue:
            cm.append((queueMenu, f'RunPlugin({sysaddon}?action=queueItem)'))
        if not context is None:
            cm.append((context[0].encode('utf-8'), f'RunPlugin({sysaddon}?action={context[1]})'))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb, 'banner': banner})
        if Fanart is None:
            Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if not isFolder:
            item.setProperty('IsPlayable', 'true')
        if not meta is None:
            item.setInfo(type='Video', infoLabels=meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)