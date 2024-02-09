# -*- coding: utf-8 -*-

'''
    Moviedrive Add-on
    Copyright (C) 2020 heg, vargalex

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
import sys
from resources.lib.indexers import navigator

if sys.version_info[0] == 3:
    from urllib.parse import parse_qsl
else:
    from urlparse import parse_qsl

params = dict(parse_qsl(sys.argv[2].replace('?', '')))

action = params.get('action')
url = params.get('url')
title = params.get('title')
cover = params.get('cover')
release_year = params.get('release_year')
description = params.get('description')
season = params.get('season')
episode_number = params.get('episode_number')

if action is None:
    navigator.navigator().root()

elif action == 'items':
    navigator.navigator().getItems(url, title, cover, release_year, description)

elif action == 'search':
    navigator.navigator().getSearches()

elif action == 'get_movie_sources':
    navigator.navigator().getMovieSources(url, title, cover, release_year, description)

elif action == 'get_series_sources':
    navigator.navigator().getSeriesSources(url, title, cover, release_year, description, season, episode_number)
    
elif action == 'episodes':
    navigator.navigator().getEpisodes(url, title, cover, release_year, description, season, episode_number)    

elif action == 'playmovie':
    navigator.navigator().playMovie(url)

elif action == 'newsearch':
    navigator.navigator().doSearch()

elif action == 'deletesearchhistory':
    navigator.navigator().deleteSearchHistory() 