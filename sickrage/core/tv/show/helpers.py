# ##############################################################################
#  Author: echel0n <echel0n@sickrage.ca>
#  URL: https://sickrage.ca/
#  Git: https://git.sickrage.ca/SiCKRAGE/sickrage.git
#  -
#  This file is part of SiCKRAGE.
#  -
#  SiCKRAGE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  -
#  SiCKRAGE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  -
#  You should have received a copy of the GNU General Public License
#  along with SiCKRAGE.  If not, see <http://www.gnu.org/licenses/>.
# ##############################################################################

import sickrage


def find_show(indexer_id, indexer=1):
    if not indexer_id:
        return None

    return sickrage.app.shows.get((int(indexer_id), int(indexer)), None)


def find_show_by_name(term):
    for show in get_show_list():
        if term == show.name:
            return show


def find_show_by_scene_exception(term):
    for show in get_show_list():
        if term in [x.split('|')[0] for x in show.scene_exceptions]:
            return show


def find_show_by_location(location):
    for show in get_show_list():
        if show.location == location:
            return show


def get_show_list():
    return list(sickrage.app.shows.values())
