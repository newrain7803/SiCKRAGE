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
from abc import ABC

from tornado.web import authenticated

import sickrage
from sickrage.core.helpers import checkbox_to_value
from sickrage.core.webserver import ConfigHandler
from sickrage.core.webserver.handlers.base import BaseHandler


class ConfigAnimeHandler(BaseHandler, ABC):
    @authenticated
    async def get(self, *args, **kwargs):
        await self.run_in_executor(self.handle_get)

    def handle_get(self):
        return self.render('config/anime.mako',
                           submenu=ConfigHandler.menu,
                           title=_('Config - Anime'),
                           header=_('Anime'),
                           topmenu='config',
                           controller='config',
                           action='anime')


class ConfigSaveAnimeHandler(BaseHandler, ABC):
    @authenticated
    async def post(self, *args, **kwargs):
        await self.run_in_executor(self.handle_post)

    def handle_post(self):
        use_anidb = self.get_argument('use_anidb', '')
        anidb_username = self.get_argument('anidb_username', '')
        anidb_password = self.get_argument('anidb_password', '')
        anidb_use_mylist = self.get_argument('anidb_use_mylist', '')
        split_home = self.get_argument('split_home', '')

        results = []

        sickrage.app.config.use_anidb = checkbox_to_value(use_anidb)
        sickrage.app.config.anidb_username = anidb_username
        sickrage.app.config.anidb_password = anidb_password
        sickrage.app.config.anidb_use_mylist = checkbox_to_value(anidb_use_mylist)
        sickrage.app.config.anime_split_home = checkbox_to_value(split_home)

        sickrage.app.config.save()

        if len(results) > 0:
            [sickrage.app.log.error(x) for x in results]
            sickrage.app.alerts.error(_('Error(s) Saving Configuration'), '<br>\n'.join(results))
        else:
            sickrage.app.alerts.message(_('[ANIME] Configuration Encrypted and Saved to disk'))

        return self.redirect("/config/anime/")
