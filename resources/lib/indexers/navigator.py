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
import requests
import urllib.parse
from resources.lib.modules.utils import py2_decode, py2_encode
import html
#import resolveurl as urlresolver

sysaddon = sys.argv[0]
syshandle = int(sys.argv[1])
addonFanart = xbmcaddon.Addon().getAddonInfo('fanart')

version = xbmcaddon.Addon().getAddonInfo('version')
kodi_version = xbmc.getInfoLabel('System.BuildVersion')

base_log_info = f'Moviedrive | v{version} | Kodi: {kodi_version[:5]}'
xbmc.log(f'{base_log_info}', xbmc.LOGINFO)

base_url = 'https://moviedrive.hu/src/api/third.party/?req='

headers = {
    'authority': 'moviedrive.hu',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'KODI',
}

if sys.version_info[0] == 3:
    from xbmcvfs import translatePath
    from urllib.parse import urlparse, quote_plus, unquote_plus
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
        url_p = f"{base_url}search&p=1"
        enc_url = quote_plus(url_p)
        
        self.addDirectoryItem("Filmek & Sorozatok", f"items&url={quote_plus(enc_url)}", '', 'DefaultFolder.png')
        self.addDirectoryItem("Keresés", "search", '', 'DefaultFolder.png')
        self.endDirectory()

    def getItems(self, url, title, cover, release_year, description):
        decoded_url = unquote_plus(url)

        import requests
        import re

        response = requests.get(decoded_url, headers=headers)
        resp = response.json()
        
        title_count = 0

        for key in resp.keys():
            if key != "oldal_max":
                entry = resp[key]
                title = entry["title"]
                title_count += 1
                cover = entry["cover"]
                imdb_rating = entry["imdb_rating"]
                genre = entry["genere"]
                media_type = entry["type"]
        
                if media_type == 'Film':
                    media_type = f'{media_type:^10}'
                    card_link = f'{base_url}watch&type=Film&id={entry["id"]}'
                elif media_type == 'Sorozat':
                    card_link = f'{base_url}details&id={entry["id"]}'
        
                description = entry["description"]
                age_rating = entry["age"]
                release_year = entry["release"]
                release_year = re.sub(r'&ndash;', r' - ', release_year)
                background = entry["background"]
                country = entry["country"]
                length_str = entry["length"]
                length = int(length_str)
                duration = length * 60
                
                if media_type == 'Sorozat':
                    self.addDirectoryItem(
                        f'{media_type} | [B] {title} - ({release_year}) | [COLOR yellow]{imdb_rating}[/COLOR][/B]', 
                        f'get_series_sources&url={quote_plus(card_link)}&title={title}&cover={cover}&release_year={release_year}&description={description}', 
                        cover, background, 
                        isFolder=True, 
                        meta={'title': title, 
                              'plot': f'\n[B]Kategória:[/B] {genre}\n[B]Készült:[/B] {country}\n[B]Korhatár:[/B] {age_rating}\n\n{description}', 
                              'duration': f'{duration}'
                        }
                    )
                elif media_type:
                    self.addDirectoryItem(
                        f'{media_type} | [B]{title} - {release_year} | [COLOR yellow]{imdb_rating}[/COLOR][/B]', 
                        f'get_movie_sources&url={quote_plus(card_link)}&title={title}&cover={cover}&release_year={release_year}&description={description}', 
                        cover, background, 
                        isFolder=True, 
                        meta={'title': title, 
                              'plot': f'\n[B]Kategória:[/B] {genre}\n[B]Készült:[/B] {country}\n[B]Korhatár:[/B] {age_rating}\n\n{description}', 
                              'duration': f'{duration}'
                        }
                    )
        
        try:
            if title_count == 24:
                page_num_plus = int(re.findall(r'&p=(.*)', decoded_url)[0].strip()) + 1            
                
                base_page = f'{base_url}search&p='
                next_page_url = f'{base_page}{page_num_plus}'
                
                self.addDirectoryItem('[I]Következő oldal[/I]', f'items&url={quote_plus(next_page_url)}', '', 'DefaultFolder.png')
            else:    
                xbmc.log(f'{base_log_info}| getItems | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        except (AttributeError, IndexError):
            xbmc.log(f'{base_log_info}| getItems | next_page | csak egy oldal található', xbmc.LOGINFO)
        
        self.endDirectory('movies')

    def getMovieSources(self, url, title, cover, release_year, description):
        decoded_url = unquote_plus(url)
        
        import requests
        import re
        import json
        
        response_text = requests.get(decoded_url, headers=headers).text
        
        src_list = re.findall(r"src: '(.*?)'", response_text)
        size_list = [int(size) for size in re.findall(r"size: (\d+)", response_text)]
        
        sources_list = [{'src': src.replace('\\/', '/'), 'size': size} for src, size in zip(src_list, size_list)]
        
        for video in sources_list:
            video_link = video['src']
            video_size = video['size']
        
            try:
                self.addDirectoryItem(f'[B]{video_size}p - {title} - {release_year}[/B]', f'playmovie&url={quote_plus(video_link)}', cover, 'DefaultMovies.png', isFolder=False, meta={'title': f'{title} - {release_year}', 'plot':description})
            except UnboundLocalError:
                xbmc.log(f'{base_log_info}| getMovieSources | name: No video sources found', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("Moviedrive", "Törölt tartalom", time=5000)
        
        self.endDirectory('movies')

    def getSeriesSources(self, url, title, cover, release_year, description, season, episode_number):
        decoded_url = unquote_plus(url)
        
        import requests
        import re
        import json
        
        response = requests.get(decoded_url, headers=headers).json()

        eps_data = response.get('eps', {})
        
        for season, episodes in sorted(eps_data.items(), key=lambda x: int(x[0].split('.')[0])):
            episode_count = len(episodes)
            for i, (episode_key, episode_code) in enumerate(sorted(episodes.items(), key=lambda x: int(x[0].split('.')[0]))):
                episode_number = i + 1
                episode_all_video_link = f'https://moviedrive.hu/src/api/third.party/?req=watch&type=Sorozat&id={episode_code}'
                
                try:
                    self.addDirectoryItem(f'[B]{season} - {episode_number}. RÉSZ - {title}[/B]', f'episodes&url={quote_plus(episode_all_video_link)}&title={title}&cover={cover}&release_year={release_year}&description={description}&season={season}&episode_number={episode_number}', cover, 'DefaultMovies.png', isFolder=True, meta={'title': title, 'plot': description})
                except UnboundLocalError:
                    notification = xbmcgui.Dialog()
                    notification.notification("Moviedrive", "Törölt tartalom", time=5000)
                    xbmc.log(f'{base_log_info}| getSeriesSources | name: No video sources found', xbmc.LOGINFO)

        self.endDirectory('movies')

    def getEpisodes(self, url, title, cover, release_year, description, season, episode_number):
        decoded_url = unquote_plus(url)
        
        import requests
        import re
        import json
        
        response_text = requests.get(decoded_url, headers=headers).text
        
        src_list = re.findall(r"src: '(.*?)'", response_text)
        size_list = [int(size) for size in re.findall(r"size: (\d+)", response_text)]
        
        sources_list = [{'src': src.replace('\\/', '/'), 'size': size} for src, size in zip(src_list, size_list)]

        for video in sources_list:
            video_link = video['src']
            video_size = video['size']

            try:
                self.addDirectoryItem(f'[B]{video_size}p - {season} - {episode_number}. RÉSZ - {title}[/B]', f'playmovie&url={quote_plus(video_link)}', cover, 'DefaultMovies.png', isFolder=False, meta={'title': f'{title} - {season} - {episode_number}. RÉSZ ({video_size}p)', 'plot':description})
            except UnboundLocalError:
                xbmc.log(f'{base_log_info}| getMovieSources | name: No video sources found', xbmc.LOGINFO)
                notification = xbmcgui.Dialog()
                notification.notification("Moviedrive", "Törölt tartalom", time=5000)

        self.endDirectory('movies')

    def playMovie(self, url):
        
        direct_url = url
        if direct_url:
            xbmc.log('Moviedrive: playing URL: %s' % direct_url, xbmc.LOGINFO)
            play_item = xbmcgui.ListItem(path=direct_url)
            if 'm3u8' in direct_url:
                from inputstreamhelper import Helper
                is_helper = Helper('hls')
                if is_helper.check_inputstream():
                    if sys.version_info < (3, 0):  # if python version < 3 is safe to assume we are running on Kodi 18
                        play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')   # compatible with Kodi 18 API
                    else:
                        play_item.setProperty('inputstream', 'inputstream.adaptive')  # compatible with recent builds Kodi 19 API
                    try:
                        play_item.setProperty('inputstream.adaptive.stream_headers', direct_url.split("|")[1])
                        play_item.setProperty('inputstream.adaptive.manifest_headers', direct_url.split("|")[1])
                    except:
                        pass
                    play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            xbmcplugin.setResolvedUrl(syshandle, True, listitem=play_item)

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
                enc_link = f'{base_url}search&q={item}&p=1'
                self.addDirectoryItem(item, f'items&url={quote_plus(enc_link)}', '', 'DefaultFolder.png')

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
            self.getItems(f"{base_url}search&q={search_text}", None, None, None, None)

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
