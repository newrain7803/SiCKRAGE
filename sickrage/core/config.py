# Author: echel0n <tv@gmail.com>
# URL: https://tv
# Git: https://github.com/V/git
#
# This file is part of 
#
# is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with   If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import base64
import datetime
import gettext
import os
import os.path
import pickle
import re
import sys
import uuid
from itertools import izip, cycle

import rarfile
from apscheduler.triggers.interval import IntervalTrigger
from configobj import ConfigObj

import sickrage
from sickrage.core.common import SD, WANTED, SKIPPED, Quality
from sickrage.core.helpers import backupVersionedFile, makeDir, generateCookieSecret, auto_type, get_lan_ip, \
    extract_zipfile, \
    try_int, checkbox_to_value


class Config(object):
    def __init__(self):
        self.loaded = False

        self.config_obj = None
        self.config_version = 0

        self.debug = False
        self.developer = False
        self.encryption_version = 0
        self.encryption_secret = generateCookieSecret()

        self.last_db_compact = 0

        self.naming_ep_type = ("%(seasonnumber)dx%(episodenumber)02d",
                               "s%(seasonnumber)02de%(episodenumber)02d",
                               "S%(seasonnumber)02dE%(episodenumber)02d",
                               "%(seasonnumber)02dx%(episodenumber)02d")
        self.sports_ep_type = ("%(seasonnumber)dx%(episodenumber)02d",
                               "s%(seasonnumber)02de%(episodenumber)02d",
                               "S%(seasonnumber)02dE%(episodenumber)02d",
                               "%(seasonnumber)02dx%(episodenumber)02d")
        self.naming_ep_type_text = ("1x02", "s01e02", "S01E02", "01x02")
        self.naming_multi_ep_type = {0: ["-%(episodenumber)02d"] * len(self.naming_ep_type),
                                     1: [" - " + x for x in self.naming_ep_type],
                                     2: [x + "%(episodenumber)02d" for x in ("x", "e", "E", "x")]}
        self.naming_multi_ep_type_text = ("extend", "duplicate", "repeat")
        self.naming_sep_type = (" - ", " ")
        self.naming_sep_type_text = (" - ", "space")

        self.log_size = 1048576
        self.log_nr = 5

        self.version_notify = True
        self.auto_update = True
        self.notify_on_update = True
        self.notify_on_login = False
        self.pip_path = ""
        self.git_reset = True
        self.git_username = ""
        self.git_password = ""
        self.git_path = ""
        self.git_autoissues = False
        self.git_newver = False
        self.changes_url = 'https://git.sickrage.ca/SiCKRAGE/sickrage/raw/master/changelog.md'
        self.socket_timeout = 30
        self.web_host = get_lan_ip()
        self.web_port = 8081
        self.web_log = False
        self.web_root = ""
        self.web_username = ""
        self.web_password = ""
        self.web_ipv6 = False
        self.web_cookie_secret = generateCookieSecret()
        self.web_use_gzip = True
        self.handle_reverse_proxy = False
        self.proxy_setting = ""
        self.proxy_indexers = True
        self.ssl_verify = True
        self.enable_https = False
        self.https_cert = os.path.abspath(os.path.join(sickrage.PROG_DIR, 'server.crt'))
        self.https_key = os.path.abspath(os.path.join(sickrage.PROG_DIR, 'server.key'))
        self.api_key = ""
        self.api_root = None
        self.indexer_default_language = 'en'
        self.ep_default_deleted_status = 6
        self.launch_browser = False
        self.showupdate_stale = True
        self.root_dirs = ""
        self.cpu_preset = "NORMAL"
        self.anon_redirect = 'http://nullrefer.com/?'
        self.download_url = ""
        self.trash_remove_show = False
        self.trash_rotate_logs = False
        self.sort_article = False
        self.display_all_seasons = True
        self.default_page = "home"
        self.use_listview = False

        self.quality_default = SD
        self.status_default = SKIPPED
        self.status_default_after = WANTED
        self.flatten_folders_default = False
        self.subtitles_default = False
        self.indexer_default = 0
        self.indexer_timeout = 120
        self.scene_default = False
        self.anime_default = False
        self.archive_default = False
        self.naming_multi_ep = False
        self.naming_anime_multi_ep = False
        self.naming_pattern = None
        self.naming_abd_pattern = None
        self.naming_custom_abd = False
        self.naming_sports_pattern = None
        self.naming_custom_sports = False
        self.naming_anime_pattern = None
        self.naming_custom_anime = False
        self.naming_force_folders = False
        self.naming_strip_year = False
        self.naming_anime = None
        self.use_nzbs = False
        self.use_torrents = False
        self.nzb_method = None
        self.nzb_dir = None
        self.usenet_retention = 500
        self.torrent_method = None
        self.torrent_dir = None
        self.download_propers = False
        self.enable_rss_cache = True
        self.enable_rss_cache_valid_shows = False
        self.torrent_file_to_magnet = False
        self.proper_searcher_interval = None
        self.allow_high_priority = False
        self.sab_forced = False
        self.randomize_providers = False
        self.min_autopostprocessor_freq = 1
        self.min_daily_searcher_freq = 10
        self.min_backlog_searcher_freq = 10
        self.min_version_updater_freq = 1
        self.min_subtitle_searcher_freq = 1
        self.backlog_days = 7
        self.add_shows_wo_dir = False
        self.create_missing_show_dirs = False
        self.rename_episodes = False
        self.airdate_episodes = False
        self.file_timestamp_timezone = None
        self.process_automatically = False
        self.no_delete = False
        self.keep_processed_dir = False
        self.process_method = None
        self.delrarcontents = False
        self.move_associated_files = False
        self.postpone_if_sync_files = True
        self.nfo_rename = True
        self.tv_download_dir = None
        self.unpack = False
        self.skip_removed_files = False
        self.nzbs = False
        self.nzbs_uid = None
        self.nzbs_hash = None
        self.omgwtfnzbs = False
        self.newzbin = False
        self.newzbin_username = None
        self.newzbin_password = None
        self.sab_username = None
        self.sab_password = None
        self.sab_apikey = None
        self.sab_category = None
        self.sab_category_backlog = None
        self.sab_category_anime = None
        self.sab_category_anime_backlog = None
        self.sab_host = None
        self.nzbget_username = None
        self.nzbget_password = None
        self.nzbget_category = None
        self.nzbget_category_backlog = None
        self.nzbget_category_anime = None
        self.nzbget_category_anime_backlog = None
        self.nzbget_host = None
        self.nzbget_use_https = False
        self.nzbget_priority = 100
        self.torrent_username = None
        self.torrent_password = None
        self.torrent_host = None
        self.torrent_path = None
        self.torrent_seed_time = None
        self.torrent_paused = False
        self.torrent_high_bandwidth = False
        self.torrent_label = None
        self.torrent_label_anime = None
        self.torrent_verify_cert = False
        self.torrent_rpcurl = None
        self.torrent_auth_type = None
        self.use_kodi = False
        self.kodi_always_on = True
        self.kodi_notify_onsnatch = False
        self.kodi_notify_ondownload = False
        self.kodi_notify_onsubtitledownload = False
        self.kodi_update_library = False
        self.kodi_update_full = False
        self.kodi_update_onlyfirst = False
        self.kodi_host = None
        self.kodi_username = None
        self.kodi_password = None
        self.use_plex = False
        self.plex_notify_onsnatch = False
        self.plex_notify_ondownload = False
        self.plex_notify_onsubtitledownload = False
        self.plex_update_library = False
        self.plex_server_host = None
        self.plex_server_token = None
        self.plex_host = None
        self.plex_username = None
        self.plex_password = None
        self.use_plex_client = False
        self.plex_client_username = None
        self.plex_client_password = None
        self.use_emby = False
        self.emby_host = None
        self.emby_apikey = None
        self.use_growl = False
        self.growl_notify_onsnatch = False
        self.growl_notify_ondownload = False
        self.growl_notify_onsubtitledownload = False
        self.growl_host = None
        self.growl_password = None
        self.use_freemobile = False
        self.freemobile_notify_onsnatch = False
        self.freemobile_notify_ondownload = False
        self.freemobile_notify_onsubtitledownload = False
        self.freemobile_id = ""
        self.freemobile_apikey = ""
        self.use_telegram = False
        self.telegram_notify_onsnatch = False
        self.telegram_notify_ondownload = False
        self.telegram_notify_onsubtitledownload = False
        self.telegram_id = ""
        self.telegram_apikey = ""
        self.use_prowl = False
        self.prowl_notify_onsnatch = False
        self.prowl_notify_ondownload = False
        self.prowl_notify_onsubtitledownload = False
        self.prowl_api = None
        self.prowl_priority = 0
        self.use_twitter = False
        self.twitter_notify_onsnatch = False
        self.twitter_notify_ondownload = False
        self.twitter_notify_onsubtitledownload = False
        self.twitter_username = None
        self.twitter_password = None
        self.twitter_prefix = None
        self.twitter_dmto = None
        self.twitter_usedm = False
        self.use_boxcar2 = False
        self.boxcar2_notify_onsnatch = False
        self.boxcar2_notify_ondownload = False
        self.boxcar2_notify_onsubtitledownload = False
        self.boxcar2_accesstoken = None
        self.use_pushover = False
        self.pushover_notify_onsnatch = False
        self.pushover_notify_ondownload = False
        self.pushover_notify_onsubtitledownload = False
        self.pushover_userkey = None
        self.pushover_apikey = None
        self.pushover_device = None
        self.pushover_sound = None
        self.use_libnotify = False
        self.libnotify_notify_onsnatch = False
        self.libnotify_notify_ondownload = False
        self.libnotify_notify_onsubtitledownload = False
        self.use_nmj = False
        self.nmj_host = None
        self.nmj_database = None
        self.nmj_mount = None
        self.use_anidb = False
        self.anidb_username = None
        self.anidb_password = None
        self.anidb_use_mylist = False
        self.anime_split_home = False
        self.use_synoindex = False
        self.use_nmjv2 = False
        self.nmjv2_host = None
        self.nmjv2_database = None
        self.nmjv2_dbloc = None
        self.use_synologynotifier = False
        self.synologynotifier_notify_onsnatch = False
        self.synologynotifier_notify_ondownload = False
        self.synologynotifier_notify_onsubtitledownload = False
        self.use_slack = False
        self.slack_notify_onsnatch = None
        self.slack_notify_ondownload = None
        self.slack_notify_onsubtitledownload = None
        self.slack_webhook = ""
        self.use_discord = False
        self.discord_notify_onsnatch = False
        self.discord_notify_ondownload = False
        self.discord_notify_onsubtitledownload = False
        self.discord_webhook = ""
        self.discord_name = None
        self.discord_avatar_url = None
        self.discord_tts = False
        self.use_trakt = False
        self.trakt_username = ""
        self.trakt_oauth_token = ""
        self.trakt_remove_watchlist = False
        self.trakt_remove_serieslist = False
        self.trakt_remove_show_from_sickrage = False
        self.trakt_sync_watchlist = False
        self.trakt_method_add = False
        self.trakt_start_paused = False
        self.trakt_use_recommended = False
        self.trakt_sync = False
        self.trakt_sync_remove = False
        self.trakt_default_indexer = 1
        self.trakt_timeout = 30
        self.trakt_blacklist_name = ""
        self.use_pytivo = False
        self.pytivo_notify_onsnatch = False
        self.pytivo_notify_ondownload = False
        self.pytivo_notify_onsubtitledownload = False
        self.pytivo_update_library = False
        self.pytivo_host = None
        self.pytivo_share_name = None
        self.pytivo_tivo_name = None
        self.use_nma = False
        self.nma_notify_onsnatch = False
        self.nma_notify_ondownload = False
        self.nma_notify_onsubtitledownload = False
        self.nma_api = None
        self.nma_priority = 0
        self.use_pushalot = False
        self.pushalot_notify_onsnatch = False
        self.pushalot_notify_ondownload = False
        self.pushalot_notify_onsubtitledownload = False
        self.pushalot_authorizationtoken = None
        self.use_pushbullet = False
        self.pushbullet_notify_onsnatch = False
        self.pushbullet_notify_ondownload = False
        self.pushbullet_notify_onsubtitledownload = False
        self.pushbullet_api = None
        self.pushbullet_device = None
        self.use_email = False
        self.email_notify_onsnatch = False
        self.email_notify_ondownload = False
        self.email_notify_onsubtitledownload = False
        self.email_host = None
        self.email_port = 25
        self.email_tls = False
        self.email_user = None
        self.email_password = None
        self.email_from = None
        self.email_list = None
        self.gui_lang = ""
        self.gui_static_dir = os.path.join(sickrage.PROG_DIR, 'core', 'webserver', 'static')
        self.gui_views_dir = os.path.join(sickrage.PROG_DIR, 'core', 'webserver', 'views')
        self.home_layout = None
        self.history_layout = None
        self.history_limit = 0
        self.display_show_specials = False
        self.coming_eps_layout = None
        self.coming_eps_display_paused = False
        self.coming_eps_sort = None
        self.coming_eps_missed_range = None
        self.fuzzy_dating = False
        self.trim_zero = False
        self.date_preset = None
        self.time_preset = None
        self.time_preset_w_seconds = None
        self.timezone_display = None
        self.theme_name = None
        self.poster_sortby = None
        self.poster_sortdir = None
        self.filter_row = True
        self.use_subtitles = False
        self.subtitles_languages = None
        self.subtitles_dir = None
        self.subtitles_services_list = None
        self.subtitles_services_enabled = None
        self.subtitles_history = False
        self.embedded_subtitles_all = False
        self.subtitles_hearing_impaired = False
        self.subtitles_multi = False
        self.subtitles_extra_scripts = None
        self.addic7ed_user = None
        self.addic7ed_pass = None
        self.opensubtitles_user = None
        self.opensubtitles_pass = None
        self.legendastv_user = None
        self.legendastv_pass = None
        self.itasa_user = None
        self.itasa_pass = None
        self.use_failed_downloads = False
        self.delete_failed = False
        self.extra_scripts = None
        self.require_words = None
        self.ignore_words = None
        self.ignored_subs_list = None
        self.sync_files = None
        self.calendar_unprotected = False
        self.calendar_icons = False
        self.no_restart = False
        self.thetvdb_apitoken = None
        self.trakt_api_key = '5c65f55e11d48c35385d9e8670615763a605fad28374c8ae553a7b7a50651ddd'
        self.trakt_api_secret = 'b53e32045ac122a445ef163e6d859403301ffe9b17fb8321d428531b69022a82'
        self.trakt_app_id = '4562'
        self.trakt_oauth_url = 'https://trakt.tv/'
        self.trakt_api_url = 'https://api.trakt.tv/'
        self.fanart_api_key = '9b3afaf26f6241bdb57d6cc6bd798da7'
        self.shows_recent = []

        self.default_autopostprocessor_freq = 10
        self.autopostprocessor_freq = None

        self.default_namecache_freq = 10
        self.namecache_freq = None

        self.default_daily_searcher_freq = 40
        self.daily_searcher_freq = None

        self.default_backlog_searcher_freq = 21
        self.backlog_searcher_freq = None

        self.default_version_update_freq = 1
        self.version_updater_freq = None

        self.default_subtitle_searcher_freq = 1
        self.subtitle_searcher_freq = None

        self.default_showupdate_hour = 3
        self.showupdate_hour = None

        self.quality_sizes = None

        self.custom_providers = None

        self.git_remote = "origin"
        self.git_remote_url = "https://git.sickrage.ca/SiCKRAGE/sickrage"

        self.random_user_agent = False

        self.fanart_background = True
        self.fanart_background_opacity = 0.4

        self.unrar_tool = rarfile.UNRAR_TOOL
        self.unrar_alt_tool = rarfile.ALT_TOOL

    @property
    def defaults(self):
        return {
            'Providers': {
                'custom_providers': '',
                'providers_order': []
            },
            'NZBs': {
                'nzbs': False,
                'nzbs_uid': '',
                'nzbs_hash': ''
            },
            'Growl': {
                'growl_host': '',
                'use_growl': False,
                'growl_notify_ondownload': False,
                'growl_notify_onsubtitledownload': False,
                'growl_notify_onsnatch': False,
                'growl_password': ''
            },
            'Slack': {
                'slack_notify_onsnatch': False,
                'slack_notify_ondownload': False,
                'slack_notify_onsubtitledownload': False,
                'use_slack': False,
                'slack_webhook': ''
            },
            'TELEGRAM': {
                'telegram_notify_ondownload': False,
                'telegram_apikey': '',
                'telegram_id': '',
                'use_telegram': False,
                'telegram_notify_onsnatch': False,
                'telegram_notify_onsubtitledownload': False
            },
            'GUI': {
                'coming_eps_display_paused': False,
                'display_show_specials': True,
                'gui_lang': '',
                'history_limit': '100',
                'poster_sortdir': 1,
                'coming_eps_missed_range': 7,
                'date_preset': '%x',
                'fuzzy_dating': False,
                'fanart_background': True,
                'home_layout': 'poster',
                'coming_eps_layout': 'banner',
                'coming_eps_sort': 'date',
                'poster_sortby': 'name',
                'time_preset': '%I:%M:%S%p',
                'trim_zero': False,
                'fanart_background_opacity': 0.4,
                'history_layout': 'detailed',
                'filter_row': True,
                'timezone_display': 'local',
                'theme_name': 'dark'
            },
            'NMA': {
                'nma_notify_onsubtitledownload': False,
                'use_nma': False,
                'nma_notify_onsnatch': False,
                'nma_priority': '0',
                'nma_api': '',
                'nma_notify_ondownload': False
            },
            'Prowl': {
                'prowl_notify_ondownload': False,
                'prowl_api': '',
                'prowl_priority': '0',
                'prowl_notify_onsubtitledownload': False,
                'prowl_notify_onsnatch': False,
                'use_prowl': False
            },
            'Synology': {
                'use_synoindex': False
            },
            'Newzbin': {
                'newzbin': False,
                'newzbin_password': '',
                'newzbin_username': ''
            },
            'Trakt': {
                'trakt_remove_serieslist': False,
                'trakt_remove_show_from_sickrage': False,
                'trakt_use_recommended': False,
                'trakt_sync': False,
                'use_trakt': False,
                'trakt_blacklist_name': '',
                'trakt_start_paused': False,
                'trakt_sync_remove': False,
                'trakt_username': '',
                'trakt_oauth_token': '',
                'trakt_method_add': 0,
                'trakt_remove_watchlist': False,
                'trakt_sync_watchlist': False,
                'trakt_timeout': 30,
                'trakt_default_indexer': 1
            },
            'NMJv2': {
                'nmjv2_dbloc': '',
                'nmjv2_database': '',
                'nmjv2_host': '',
                'use_nmjv2': False
            },
            'SABnzbd': {
                'sab_forced': False,
                'sab_category': 'tv',
                'sab_apikey': '',
                'sab_category_anime': 'anime',
                'sab_category_backlog': 'tv',
                'sab_host': '',
                'sab_password': '',
                'sab_username': '',
                'sab_category_anime_backlog': 'anime'
            },
            'Plex': {
                'plex_update_library': False,
                'plex_server_host': '',
                'plex_host': '',
                'plex_password': '',
                'plex_notify_onsubtitledownload': False,
                'plex_notify_onsnatch': False,
                'plex_username': '',
                'plex_notify_ondownload': False,
                'plex_server_token': '',
                'use_plex': False,
                'use_plex_client': False,
                'plex_client_username': '',
                'plex_client_password': ''
            },
            'TORRENT': {
                'torrent_verify_cert': False,
                'torrent_paused': False,
                'torrent_host': '',
                'torrent_label_anime': '',
                'torrent_path': '',
                'torrent_auth_type': '',
                'torrent_rpcurl': 'transmission',
                'torrent_username': '',
                'torrent_label': '',
                'torrent_password': '',
                'torrent_high_bandwidth': False,
                'torrent_seed_time': 0
            },
            'Pushalot': {
                'pushalot_notify_onsubtitledownload': False,
                'pushalot_authorizationtoken': '',
                'pushalot_notify_onsnatch': False,
                'pushalot_notify_ondownload': False,
                'use_pushalot': False
            },
            'Pushover': {
                'pushover_notify_ondownload': False,
                'pushover_sound': 'pushover',
                'use_pushover': False,
                'pushover_notify_onsubtitledownload': False,
                'pushover_device': '',
                'pushover_apikey': '',
                'pushover_userkey': '',
                'pushover_notify_onsnatch': False
            },
            'Email': {
                'email_notify_onsnatch': False,
                'email_list': '',
                'email_password': '',
                'email_tls': False,
                'use_email': False,
                'email_notify_ondownload': False,
                'email_port': 25,
                'email_notify_onsubtitledownload': False,
                'email_user': '',
                'email_from': '',
                'email_host': ''
            },
            'KODI': {
                'kodi_update_onlyfirst': False,
                'kodi_notify_onsnatch': False,
                'kodi_notify_ondownload': False,
                'kodi_host': '',
                'kodi_username': '',
                'kodi_always_on': True,
                'kodi_update_library': False,
                'use_kodi': False,
                'kodi_password': '',
                'kodi_update_full': False,
                'kodi_notify_onsubtitledownload': False
            },
            'Quality': {
                'sizes': Quality.qualitySizes
            },
            'FreeMobile': {
                'freemobile_notify_onsnatch': False,
                'freemobile_notify_onsubtitledownload': False,
                'freemobile_notify_ondownload': False,
                'freemobile_apikey': '',
                'freemobile_id': '',
                'use_freemobile': False
            },
            'Discord': {
                'discord_notify_onsubtitledownload': False,
                'discord_notify_ondownload': False,
                'discord_notify_onsnatch': False,
                'discord_webhook': '',
                'use_discord': False,
                'discord_name': '',
                'discord_avatar_url': '',
                'discord_tts': False
            },
            'SynologyNotifier': {
                'synologynotifier_notify_onsnatch': False,
                'synologynotifier_notify_ondownload': False,
                'use_synologynotifier': False,
                'synologynotifier_notify_onsubtitledownload': False
            },
            'ANIDB': {
                'anidb_use_mylist': False,
                'use_anidb': False,
                'anidb_password': '',
                'anidb_username': ''
            },
            'Blackhole': {
                'nzb_dir': '',
                'torrent_dir': ''
            },
            'General': {
                'log_size': 1048576,
                'calendar_unprotected': False,
                'https_key': os.path.abspath(os.path.join(sickrage.PROG_DIR, 'server.key')),
                'allow_high_priority': True,
                'developer': True,
                'anon_redirect': 'http://nullrefer.com/?',
                'indexer_timeout': 120,
                'web_use_gzip': True,
                'dailysearch_frequency': 40,
                'ignore_words': 'german,french,core2hd,dutch,swedish,reenc,MrLss',
                'api_key': '',
                'check_propers_interval': 'daily',
                'nzb_method': 'blackhole',
                'web_cookie_secret': generateCookieSecret(),
                'ssl_verify': True,
                'encryption_secret': generateCookieSecret(),
                'version_notify': True,
                'web_root': '',
                'add_shows_wo_dir': False,
                'debug': True,
                'indexer_default': 0,
                'use_torrents': True,
                'display_all_seasons': True,
                'usenet_retention': 500,
                'download_propers': True,
                'pip_path': 'pip',
                'del_rar_contents': False,
                'process_method': 'copy',
                'file_timestamp_timezone': 'network',
                'auto_update': True,
                'tv_download_dir': '',
                'naming_custom_abd': False,
                'archive_default': False,
                'naming_sports_pattern': '%SN - %A-D - %EN',
                'create_missing_show_dirs': False,
                'trash_rotate_logs': False,
                'airdate_episodes': False,
                'notify_on_update': True,
                'https_cert': os.path.abspath(os.path.join(sickrage.PROG_DIR, 'server.crt')),
                'git_autoissues': False,
                'backlog_days': 7,
                'root_dirs': '',
                'naming_pattern': 'Season %0S/%SN - S%0SE%0E - %EN',
                'sort_article': False,
                'handle_reverse_proxy': False,
                'web_username': '',
                'postpone_if_sync_files': True,
                'cpu_preset': 'NORMAL',
                'nfo_rename': True,
                'naming_anime_multi_ep': 1,
                'use_nzbs': False,
                'web_ipv6': False,
                'anime_default': False,
                'default_page': 'home',
                'update_frequency': 1,
                'download_url': '',
                'encryption_version': 0,
                'showupdate_hour': 3,
                'enable_rss_cache': True,
                'enable_rss_cache_valid_shows': False,
                'torrent_file_to_magnet': False,
                'status_default': 5,
                'naming_anime': 3,
                'naming_custom_sports': False,
                'naming_anime_pattern': 'Season %0S/%SN - S%0SE%0E - %EN',
                'naming_custom_anime': False,
                'randomize_providers': False,
                'web_host': '192.168.1.203',
                'config_version': 11,
                'process_automatically': False,
                'git_path': 'git',
                'sync_files': '!sync,lftp-pget-status,part,bts,!qb',
                'web_port': 8081,
                'launch_browser': False,
                'unpack': False,
                'move_associated_files': False,
                'naming_multi_ep': 1,
                'random_user_agent': False,
                'torrent_method': 'blackhole',
                'use_listview': False,
                'trash_remove_show': False,
                'enable_https': False,
                'no_delete': False,
                'naming_abd_pattern': '%SN - %A.D - %EN',
                'socket_timeout': 30,
                'proxy_setting': '',
                'backlog_frequency': 21,
                'notify_on_login': False,
                'rename_episodes': True,
                'quality_default': 3,
                'git_username': '',
                'extra_scripts': '',
                'flatten_folders_default': False,
                'indexerDefaultLang': 'en',
                'autopostprocessor_frequency': 10,
                'showupdate_stale': True,
                'git_password': '',
                'ep_default_deleted_status': 6,
                'no_restart': False,
                'require_words': '',
                'naming_strip_year': False,
                'proxy_indexers': True,
                'web_log': False,
                'log_nr': 5,
                'git_newver': False,
                'git_reset': True,
                'web_password': '',
                'scene_default': False,
                'skip_removed_files': False,
                'status_default_after': 3,
                'last_db_compact': 0,
                'ignored_subs_list': 'dk,fin,heb,kor,nor,nordic,pl,swe',
                'calendar_icons': False,
                'keep_processed_dir': True
            },
            'NZBget': {
                'nzbget_host': '',
                'nzbget_category_anime': 'anime',
                'nzbget_use_https': False,
                'nzbget_password': 'tegbzn6789',
                'nzbget_category': 'tv',
                'nzbget_priority': 100,
                'nzbget_category_anime_backlog': 'anime',
                'nzbget_username': 'nzbget',
                'nzbget_category_backlog': 'tv'
            },
            'Emby': {
                'use_emby': False,
                'emby_apikey': '',
                'emby_host': ''
            },
            'pyTivo': {
                'pytivo_share_name': '',
                'pytivo_notify_ondownload': False,
                'pytivo_tivo_name': '',
                'pytivo_notify_onsnatch': False,
                'pytivo_host': '',
                'pytivo_notify_onsubtitledownload': False,
                'pyTivo_update_library': False,
                'use_pytivo': False
            },
            'theTVDB': {
                'thetvdb_apitoken': ''
            },
            'Pushbullet': {
                'pushbullet_device': '',
                'use_pushbullet': False,
                'pushbullet_notify_ondownload': False,
                'pushbullet_notify_onsubtitledownload': False,
                'pushbullet_notify_onsnatch': False,
                'pushbullet_api': ''
            },
            'Libnotify': {
                'libnotify_notify_onsubtitledownload': False,
                'libnotify_notify_onsnatch': False,
                'libnotify_notify_ondownload': False,
                'use_libnotify': False
            },
            'Boxcar2': {
                'use_boxcar2': False,
                'boxcar2_notify_onsnatch': False,
                'boxcar2_notify_ondownload': False,
                'boxcar2_accesstoken': '',
                'boxcar2_notify_onsubtitledownload': False
            },
            'FailedDownloads': {
                'use_failed_downloads': False,
                'delete_failed': False
            },
            'NMJ': {
                'nmj_host': '',
                'nmj_mount': '',
                'use_nmj': False,
                'nmj_database': ''
            },
            'Twitter': {
                'twitter_username': '',
                'use_twitter': False,
                'twitter_password': '',
                'twitter_notify_ondownload': False,
                'twitter_notify_onsubtitledownload': False,
                'twitter_notify_onsnatch': False,
                'twitter_prefix': 'SiCKRAGE',
                'twitter_dmto': '',
                'twitter_usedm': False
            },
            'Twilio': {
                'use_twilio': False,
                'twilio_notify_onsnatch': False,
                'twilio_notify_ondownload': False,
                'twilio_notify_onsubtitledownload': False,
                'twilio_phone_sid': '',
                'twilio_account_sid': '',
                'twilio_auth_token': '',
                'twilio_to_number': '',
            },
            'Subtitles': {
                'itasa_password': '',
                'opensubtitles_username': '',
                'subtitles_services_list': '',
                'subtitles_history': False,
                'legendastv_password': '',
                'subtitles_hearing_impaired': False,
                'addic7ed_password': '',
                'subtitles_languages': '',
                'embedded_subtitles_all': False,
                'subtitles_finder_frequency': 1,
                'subtitles_default': False,
                'subtitles_multi': True,
                'subtitles_services_enabled': '',
                'itasa_username': '',
                'subtitles_dir': '',
                'addic7ed_username': '',
                'opensubtitles_password': '',
                'subtitles_extra_scripts': '',
                'use_subtitles': False,
                'legendastv_username': ''
            },
            'ANIME': {
                'anime_split_home': False
            }
        }

    def change_gui_lang(self, lang):
        if lang:
            # Selected language
            gt = gettext.translation('messages', sickrage.LOCALE_DIR, languages=[lang], codeset='UTF-8')
            gt.install(unicode=True, names=["ngettext"])
        else:
            # System default language
            gettext.install('messages', sickrage.LOCALE_DIR, unicode=1, codeset='UTF-8', names=["ngettext"])

        self.gui_lang = lang

    def change_unrar_tool(self, unrar_tool, unrar_alt_tool):
        # Check for failed unrar attempt, and remove it
        # Must be done before unrar is ever called or the self-extractor opens and locks startup
        bad_unrar = os.path.join(sickrage.app.data_dir, 'unrar.exe')
        if os.path.exists(bad_unrar) and os.path.getsize(bad_unrar) == 447440:
            try:
                os.remove(bad_unrar)
            except OSError as e:
                sickrage.app.log.warning(
                    "Unable to delete bad unrar.exe file {}: {}. You should delete it manually".format(bad_unrar,
                                                                                                       e.strerror))

        try:
            rarfile.custom_check(unrar_tool)
        except (rarfile.RarCannotExec, rarfile.RarExecError, OSError, IOError):
            # Let's just return right now if the defaults work
            try:

                test = rarfile._check_unrar_tool()
                if test:
                    # These must always be set to something before returning
                    self.unrar_tool = rarfile.UNRAR_TOOL
                    self.alt_unrar_tool = rarfile.ALT_TOOL
                    return True
            except (rarfile.RarCannotExec, rarfile.RarExecError, OSError, IOError):
                pass

            if sys.platform == 'win32':
                # Look for WinRAR installations
                found = False
                winrar_path = 'WinRAR\\UnRAR.exe'
                # Make a set of unique paths to check from existing environment variables
                check_locations = {
                    os.path.join(location, winrar_path) for location in (
                    os.environ.get("ProgramW6432"), os.environ.get("ProgramFiles(x86)"),
                    os.environ.get("ProgramFiles"), re.sub(r'\s?\(x86\)', '', os.environ["ProgramFiles"])
                ) if location
                }
                check_locations.add(os.path.join(sickrage.PROG_DIR, 'unrar\\unrar.exe'))

                for check in check_locations:
                    if os.path.isfile(check):
                        # Can use it?
                        try:
                            rarfile.custom_check(check)
                            unrar_tool = check
                            found = True
                            break
                        except (rarfile.RarCannotExec, rarfile.RarExecError, OSError, IOError):
                            found = False

                # Download
                if not found:
                    sickrage.app.log.info('Trying to download unrar.exe and set the path')
                    unrar_dir = os.path.join(sickrage.PROG_DIR, 'unrar')
                    unrar_zip = os.path.join(unrar_dir, 'unrar_win.zip')

                    if (sickrage.app.wsession.download(
                            "https://sickrage.ca/downloads/unrar_win.zip", filename=unrar_zip,
                    ) and extract_zipfile(archive=unrar_zip, targetDir=unrar_dir)):
                        try:
                            os.remove(unrar_zip)
                        except OSError as e:
                            sickrage.app.log.info(
                                "Unable to delete downloaded file {}: {}. You may delete it manually".format(unrar_zip,
                                                                                                             e.strerror))

                        check = os.path.join(unrar_dir, "unrar.exe")
                        try:
                            rarfile.custom_check(check)
                            unrar_tool = check
                            sickrage.app.log.info('Successfully downloaded unrar.exe and set as unrar tool')
                        except (rarfile.RarCannotExec, rarfile.RarExecError, OSError, IOError):
                            sickrage.app.log.info(
                                'Sorry, unrar was not set up correctly. Try installing WinRAR and make sure it is on the system PATH')
                    else:
                        sickrage.app.log.info('Unable to download unrar.exe')

        # These must always be set to something before returning
        self.unrar_tool = rarfile.UNRAR_TOOL = rarfile.ORIG_UNRAR_TOOL = unrar_tool
        self.unrar_alt_tool = rarfile.ALT_TOOL = unrar_alt_tool

        try:
            rarfile._check_unrar_tool()
            return True
        except (rarfile.RarCannotExec, rarfile.RarExecError, OSError, IOError):
            if self.unpack:
                sickrage.app.log.info('Disabling UNPACK setting because no unrar is installed.')
                self.unpack = False

    def change_https_cert(self, https_cert):
        """
        Replace HTTPS Certificate file path

        :param https_cert: path to the new certificate file
        :return: True on success, False on failure
        """

        if https_cert == '':
            self.https_cert = ''
            return True

        if os.path.normpath(self.https_cert) != os.path.normpath(https_cert):
            if makeDir(os.path.dirname(os.path.abspath(https_cert))):
                self.https_cert = os.path.normpath(https_cert)
                sickrage.app.log.info("Changed https cert path to " + https_cert)
            else:
                return False

        return True

    def change_https_key(self, https_key):
        """
        Replace HTTPS Key file path

        :param https_key: path to the new key file
        :return: True on success, False on failure
        """
        if https_key == '':
            self.https_key = ''
            return True

        if os.path.normpath(self.https_key) != os.path.normpath(https_key):
            if makeDir(os.path.dirname(os.path.abspath(https_key))):
                self.https_key = os.path.normpath(https_key)
                sickrage.app.log.info("Changed https key path to " + https_key)
            else:
                return False

        return True

    def change_nzb_dir(self, nzb_dir):
        """
        Change NZB Folder

        :param nzb_dir: New NZB Folder location
        :return: True on success, False on failure
        """
        if nzb_dir == '':
            self.nzb_dir = ''
            return True

        if os.path.normpath(self.nzb_dir) != os.path.normpath(nzb_dir):
            if makeDir(nzb_dir):
                self.nzb_dir = os.path.normpath(nzb_dir)
                sickrage.app.log.info("Changed NZB folder to " + nzb_dir)
            else:
                return False

        return True

    def change_torrent_dir(self, torrent_dir):
        """
        Change torrent directory

        :param torrent_dir: New torrent directory
        :return: True on success, False on failure
        """
        if torrent_dir == '':
            self.torrent_dir = ''
            return True

        if os.path.normpath(self.torrent_dir) != os.path.normpath(torrent_dir):
            if makeDir(torrent_dir):
                self.torrent_dir = os.path.normpath(torrent_dir)
                sickrage.app.log.info("Changed torrent folder to " + torrent_dir)
            else:
                return False

        return True

    def change_tv_download_dir(self, tv_download_dir):
        """
        Change TV_DOWNLOAD directory (used by postprocessor)

        :param tv_download_dir: New tv download directory
        :return: True on success, False on failure
        """
        if tv_download_dir == '':
            self.tv_download_dir = ''
            return True

        if os.path.normpath(self.tv_download_dir) != os.path.normpath(tv_download_dir):
            if makeDir(tv_download_dir):
                self.tv_download_dir = os.path.normpath(tv_download_dir)
                sickrage.app.log.info("Changed TV download folder to " + tv_download_dir)
            else:
                return False

        return True

    def change_autopostprocessor_freq(self, freq):
        """
        Change frequency of automatic postprocessing thread
        TODO: Make all thread frequency changers in config.py return True/False status

        :param freq: New frequency
        """
        self.autopostprocessor_freq = try_int(freq, self.default_autopostprocessor_freq)
        sickrage.app.scheduler.modify_job('POSTPROCESSOR',
                                          trigger=IntervalTrigger(
                                              minutes=self.autopostprocessor_freq if self.autopostprocessor_freq >= self.min_autopostprocessor_freq else self.min_autopostprocessor_freq
                                          ))

    def change_daily_searcher_freq(self, freq):
        """
        Change frequency of daily search thread

        :param freq: New frequency
        """
        self.daily_searcher_freq = try_int(freq, self.default_daily_searcher_freq)
        sickrage.app.scheduler.modify_job('DAILYSEARCHER',
                                          trigger=IntervalTrigger(
                                              minutes=self.daily_searcher_freq if self.daily_searcher_freq >= self.min_daily_searcher_freq else self.min_daily_searcher_freq
                                          ))

    def change_backlog_searcher_freq(self, freq):
        """
        Change frequency of backlog thread

        :param freq: New frequency
        """
        self.backlog_searcher_freq = try_int(freq, self.default_backlog_searcher_freq)
        self.min_backlog_searcher_freq = sickrage.app.BACKLOGSEARCHER.get_backlog_cycle_time()
        sickrage.app.scheduler.modify_job('BACKLOG',
                                          trigger=IntervalTrigger(
                                              minutes=self.backlog_searcher_freq if self.backlog_searcher_freq >= self.min_backlog_searcher_freq else self.min_backlog_searcher_freq
                                          ))

    def change_updater_freq(self, freq):
        """
        Change frequency of version updater thread

        :param freq: New frequency
        """
        self.version_updater_freq = try_int(freq, self.default_version_update_freq)
        sickrage.app.scheduler.modify_job('VERSIONUPDATER',
                                          trigger=IntervalTrigger(
                                              hours=self.version_updater_freq if self.version_updater_freq >= self.min_version_updater_freq else self.min_version_updater_freq
                                          ))

    def change_showupdate_hour(self, freq):
        """
        Change frequency of show updater thread

        :param freq: New frequency
        """
        self.showupdate_hour = try_int(freq, self.default_showupdate_hour)
        sickrage.app.scheduler.modify_job('SHOWUPDATER',
                                          trigger=IntervalTrigger(
                                              hours=1,
                                              start_date=datetime.datetime.now().replace(
                                                  hour=self.showupdate_hour if self.showupdate_hour >= 0 and self.showupdate_hour <= 23 else 0)
                                          ))

    def change_subtitle_searcher_freq(self, freq):
        """
        Change frequency of subtitle thread

        :param freq: New frequency
        """
        self.subtitle_searcher_freq = try_int(freq, self.default_subtitle_searcher_freq)
        sickrage.app.scheduler.modify_job('SUBTITLESEARCHER',
                                          trigger=IntervalTrigger(
                                              hours=self.subtitle_searcher_freq if self.subtitle_searcher_freq >= self.min_subtitle_searcher_freq else self.min_subtitle_searcher_freq
                                          ))

    def change_version_notify(self, version_notify):
        """
        Change frequency of versioncheck thread

        :param version_notify: New frequency
        """
        self.version_notify = checkbox_to_value(version_notify)
        if not self.version_notify:
            sickrage.app.newest_version_string = None

    def change_download_propers(self, download_propers):
        """
        Enable/Disable proper download thread
        TODO: Make this return True/False on success/failure

        :param download_propers: New desired state
        """
        self.download_propers = checkbox_to_value(download_propers)
        job = sickrage.app.scheduler.get_job('PROPERSEARCHER')
        (job.pause, job.resume)[self.download_propers]()

    def change_use_trakt(self, use_trakt):
        """
        Enable/disable trakt thread
        TODO: Make this return true/false on success/failure

        :param use_trakt: New desired state
        """
        self.use_trakt = checkbox_to_value(use_trakt)
        job = sickrage.app.scheduler.get_job('TRAKTSEARCHER')
        (job.pause, job.resume)[self.use_trakt]()

    def change_use_subtitles(self, use_subtitles):
        """
        Enable/Disable subtitle searcher
        TODO: Make this return true/false on success/failure

        :param use_subtitles: New desired state
        """
        self.use_subtitles = checkbox_to_value(use_subtitles)
        job = sickrage.app.scheduler.get_job('SUBTITLESEARCHER')
        (job.pause, job.resume)[self.use_subtitles]()

    def change_process_automatically(self, process_automatically):
        """
        Enable/Disable postprocessor thread
        TODO: Make this return True/False on success/failure

        :param process_automatically: New desired state
        """
        self.process_automatically = checkbox_to_value(process_automatically)
        job = sickrage.app.scheduler.get_job('POSTPROCESSOR')
        (job.pause, job.resume)[self.process_automatically]()

    ################################################################################
    # check_setting_int                                                            #
    ################################################################################
    def check_setting_int(self, section, key, def_val=None, silent=True):
        def_val = def_val if def_val is not None else self.defaults[section][key]

        my_val = self.config_obj.get(section, {section: key}).get(key, def_val)

        if str(my_val).lower() == "true":
            my_val = 1
        elif str(my_val).lower() == "false":
            my_val = 0

        try:
            my_val = int(my_val)
        except Exception:
            my_val = def_val

        if not silent:
            sickrage.app.log.debug(key + " -> " + str(my_val))

        return my_val

    ################################################################################
    # check_setting_float                                                          #
    ################################################################################
    def check_setting_float(self, section, key, def_val=None, silent=True):
        def_val = def_val if def_val is not None else self.defaults[section][key]

        try:
            my_val = float(self.config_obj.get(section, {section: key}).get(key, def_val))
        except Exception:
            my_val = def_val

        if not silent:
            sickrage.app.log.debug(section + " -> " + str(my_val))

        return my_val

    ################################################################################
    # check_setting_str                                                            #
    ################################################################################
    def check_setting_str(self, section, key, def_val=None, silent=True, censor=False):
        def_val = def_val if def_val is not None else self.defaults[section][key]

        my_val = self.config_obj.get(section, {section: key}).get(key, def_val)

        if censor or (section, key) in sickrage.app.log.CENSORED_ITEMS:
            sickrage.app.log.CENSORED_ITEMS[section, key] = my_val

        if not silent:
            sickrage.app.log.debug(key + " -> " + my_val)

        return my_val

    ################################################################################
    # check_setting_pickle                                                           #
    ################################################################################
    def check_setting_pickle(self, section, key, def_val=None, silent=True):
        def_val = def_val if def_val is not None else self.defaults[section][key]

        try:
            my_val = pickle.loads(self.config_obj.get(section, {section: key}).get(key, def_val))
        except Exception:
            my_val = def_val

        if not silent:
            print(key + " -> " + my_val)

        return my_val

    ################################################################################
    # check_setting_bool                                                           #
    ################################################################################
    def check_setting_bool(self, section, key, def_val=None, silent=True):
        def_val = def_val if def_val is not None else self.defaults[section][key]

        try:
            my_val = checkbox_to_value(self.config_obj.get(section, {section: key}).get(key, def_val))
        except Exception:
            my_val = bool(def_val)

        if not silent:
            print(key + " -> " + my_val)

        return my_val

    def load(self, defaults=False):
        # Make sure we can write to the config file
        if not os.path.isabs(sickrage.app.config_file):
            sickrage.app.config_file = os.path.abspath(os.path.join(sickrage.app.data_dir, sickrage.app.config_file))

        if not os.access(sickrage.app.config_file, os.W_OK):
            if os.path.isfile(sickrage.app.config_file):
                raise SystemExit("Config file '" + sickrage.app.config_file + "' must be writeable.")
            elif not os.access(os.path.dirname(sickrage.app.config_file), os.W_OK):
                raise SystemExit(
                    "Config file root dir '" + os.path.dirname(sickrage.app.config_file) + "' must be writeable.")

        # load config
        self.config_obj = ConfigObj(sickrage.app.config_file, encoding='utf8')

        # use defaults
        if defaults: self.config_obj.clear()

        # decrypt settings
        self.encryption_version = self.check_setting_int('General', 'encryption_version')
        self.encryption_secret = self.check_setting_str('General', 'encryption_secret', censor=True)
        self.config_obj.walk(self.decrypt)

        # migrate config
        self.config_obj = ConfigMigrator(self.config_obj).migrate_config(
            current_version=self.check_setting_int('General', 'config_version'),
            expected_version=self.defaults['General']['config_version']
        )

        # GENERAL SETTINGS
        self.config_version = self.check_setting_int('General', 'config_version')
        self.debug = sickrage.app.debug or self.check_setting_bool('General', 'debug')
        self.developer = sickrage.app.developer or self.check_setting_bool('General', 'developer')
        self.last_db_compact = self.check_setting_int('General', 'last_db_compact')
        self.log_nr = self.check_setting_int('General', 'log_nr')
        self.log_size = self.check_setting_int('General', 'log_size')
        self.socket_timeout = self.check_setting_int('General', 'socket_timeout')
        self.default_page = self.check_setting_str('General', 'default_page')
        self.pip_path = self.check_setting_str('General', 'pip_path')
        self.git_path = self.check_setting_str('General', 'git_path')
        self.git_autoissues = self.check_setting_bool('General', 'git_autoissues')
        self.git_username = self.check_setting_str('General', 'git_username', censor=True)
        self.git_password = self.check_setting_str('General', 'git_password', censor=True)
        self.git_newver = self.check_setting_bool('General', 'git_newver')
        self.git_reset = self.check_setting_bool('General', 'git_reset')
        self.web_port = sickrage.app.web_port or self.check_setting_int('General', 'web_port')
        self.web_host = self.check_setting_str('General', 'web_host')
        self.web_ipv6 = self.check_setting_bool('General', 'web_ipv6')
        self.web_root = self.check_setting_str('General', 'web_root').rstrip("/")
        self.web_log = self.check_setting_bool('General', 'web_log')
        self.web_username = self.check_setting_str('General', 'web_username', censor=True)
        self.web_password = self.check_setting_str('General', 'web_password', censor=True)
        self.web_cookie_secret = self.check_setting_str('General', 'web_cookie_secret')
        self.web_use_gzip = self.check_setting_bool('General', 'web_use_gzip')
        self.ssl_verify = self.check_setting_bool('General', 'ssl_verify')
        self.launch_browser = self.check_setting_bool('General', 'launch_browser')
        self.indexer_default_language = self.check_setting_str('General', 'indexerDefaultLang')
        self.ep_default_deleted_status = self.check_setting_int('General', 'ep_default_deleted_status')
        self.download_url = self.check_setting_str('General', 'download_url')
        self.cpu_preset = self.check_setting_str('General', 'cpu_preset')
        self.anon_redirect = self.check_setting_str('General', 'anon_redirect')
        self.proxy_setting = self.check_setting_str('General', 'proxy_setting')
        self.proxy_indexers = self.check_setting_bool('General', 'proxy_indexers')
        self.trash_remove_show = self.check_setting_bool('General', 'trash_remove_show')
        self.trash_rotate_logs = self.check_setting_bool('General', 'trash_rotate_logs')
        self.sort_article = self.check_setting_bool('General', 'sort_article')
        self.api_key = self.check_setting_str('General', 'api_key', censor=True)
        self.enable_https = self.check_setting_bool('General', 'enable_https')
        self.https_cert = self.check_setting_str('General', 'https_cert')
        self.https_key = self.check_setting_str('General', 'https_key')
        self.handle_reverse_proxy = self.check_setting_bool('General', 'handle_reverse_proxy')
        self.root_dirs = self.check_setting_str('General', 'root_dirs')
        self.quality_default = self.check_setting_int('General', 'quality_default')
        self.status_default = self.check_setting_int('General', 'status_default')
        self.status_default_after = self.check_setting_int('General', 'status_default_after')
        self.version_notify = self.check_setting_bool('General', 'version_notify')
        self.auto_update = self.check_setting_bool('General', 'auto_update')
        self.notify_on_update = self.check_setting_bool('General', 'notify_on_update')
        self.notify_on_login = self.check_setting_bool('General', 'notify_on_login')
        self.flatten_folders_default = self.check_setting_bool('General', 'flatten_folders_default')
        self.indexer_default = self.check_setting_int('General', 'indexer_default')
        self.indexer_timeout = self.check_setting_int('General', 'indexer_timeout')
        self.anime_default = self.check_setting_bool('General', 'anime_default')
        self.scene_default = self.check_setting_bool('General', 'scene_default')
        self.archive_default = self.check_setting_bool('General', 'archive_default')
        self.naming_pattern = self.check_setting_str('General', 'naming_pattern')
        self.naming_abd_pattern = self.check_setting_str('General', 'naming_abd_pattern')
        self.naming_custom_abd = self.check_setting_bool('General', 'naming_custom_abd')
        self.naming_sports_pattern = self.check_setting_str('General', 'naming_sports_pattern')
        self.naming_anime_pattern = self.check_setting_str('General', 'naming_anime_pattern')
        self.naming_anime = self.check_setting_int('General', 'naming_anime')
        self.naming_custom_sports = self.check_setting_bool('General', 'naming_custom_sports')
        self.naming_custom_anime = self.check_setting_bool('General', 'naming_custom_anime')
        self.naming_multi_ep = self.check_setting_int('General', 'naming_multi_ep')
        self.naming_anime_multi_ep = self.check_setting_int('General', 'naming_anime_multi_ep')
        self.naming_strip_year = self.check_setting_bool('General', 'naming_strip_year')
        self.use_nzbs = self.check_setting_bool('General', 'use_nzbs')
        self.use_torrents = self.check_setting_bool('General', 'use_torrents')
        self.nzb_method = self.check_setting_str('General', 'nzb_method')
        self.torrent_method = self.check_setting_str('General', 'torrent_method')
        self.download_propers = self.check_setting_bool('General', 'download_propers')
        self.enable_rss_cache = self.check_setting_bool('General', 'enable_rss_cache')
        self.enable_rss_cache_valid_shows = self.check_setting_bool('General', 'enable_rss_cache_valid_shows')
        self.torrent_file_to_magnet = self.check_setting_bool('General', 'torrent_file_to_magnet')
        self.proper_searcher_interval = self.check_setting_str('General', 'check_propers_interval')
        self.randomize_providers = self.check_setting_bool('General', 'randomize_providers')
        self.allow_high_priority = self.check_setting_bool('General', 'allow_high_priority')
        self.skip_removed_files = self.check_setting_bool('General', 'skip_removed_files')
        self.usenet_retention = self.check_setting_int('General', 'usenet_retention')
        self.daily_searcher_freq = self.check_setting_int('General', 'dailysearch_frequency')
        self.backlog_searcher_freq = self.check_setting_int('General', 'backlog_frequency')
        self.version_updater_freq = self.check_setting_int('General', 'update_frequency')
        self.showupdate_stale = self.check_setting_bool('General', 'showupdate_stale')
        self.showupdate_hour = self.check_setting_int('General', 'showupdate_hour')
        self.backlog_days = self.check_setting_int('General', 'backlog_days')
        self.autopostprocessor_freq = self.check_setting_int('General', 'autopostprocessor_frequency')
        self.tv_download_dir = self.check_setting_str('General', 'tv_download_dir')
        self.process_automatically = self.check_setting_bool('General', 'process_automatically')
        self.no_delete = self.check_setting_bool('General', 'no_delete')
        self.unpack = self.check_setting_bool('General', 'unpack')
        self.rename_episodes = self.check_setting_bool('General', 'rename_episodes')
        self.airdate_episodes = self.check_setting_bool('General', 'airdate_episodes')
        self.file_timestamp_timezone = self.check_setting_str('General', 'file_timestamp_timezone')
        self.keep_processed_dir = self.check_setting_bool('General', 'keep_processed_dir')
        self.process_method = self.check_setting_str('General', 'process_method')
        self.delrarcontents = self.check_setting_bool('General', 'del_rar_contents')
        self.move_associated_files = self.check_setting_bool('General', 'move_associated_files')
        self.postpone_if_sync_files = self.check_setting_bool('General', 'postpone_if_sync_files')
        self.sync_files = self.check_setting_str('General', 'sync_files')
        self.nfo_rename = self.check_setting_bool('General', 'nfo_rename')
        self.create_missing_show_dirs = self.check_setting_bool('General', 'create_missing_show_dirs')
        self.add_shows_wo_dir = self.check_setting_bool('General', 'add_shows_wo_dir')
        self.require_words = self.check_setting_str('General', 'require_words')
        self.ignore_words = self.check_setting_str('General', 'ignore_words')
        self.ignored_subs_list = self.check_setting_str('General', 'ignored_subs_list')
        self.calendar_unprotected = self.check_setting_bool('General', 'calendar_unprotected')
        self.calendar_icons = self.check_setting_bool('General', 'calendar_icons')
        self.no_restart = self.check_setting_bool('General', 'no_restart')
        self.extra_scripts = [x.strip() for x in self.check_setting_str('General', 'extra_scripts').split('|') if
                              x.strip()]
        self.use_listview = self.check_setting_bool('General', 'use_listview')
        self.display_all_seasons = self.check_setting_bool('General', 'display_all_seasons')
        self.random_user_agent = self.check_setting_bool('General', 'random_user_agent')

        # GUI SETTINGS
        self.gui_lang = self.check_setting_str('GUI', 'gui_lang')
        self.theme_name = self.check_setting_str('GUI', 'theme_name')
        self.fanart_background = self.check_setting_bool('GUI', 'fanart_background')
        self.fanart_background_opacity = self.check_setting_float('GUI', 'fanart_background_opacity')
        self.home_layout = self.check_setting_str('GUI', 'home_layout')
        self.history_layout = self.check_setting_str('GUI', 'history_layout')
        self.history_limit = self.check_setting_str('GUI', 'history_limit')
        self.display_show_specials = self.check_setting_bool('GUI', 'display_show_specials')
        self.coming_eps_layout = self.check_setting_str('GUI', 'coming_eps_layout')
        self.coming_eps_display_paused = self.check_setting_bool('GUI', 'coming_eps_display_paused')
        self.coming_eps_sort = self.check_setting_str('GUI', 'coming_eps_sort')
        self.coming_eps_missed_range = self.check_setting_int('GUI', 'coming_eps_missed_range')
        self.fuzzy_dating = self.check_setting_bool('GUI', 'fuzzy_dating')
        self.trim_zero = self.check_setting_bool('GUI', 'trim_zero')
        self.date_preset = self.check_setting_str('GUI', 'date_preset')
        self.time_preset_w_seconds = self.check_setting_str('GUI', 'time_preset')
        self.time_preset = self.time_preset_w_seconds.replace(":%S", "")
        self.timezone_display = self.check_setting_str('GUI', 'timezone_display')
        self.poster_sortby = self.check_setting_str('GUI', 'poster_sortby')
        self.poster_sortdir = self.check_setting_int('GUI', 'poster_sortdir')
        self.filter_row = self.check_setting_bool('GUI', 'filter_row')

        # BLACKHOLE SETTINGS
        self.nzb_dir = self.check_setting_str('Blackhole', 'nzb_dir')
        self.torrent_dir = self.check_setting_str('Blackhole', 'torrent_dir')

        # NZBS SETTINGS
        self.nzbs = self.check_setting_bool('NZBs', 'nzbs')
        self.nzbs_uid = self.check_setting_str('NZBs', 'nzbs_uid')
        self.nzbs_hash = self.check_setting_str('NZBs', 'nzbs_hash', censor=True)

        # NEWZBIN SETTINGS
        self.newzbin = self.check_setting_bool('Newzbin', 'newzbin')
        self.newzbin_username = self.check_setting_str('Newzbin', 'newzbin_username', censor=True)
        self.newzbin_password = self.check_setting_str('Newzbin', 'newzbin_password', censor=True)

        # SABNZBD SETTINGS
        self.sab_username = self.check_setting_str('SABnzbd', 'sab_username', censor=True)
        self.sab_password = self.check_setting_str('SABnzbd', 'sab_password', censor=True)
        self.sab_apikey = self.check_setting_str('SABnzbd', 'sab_apikey', censor=True)
        self.sab_category = self.check_setting_str('SABnzbd', 'sab_category')
        self.sab_category_backlog = self.check_setting_str('SABnzbd', 'sab_category_backlog')
        self.sab_category_anime = self.check_setting_str('SABnzbd', 'sab_category_anime')
        self.sab_category_anime_backlog = self.check_setting_str('SABnzbd', 'sab_category_anime_backlog')
        self.sab_host = self.check_setting_str('SABnzbd', 'sab_host')
        self.sab_forced = self.check_setting_bool('SABnzbd', 'sab_forced')

        # NZBGET SETTINGS
        self.nzbget_username = self.check_setting_str('NZBget', 'nzbget_username', censor=True)
        self.nzbget_password = self.check_setting_str('NZBget', 'nzbget_password', censor=True)
        self.nzbget_category = self.check_setting_str('NZBget', 'nzbget_category')
        self.nzbget_category_backlog = self.check_setting_str('NZBget', 'nzbget_category_backlog')
        self.nzbget_category_anime = self.check_setting_str('NZBget', 'nzbget_category_anime')
        self.nzbget_category_anime_backlog = self.check_setting_str('NZBget', 'nzbget_category_anime_backlog')
        self.nzbget_host = self.check_setting_str('NZBget', 'nzbget_host')
        self.nzbget_use_https = self.check_setting_bool('NZBget', 'nzbget_use_https')
        self.nzbget_priority = self.check_setting_int('NZBget', 'nzbget_priority')

        # TORRENT SETTINGS
        self.torrent_username = self.check_setting_str('TORRENT', 'torrent_username', censor=True)
        self.torrent_password = self.check_setting_str('TORRENT', 'torrent_password', censor=True)
        self.torrent_host = self.check_setting_str('TORRENT', 'torrent_host')
        self.torrent_path = self.check_setting_str('TORRENT', 'torrent_path')
        self.torrent_seed_time = self.check_setting_int('TORRENT', 'torrent_seed_time')
        self.torrent_paused = self.check_setting_bool('TORRENT', 'torrent_paused')
        self.torrent_high_bandwidth = self.check_setting_bool('TORRENT', 'torrent_high_bandwidth')
        self.torrent_label = self.check_setting_str('TORRENT', 'torrent_label')
        self.torrent_label_anime = self.check_setting_str('TORRENT', 'torrent_label_anime')
        self.torrent_verify_cert = self.check_setting_bool('TORRENT', 'torrent_verify_cert')
        self.torrent_rpcurl = self.check_setting_str('TORRENT', 'torrent_rpcurl')
        self.torrent_auth_type = self.check_setting_str('TORRENT', 'torrent_auth_type')

        # KODI SETTINGS
        self.use_kodi = self.check_setting_bool('KODI', 'use_kodi')
        self.kodi_always_on = self.check_setting_bool('KODI', 'kodi_always_on')
        self.kodi_notify_onsnatch = self.check_setting_bool('KODI', 'kodi_notify_onsnatch')
        self.kodi_notify_ondownload = self.check_setting_bool('KODI', 'kodi_notify_ondownload')
        self.kodi_notify_onsubtitledownload = self.check_setting_bool('KODI', 'kodi_notify_onsubtitledownload')
        self.kodi_update_library = self.check_setting_bool('KODI', 'kodi_update_library')
        self.kodi_update_full = self.check_setting_bool('KODI', 'kodi_update_full')
        self.kodi_update_onlyfirst = self.check_setting_bool('KODI', 'kodi_update_onlyfirst')
        self.kodi_host = self.check_setting_str('KODI', 'kodi_host')
        self.kodi_username = self.check_setting_str('KODI', 'kodi_username', censor=True)
        self.kodi_password = self.check_setting_str('KODI', 'kodi_password', censor=True)

        # PLEX SETTINGS
        self.use_plex = self.check_setting_bool('Plex', 'use_plex')
        self.plex_notify_onsnatch = self.check_setting_bool('Plex', 'plex_notify_onsnatch')
        self.plex_notify_ondownload = self.check_setting_bool('Plex', 'plex_notify_ondownload')
        self.plex_notify_onsubtitledownload = self.check_setting_bool('Plex', 'plex_notify_onsubtitledownload')
        self.plex_update_library = self.check_setting_bool('Plex', 'plex_update_library')
        self.plex_server_host = self.check_setting_str('Plex', 'plex_server_host')
        self.plex_server_token = self.check_setting_str('Plex', 'plex_server_token', censor=True)
        self.plex_host = self.check_setting_str('Plex', 'plex_host')
        self.plex_username = self.check_setting_str('Plex', 'plex_username', censor=True)
        self.plex_password = self.check_setting_str('Plex', 'plex_password', censor=True)
        self.use_plex_client = self.check_setting_bool('Plex', 'use_plex_client')
        self.plex_client_username = self.check_setting_str('Plex', 'plex_client_username', censor=True)
        self.plex_client_password = self.check_setting_str('Plex', 'plex_client_password', censor=True)

        # EMBY SETTINGS
        self.use_emby = self.check_setting_bool('Emby', 'use_emby')
        self.emby_host = self.check_setting_str('Emby', 'emby_host')
        self.emby_apikey = self.check_setting_str('Emby', 'emby_apikey', censor=True)

        # GROWL SETTINGS
        self.use_growl = self.check_setting_bool('Growl', 'use_growl')
        self.growl_notify_onsnatch = self.check_setting_bool('Growl', 'growl_notify_onsnatch')
        self.growl_notify_ondownload = self.check_setting_bool('Growl', 'growl_notify_ondownload')
        self.growl_notify_onsubtitledownload = self.check_setting_bool('Growl', 'growl_notify_onsubtitledownload')
        self.growl_host = self.check_setting_str('Growl', 'growl_host')
        self.growl_password = self.check_setting_str('Growl', 'growl_password', censor=True)

        # FREEMOBILE SETTINGS
        self.use_freemobile = self.check_setting_bool('FreeMobile', 'use_freemobile')
        self.freemobile_notify_onsnatch = self.check_setting_bool('FreeMobile', 'freemobile_notify_onsnatch')
        self.freemobile_notify_ondownload = self.check_setting_bool('FreeMobile', 'freemobile_notify_ondownload')
        self.freemobile_notify_onsubtitledownload = self.check_setting_bool('FreeMobile',
                                                                            'freemobile_notify_onsubtitledownload')
        self.freemobile_id = self.check_setting_str('FreeMobile', 'freemobile_id')
        self.freemobile_apikey = self.check_setting_str('FreeMobile', 'freemobile_apikey', censor=True)

        # TELEGRAM SETTINGS
        self.use_telegram = self.check_setting_bool('TELEGRAM', 'use_telegram')
        self.telegram_notify_onsnatch = self.check_setting_bool('TELEGRAM', 'telegram_notify_onsnatch')
        self.telegram_notify_ondownload = self.check_setting_bool('TELEGRAM', 'telegram_notify_ondownload')
        self.telegram_notify_onsubtitledownload = self.check_setting_bool('TELEGRAM',
                                                                          'telegram_notify_onsubtitledownload')
        self.telegram_id = self.check_setting_str('TELEGRAM', 'telegram_id')
        self.telegram_apikey = self.check_setting_str('TELEGRAM', 'telegram_apikey', censor=True)

        # PROWL SETTINGS
        self.use_prowl = self.check_setting_bool('Prowl', 'use_prowl')
        self.prowl_notify_onsnatch = self.check_setting_bool('Prowl', 'prowl_notify_onsnatch')
        self.prowl_notify_ondownload = self.check_setting_bool('Prowl', 'prowl_notify_ondownload')
        self.prowl_notify_onsubtitledownload = self.check_setting_bool('Prowl', 'prowl_notify_onsubtitledownload')
        self.prowl_api = self.check_setting_str('Prowl', 'prowl_api', censor=True)
        self.prowl_priority = self.check_setting_str('Prowl', 'prowl_priority')

        # TWITTER SETTINGS
        self.use_twitter = self.check_setting_bool('Twitter', 'use_twitter')
        self.twitter_notify_onsnatch = self.check_setting_bool('Twitter', 'twitter_notify_onsnatch')
        self.twitter_notify_ondownload = self.check_setting_bool('Twitter', 'twitter_notify_ondownload')
        self.twitter_notify_onsubtitledownload = self.check_setting_bool('Twitter', 'twitter_notify_onsubtitledownload')
        self.twitter_username = self.check_setting_str('Twitter', 'twitter_username', censor=True)
        self.twitter_password = self.check_setting_str('Twitter', 'twitter_password', censor=True)
        self.twitter_prefix = self.check_setting_str('Twitter', 'twitter_prefix', 'SiCKRAGE')
        self.twitter_dmto = self.check_setting_str('Twitter', 'twitter_dmto')
        self.twitter_usedm = self.check_setting_bool('Twitter', 'twitter_usedm')

        self.use_twilio = self.check_setting_bool('Twilio', 'use_twilio')
        self.twilio_notify_onsnatch = self.check_setting_bool('Twilio', 'twilio_notify_onsnatch')
        self.twilio_notify_ondownload = self.check_setting_bool('Twilio', 'twilio_notify_ondownload')
        self.twilio_notify_onsubtitledownload = self.check_setting_bool('Twilio', 'twilio_notify_onsubtitledownload')
        self.twilio_phone_sid = self.check_setting_str('Twilio', 'twilio_phone_sid', censor=True)
        self.twilio_account_sid = self.check_setting_str('Twilio', 'twilio_account_sid', censor=True)
        self.twilio_auth_token = self.check_setting_str('Twilio', 'twilio_auth_token', censor=True)
        self.twilio_to_number = self.check_setting_str('Twilio', 'twilio_to_number', censor=True)

        self.use_boxcar2 = self.check_setting_bool('Boxcar2', 'use_boxcar2')
        self.boxcar2_notify_onsnatch = self.check_setting_bool('Boxcar2', 'boxcar2_notify_onsnatch')
        self.boxcar2_notify_ondownload = self.check_setting_bool('Boxcar2', 'boxcar2_notify_ondownload')
        self.boxcar2_notify_onsubtitledownload = self.check_setting_bool('Boxcar2', 'boxcar2_notify_onsubtitledownload')
        self.boxcar2_accesstoken = self.check_setting_str('Boxcar2', 'boxcar2_accesstoken', censor=True)

        self.use_pushover = self.check_setting_bool('Pushover', 'use_pushover')
        self.pushover_notify_onsnatch = self.check_setting_bool('Pushover', 'pushover_notify_onsnatch')
        self.pushover_notify_ondownload = self.check_setting_bool('Pushover', 'pushover_notify_ondownload')
        self.pushover_notify_onsubtitledownload = self.check_setting_bool('Pushover',
                                                                          'pushover_notify_onsubtitledownload')
        self.pushover_userkey = self.check_setting_str('Pushover', 'pushover_userkey', censor=True)
        self.pushover_apikey = self.check_setting_str('Pushover', 'pushover_apikey', censor=True)
        self.pushover_device = self.check_setting_str('Pushover', 'pushover_device')
        self.pushover_sound = self.check_setting_str('Pushover', 'pushover_sound', 'pushover')

        self.use_libnotify = self.check_setting_bool('Libnotify', 'use_libnotify')
        self.libnotify_notify_onsnatch = self.check_setting_bool('Libnotify', 'libnotify_notify_onsnatch')
        self.libnotify_notify_ondownload = self.check_setting_bool('Libnotify', 'libnotify_notify_ondownload')
        self.libnotify_notify_onsubtitledownload = self.check_setting_bool('Libnotify',
                                                                           'libnotify_notify_onsubtitledownload')

        self.use_nmj = self.check_setting_bool('NMJ', 'use_nmj')
        self.nmj_host = self.check_setting_str('NMJ', 'nmj_host')
        self.nmj_database = self.check_setting_str('NMJ', 'nmj_database')
        self.nmj_mount = self.check_setting_str('NMJ', 'nmj_mount')

        self.use_nmjv2 = self.check_setting_bool('NMJv2', 'use_nmjv2')
        self.nmjv2_host = self.check_setting_str('NMJv2', 'nmjv2_host')
        self.nmjv2_database = self.check_setting_str('NMJv2', 'nmjv2_database')
        self.nmjv2_dbloc = self.check_setting_str('NMJv2', 'nmjv2_dbloc')

        self.use_synoindex = self.check_setting_bool('Synology', 'use_synoindex')

        self.use_synologynotifier = self.check_setting_bool('SynologyNotifier', 'use_synologynotifier')
        self.synologynotifier_notify_onsnatch = self.check_setting_bool('SynologyNotifier',
                                                                        'synologynotifier_notify_onsnatch')
        self.synologynotifier_notify_ondownload = self.check_setting_bool('SynologyNotifier',
                                                                          'synologynotifier_notify_ondownload')
        self.synologynotifier_notify_onsubtitledownload = self.check_setting_bool('SynologyNotifier',
                                                                                  'synologynotifier_notify_onsubtitledownload')

        self.thetvdb_apitoken = self.check_setting_str('theTVDB', 'thetvdb_apitoken', censor=True)

        self.use_slack = self.check_setting_bool('Slack', 'use_slack')
        self.slack_notify_onsnatch = self.check_setting_bool('Slack', 'slack_notify_onsnatch')
        self.slack_notify_ondownload = self.check_setting_bool('Slack', 'slack_notify_ondownload')
        self.slack_notify_onsubtitledownload = self.check_setting_bool('Slack', 'slack_notify_onsubtitledownload')
        self.slack_webhook = self.check_setting_str('Slack', 'slack_webhook')

        self.use_discord = self.check_setting_bool('Discord', 'use_discord')
        self.discord_notify_onsnatch = self.check_setting_bool('Discord', 'discord_notify_onsnatch')
        self.discord_notify_ondownload = self.check_setting_bool('Discord', 'discord_notify_ondownload')
        self.discord_notify_onsubtitledownload = self.check_setting_bool('Discord', 'discord_notify_onsubtitledownload')
        self.discord_webhook = self.check_setting_str('Discord', 'discord_webhook')
        self.discord_avatar_url = self.check_setting_str('Discord', 'discord_avatar_url')
        self.discord_name = self.check_setting_str('Discord', 'discord_name')
        self.discord_tts = self.check_setting_bool('Discord', 'discord_tts')

        self.use_trakt = self.check_setting_bool('Trakt', 'use_trakt')
        self.trakt_username = self.check_setting_str('Trakt', 'trakt_username', censor=True)
        self.trakt_oauth_token = self.check_setting_pickle('Trakt', 'trakt_oauth_token')
        self.trakt_remove_watchlist = self.check_setting_bool('Trakt', 'trakt_remove_watchlist')
        self.trakt_remove_serieslist = self.check_setting_bool('Trakt', 'trakt_remove_serieslist')
        self.trakt_remove_show_from_sickrage = self.check_setting_bool('Trakt', 'trakt_remove_show_from_sickrage')
        self.trakt_sync_watchlist = self.check_setting_bool('Trakt', 'trakt_sync_watchlist')
        self.trakt_method_add = self.check_setting_int('Trakt', 'trakt_method_add')
        self.trakt_start_paused = self.check_setting_bool('Trakt', 'trakt_start_paused')
        self.trakt_use_recommended = self.check_setting_bool('Trakt', 'trakt_use_recommended')
        self.trakt_sync = self.check_setting_bool('Trakt', 'trakt_sync')
        self.trakt_sync_remove = self.check_setting_bool('Trakt', 'trakt_sync_remove')
        self.trakt_default_indexer = self.check_setting_int('Trakt', 'trakt_default_indexer')
        self.trakt_timeout = self.check_setting_int('Trakt', 'trakt_timeout')
        self.trakt_blacklist_name = self.check_setting_str('Trakt', 'trakt_blacklist_name')

        self.use_pytivo = self.check_setting_bool('pyTivo', 'use_pytivo')
        self.pytivo_notify_onsnatch = self.check_setting_bool('pyTivo', 'pytivo_notify_onsnatch')
        self.pytivo_notify_ondownload = self.check_setting_bool('pyTivo', 'pytivo_notify_ondownload')
        self.pytivo_notify_onsubtitledownload = self.check_setting_bool('pyTivo', 'pytivo_notify_onsubtitledownload')
        self.pytivo_update_library = self.check_setting_bool('pyTivo', 'pyTivo_update_library')
        self.pytivo_host = self.check_setting_str('pyTivo', 'pytivo_host')
        self.pytivo_share_name = self.check_setting_str('pyTivo', 'pytivo_share_name')
        self.pytivo_tivo_name = self.check_setting_str('pyTivo', 'pytivo_tivo_name')

        self.use_nma = self.check_setting_bool('NMA', 'use_nma')
        self.nma_notify_onsnatch = self.check_setting_bool('NMA', 'nma_notify_onsnatch')
        self.nma_notify_ondownload = self.check_setting_bool('NMA', 'nma_notify_ondownload')
        self.nma_notify_onsubtitledownload = self.check_setting_bool('NMA', 'nma_notify_onsubtitledownload')
        self.nma_api = self.check_setting_str('NMA', 'nma_api', censor=True)
        self.nma_priority = self.check_setting_str('NMA', 'nma_priority')

        self.use_pushalot = self.check_setting_bool('Pushalot', 'use_pushalot')
        self.pushalot_notify_onsnatch = self.check_setting_bool('Pushalot', 'pushalot_notify_onsnatch')
        self.pushalot_notify_ondownload = self.check_setting_bool('Pushalot', 'pushalot_notify_ondownload')
        self.pushalot_notify_onsubtitledownload = self.check_setting_bool('Pushalot',
                                                                          'pushalot_notify_onsubtitledownload')
        self.pushalot_authorizationtoken = self.check_setting_str('Pushalot', 'pushalot_authorizationtoken',
                                                                  censor=True)

        self.use_pushbullet = self.check_setting_bool('Pushbullet', 'use_pushbullet')
        self.pushbullet_notify_onsnatch = self.check_setting_bool('Pushbullet', 'pushbullet_notify_onsnatch')
        self.pushbullet_notify_ondownload = self.check_setting_bool('Pushbullet', 'pushbullet_notify_ondownload')
        self.pushbullet_notify_onsubtitledownload = self.check_setting_bool('Pushbullet',
                                                                            'pushbullet_notify_onsubtitledownload')
        self.pushbullet_api = self.check_setting_str('Pushbullet', 'pushbullet_api', censor=True)
        self.pushbullet_device = self.check_setting_str('Pushbullet', 'pushbullet_device')

        self.use_email = self.check_setting_bool('Email', 'use_email')
        self.email_notify_onsnatch = self.check_setting_bool('Email', 'email_notify_onsnatch')
        self.email_notify_ondownload = self.check_setting_bool('Email', 'email_notify_ondownload')
        self.email_notify_onsubtitledownload = self.check_setting_bool('Email', 'email_notify_onsubtitledownload')
        self.email_host = self.check_setting_str('Email', 'email_host')
        self.email_port = self.check_setting_int('Email', 'email_port')
        self.email_tls = self.check_setting_bool('Email', 'email_tls')
        self.email_user = self.check_setting_str('Email', 'email_user', censor=True)
        self.email_password = self.check_setting_str('Email', 'email_password', censor=True)
        self.email_from = self.check_setting_str('Email', 'email_from')
        self.email_list = self.check_setting_str('Email', 'email_list')

        # SUBTITLE SETTINGS
        self.use_subtitles = self.check_setting_bool('Subtitles', 'use_subtitles')
        self.subtitles_languages = self.check_setting_str('Subtitles', 'subtitles_languages').split(',')
        self.subtitles_dir = self.check_setting_str('Subtitles', 'subtitles_dir')
        self.subtitles_services_list = self.check_setting_str('Subtitles', 'subtitles_services_list').split(',')
        self.subtitles_default = self.check_setting_bool('Subtitles', 'subtitles_default')
        self.subtitles_history = self.check_setting_bool('Subtitles', 'subtitles_history')
        self.subtitles_hearing_impaired = self.check_setting_bool('Subtitles', 'subtitles_hearing_impaired')
        self.embedded_subtitles_all = self.check_setting_bool('Subtitles', 'embedded_subtitles_all')
        self.subtitles_multi = self.check_setting_bool('Subtitles', 'subtitles_multi')
        self.subtitles_services_enabled = [int(x) for x in
                                           self.check_setting_str('Subtitles', 'subtitles_services_enabled').split('|')
                                           if x]
        self.subtitles_extra_scripts = [x.strip() for x in
                                        self.check_setting_str('Subtitles', 'subtitles_extra_scripts').split('|') if
                                        x.strip()]
        self.addic7ed_user = self.check_setting_str('Subtitles', 'addic7ed_username', censor=True)
        self.addic7ed_pass = self.check_setting_str('Subtitles', 'addic7ed_password', censor=True)
        self.legendastv_user = self.check_setting_str('Subtitles', 'legendastv_username', censor=True)
        self.legendastv_pass = self.check_setting_str('Subtitles', 'legendastv_password', censor=True)
        self.itasa_user = self.check_setting_str('Subtitles', 'itasa_username', censor=True)
        self.itasa_pass = self.check_setting_str('Subtitles', 'itasa_password', censor=True)
        self.opensubtitles_user = self.check_setting_str('Subtitles', 'opensubtitles_username', censor=True)
        self.opensubtitles_pass = self.check_setting_str('Subtitles', 'opensubtitles_password', censor=True)
        self.subtitle_searcher_freq = self.check_setting_int('Subtitles', 'subtitles_finder_frequency')

        # FAILED DOWNLOAD SETTINGS
        self.use_failed_downloads = self.check_setting_bool('FailedDownloads', 'use_failed_downloads')
        self.delete_failed = self.check_setting_bool('FailedDownloads', 'delete_failed')

        # ANIDB SETTINGS
        self.use_anidb = self.check_setting_bool('ANIDB', 'use_anidb')
        self.anidb_username = self.check_setting_str('ANIDB', 'anidb_username', censor=True)
        self.anidb_password = self.check_setting_str('ANIDB', 'anidb_password', censor=True)
        self.anidb_use_mylist = self.check_setting_bool('ANIDB', 'anidb_use_mylist')
        self.anime_split_home = self.check_setting_bool('ANIME', 'anime_split_home')

        self.quality_sizes = self.check_setting_pickle('Quality', 'sizes')

        self.custom_providers = self.check_setting_str('Providers', 'custom_providers')

        for providerID, providerObj in sickrage.app.search_providers.all().items():
            providerSettings = self.check_setting_str('Providers', providerID, '') or {}
            for k, v in providerSettings.items():
                providerSettings[k] = auto_type(v)

            [setattr(providerObj, x, providerSettings[x]) for x in
             set(providerObj.__dict__).intersection(providerSettings)]

        # order providers
        sickrage.app.search_providers.provider_order = self.check_setting_str('Providers', 'providers_order')

        for metadataProviderID, metadataProviderObj in sickrage.app.metadata_providers.items():
            metadataProviderObj.set_config(
                self.check_setting_str('MetadataProviders', metadataProviderID, '0|0|0|0|0|0|0|0|0|0|0')
            )

        # mark config settings loaded
        self.loaded = True

        # save config settings
        self.save()

    def save(self):
        # dont bother saving settings if there not loaded
        if not self.loaded:
            return

        new_config = ConfigObj(sickrage.app.config_file, indent_type='  ', encoding='utf8')
        new_config.clear()

        sickrage.app.log.debug("Saving all settings to disk")

        new_config.update({
            'General': {
                'config_version': self.config_version,
                'encryption_version': int(self.encryption_version),
                'encryption_secret': self.encryption_secret,
                'last_db_compact': self.last_db_compact,
                'git_autoissues': int(self.git_autoissues),
                'git_username': self.git_username,
                'git_password': self.git_password,
                'git_reset': int(self.git_reset),
                'git_newver': int(self.git_newver),
                'log_nr': int(self.log_nr),
                'log_size': int(self.log_size),
                'socket_timeout': self.socket_timeout,
                'web_port': self.web_port,
                'web_host': self.web_host,
                'web_ipv6': int(self.web_ipv6),
                'web_log': int(self.web_log),
                'web_root': self.web_root,
                'web_username': self.web_username,
                'web_password': self.web_password,
                'web_cookie_secret': self.web_cookie_secret,
                'web_use_gzip': int(self.web_use_gzip),
                'ssl_verify': int(self.ssl_verify),
                'download_url': self.download_url,
                'cpu_preset': self.cpu_preset,
                'anon_redirect': self.anon_redirect,
                'api_key': self.api_key,
                'debug': int(self.debug),
                'default_page': self.default_page,
                'enable_https': int(self.enable_https),
                'https_cert': self.https_cert,
                'https_key': self.https_key,
                'handle_reverse_proxy': int(self.handle_reverse_proxy),
                'use_nzbs': int(self.use_nzbs),
                'use_torrents': int(self.use_torrents),
                'nzb_method': self.nzb_method,
                'torrent_method': self.torrent_method,
                'usenet_retention': int(self.usenet_retention),
                'autopostprocessor_frequency': int(self.autopostprocessor_freq),
                'dailysearch_frequency': int(self.daily_searcher_freq),
                'backlog_frequency': int(self.backlog_searcher_freq),
                'update_frequency': int(self.version_updater_freq),
                'showupdate_hour': int(self.showupdate_hour),
                'showupdate_stale': int(self.showupdate_stale),
                'download_propers': int(self.download_propers),
                'enable_rss_cache': int(self.enable_rss_cache),
                'enable_rss_cache_valid_shows': int(self.enable_rss_cache_valid_shows),
                'torrent_file_to_magnet': int(self.torrent_file_to_magnet),
                'randomize_providers': int(self.randomize_providers),
                'check_propers_interval': self.proper_searcher_interval,
                'allow_high_priority': int(self.allow_high_priority),
                'skip_removed_files': int(self.skip_removed_files),
                'quality_default': int(self.quality_default),
                'status_default': int(self.status_default),
                'status_default_after': int(self.status_default_after),
                'flatten_folders_default': int(self.flatten_folders_default),
                'indexer_default': int(self.indexer_default),
                'indexer_timeout': int(self.indexer_timeout),
                'anime_default': int(self.anime_default),
                'scene_default': int(self.scene_default),
                'archive_default': int(self.archive_default),
                'version_notify': int(self.version_notify),
                'auto_update': int(self.auto_update),
                'notify_on_update': int(self.notify_on_update),
                'notify_on_login': int(self.notify_on_login),
                'naming_strip_year': int(self.naming_strip_year),
                'naming_pattern': self.naming_pattern,
                'naming_custom_abd': int(self.naming_custom_abd),
                'naming_abd_pattern': self.naming_abd_pattern,
                'naming_custom_sports': int(self.naming_custom_sports),
                'naming_sports_pattern': self.naming_sports_pattern,
                'naming_custom_anime': int(self.naming_custom_anime),
                'naming_anime_pattern': self.naming_anime_pattern,
                'naming_multi_ep': int(self.naming_multi_ep),
                'naming_anime_multi_ep': int(self.naming_anime_multi_ep),
                'naming_anime': int(self.naming_anime),
                'indexerDefaultLang': self.indexer_default_language,
                'ep_default_deleted_status': int(self.ep_default_deleted_status),
                'launch_browser': int(self.launch_browser),
                'trash_remove_show': int(self.trash_remove_show),
                'trash_rotate_logs': int(self.trash_rotate_logs),
                'sort_article': int(self.sort_article),
                'proxy_setting': self.proxy_setting,
                'proxy_indexers': int(self.proxy_indexers),
                'use_listview': int(self.use_listview),
                'backlog_days': int(self.backlog_days),
                'root_dirs': self.root_dirs,
                'tv_download_dir': self.tv_download_dir,
                'keep_processed_dir': int(self.keep_processed_dir),
                'process_method': self.process_method,
                'del_rar_contents': int(self.delrarcontents),
                'move_associated_files': int(self.move_associated_files),
                'sync_files': self.sync_files,
                'postpone_if_sync_files': int(self.postpone_if_sync_files),
                'nfo_rename': int(self.nfo_rename),
                'process_automatically': int(self.process_automatically),
                'no_delete': int(self.no_delete),
                'unpack': int(self.unpack),
                'rename_episodes': int(self.rename_episodes),
                'airdate_episodes': int(self.airdate_episodes),
                'file_timestamp_timezone': self.file_timestamp_timezone,
                'create_missing_show_dirs': int(self.create_missing_show_dirs),
                'add_shows_wo_dir': int(self.add_shows_wo_dir),
                'extra_scripts': '|'.join(self.extra_scripts),
                'pip_path': self.pip_path,
                'git_path': self.git_path,
                'ignore_words': self.ignore_words,
                'require_words': self.require_words,
                'ignored_subs_list': self.ignored_subs_list,
                'calendar_unprotected': int(self.calendar_unprotected),
                'calendar_icons': int(self.calendar_icons),
                'no_restart': int(self.no_restart),
                'developer': int(self.developer),
                'display_all_seasons': int(self.display_all_seasons),
                'random_user_agent': int(self.random_user_agent),
            },
            'GUI': {
                'gui_lang': self.gui_lang,
                'theme_name': self.theme_name,
                'home_layout': self.home_layout,
                'history_layout': self.history_layout,
                'history_limit': self.history_limit,
                'display_show_specials': int(self.display_show_specials),
                'coming_eps_layout': self.coming_eps_layout,
                'coming_eps_display_paused': int(self.coming_eps_display_paused),
                'coming_eps_sort': self.coming_eps_sort,
                'coming_eps_missed_range': int(self.coming_eps_missed_range),
                'fuzzy_dating': int(self.fuzzy_dating),
                'trim_zero': int(self.trim_zero),
                'date_preset': self.date_preset,
                'time_preset': self.time_preset_w_seconds,
                'timezone_display': self.timezone_display,
                'poster_sortby': self.poster_sortby,
                'poster_sortdir': self.poster_sortdir,
                'filter_row': int(self.filter_row),
                'fanart_background': int(self.fanart_background),
                'fanart_background_opacity': self.fanart_background_opacity,
            },
            'Blackhole': {
                'nzb_dir': self.nzb_dir,
                'torrent_dir': self.torrent_dir,
            },
            'NZBs': {
                'nzbs': int(self.nzbs),
                'nzbs_uid': self.nzbs_uid,
                'nzbs_hash': self.nzbs_hash,
            },
            'Newzbin': {
                'newzbin': int(self.newzbin),
                'newzbin_username': self.newzbin_username,
                'newzbin_password': self.newzbin_password,
            },
            'SABnzbd': {
                'sab_username': self.sab_username,
                'sab_password': self.sab_password,
                'sab_apikey': self.sab_apikey,
                'sab_category': self.sab_category,
                'sab_category_backlog': self.sab_category_backlog,
                'sab_category_anime': self.sab_category_anime,
                'sab_category_anime_backlog': self.sab_category_anime_backlog,
                'sab_host': self.sab_host,
                'sab_forced': int(self.sab_forced),
            },
            'NZBget': {
                'nzbget_username': self.nzbget_username,
                'nzbget_password': self.nzbget_password,
                'nzbget_category': self.nzbget_category,
                'nzbget_category_backlog': self.nzbget_category_backlog,
                'nzbget_category_anime': self.nzbget_category_anime,
                'nzbget_category_anime_backlog': self.nzbget_category_anime_backlog,
                'nzbget_host': self.nzbget_host,
                'nzbget_use_https': int(self.nzbget_use_https),
                'nzbget_priority': self.nzbget_priority,
            },
            'TORRENT': {
                'torrent_username': self.torrent_username,
                'torrent_password': self.torrent_password,
                'torrent_host': self.torrent_host,
                'torrent_path': self.torrent_path,
                'torrent_seed_time': int(self.torrent_seed_time),
                'torrent_paused': int(self.torrent_paused),
                'torrent_high_bandwidth': int(self.torrent_high_bandwidth),
                'torrent_label': self.torrent_label,
                'torrent_label_anime': self.torrent_label_anime,
                'torrent_verify_cert': int(self.torrent_verify_cert),
                'torrent_rpcurl': self.torrent_rpcurl,
                'torrent_auth_type': self.torrent_auth_type,
            },
            'KODI': {
                'use_kodi': int(self.use_kodi),
                'kodi_always_on': int(self.kodi_always_on),
                'kodi_notify_onsnatch': int(self.kodi_notify_onsnatch),
                'kodi_notify_ondownload': int(self.kodi_notify_ondownload),
                'kodi_notify_onsubtitledownload': int(self.kodi_notify_onsubtitledownload),
                'kodi_update_library': int(self.kodi_update_library),
                'kodi_update_full': int(self.kodi_update_full),
                'kodi_update_onlyfirst': int(self.kodi_update_onlyfirst),
                'kodi_host': self.kodi_host,
                'kodi_username': self.kodi_username,
                'kodi_password': self.kodi_password,
            },
            'Plex': {
                'use_plex': int(self.use_plex),
                'plex_notify_onsnatch': int(self.plex_notify_onsnatch),
                'plex_notify_ondownload': int(self.plex_notify_ondownload),
                'plex_notify_onsubtitledownload': int(self.plex_notify_onsubtitledownload),
                'plex_update_library': int(self.plex_update_library),
                'plex_server_host': self.plex_server_host,
                'plex_server_token': self.plex_server_token,
                'plex_host': self.plex_host,
                'plex_username': self.plex_username,
                'plex_password': self.plex_password,
            },
            'Emby': {
                'use_emby': int(self.use_emby),
                'emby_host': self.emby_host,
                'emby_apikey': self.emby_apikey,
            },
            'Growl': {
                'use_growl': int(self.use_growl),
                'growl_notify_onsnatch': int(self.growl_notify_onsnatch),
                'growl_notify_ondownload': int(self.growl_notify_ondownload),
                'growl_notify_onsubtitledownload': int(self.growl_notify_onsubtitledownload),
                'growl_host': self.growl_host,
                'growl_password': self.growl_password,
            },
            'FreeMobile': {
                'use_freemobile': int(self.use_freemobile),
                'freemobile_notify_onsnatch': int(self.freemobile_notify_onsnatch),
                'freemobile_notify_ondownload': int(self.freemobile_notify_ondownload),
                'freemobile_notify_onsubtitledownload': int(self.freemobile_notify_onsubtitledownload),
                'freemobile_id': self.freemobile_id,
                'freemobile_apikey': self.freemobile_apikey,
            },
            'TELEGRAM': {
                'use_telegram': int(self.use_telegram),
                'telegram_notify_onsnatch': int(self.telegram_notify_onsnatch),
                'telegram_notify_ondownload': int(self.telegram_notify_ondownload),
                'telegram_notify_onsubtitledownload': int(self.telegram_notify_onsubtitledownload),
                'telegram_id': self.telegram_id,
                'telegram_apikey': self.telegram_apikey,
            },
            'Prowl': {
                'use_prowl': int(self.use_prowl),
                'prowl_notify_onsnatch': int(self.prowl_notify_onsnatch),
                'prowl_notify_ondownload': int(self.prowl_notify_ondownload),
                'prowl_notify_onsubtitledownload': int(self.prowl_notify_onsubtitledownload),
                'prowl_api': self.prowl_api,
                'prowl_priority': self.prowl_priority,
            },
            'Twitter': {
                'use_twitter': int(self.use_twitter),
                'twitter_notify_onsnatch': int(self.twitter_notify_onsnatch),
                'twitter_notify_ondownload': int(self.twitter_notify_ondownload),
                'twitter_notify_onsubtitledownload': int(self.twitter_notify_onsubtitledownload),
                'twitter_username': self.twitter_username,
                'twitter_password': self.twitter_password,
                'twitter_prefix': self.twitter_prefix,
                'twitter_dmto': self.twitter_dmto,
                'twitter_usedm': int(self.twitter_usedm),
            },
            'Twilio': {
                'use_twilio': int(self.use_twilio),
                'twilio_notify_onsnatch': int(self.twilio_notify_onsnatch),
                'twilio_notify_ondownload': int(self.twilio_notify_ondownload),
                'twilio_notify_onsubtitledownload': int(self.twilio_notify_onsubtitledownload),
                'twilio_phone_sid': self.twilio_phone_sid,
                'twilio_account_sid': self.twilio_account_sid,
                'twilio_auth_token': self.twilio_auth_token,
                'twilio_to_number': self.twilio_to_number,
            },
            'Boxcar2': {
                'use_boxcar2': int(self.use_boxcar2),
                'boxcar2_notify_onsnatch': int(self.boxcar2_notify_onsnatch),
                'boxcar2_notify_ondownload': int(self.boxcar2_notify_ondownload),
                'boxcar2_notify_onsubtitledownload': int(self.boxcar2_notify_onsubtitledownload),
                'boxcar2_accesstoken': self.boxcar2_accesstoken,
            },
            'Pushover': {
                'use_pushover': int(self.use_pushover),
                'pushover_notify_onsnatch': int(self.pushover_notify_onsnatch),
                'pushover_notify_ondownload': int(self.pushover_notify_ondownload),
                'pushover_notify_onsubtitledownload': int(self.pushover_notify_onsubtitledownload),
                'pushover_userkey': self.pushover_userkey,
                'pushover_apikey': self.pushover_apikey,
                'pushover_device': self.pushover_device,
                'pushover_sound': self.pushover_sound,
            },
            'Libnotify': {
                'use_libnotify': int(self.use_libnotify),
                'libnotify_notify_onsnatch': int(self.libnotify_notify_onsnatch),
                'libnotify_notify_ondownload': int(self.libnotify_notify_ondownload),
                'libnotify_notify_onsubtitledownload': int(self.libnotify_notify_onsubtitledownload)
            },
            'NMJ': {
                'use_nmj': int(self.use_nmj),
                'nmj_host': self.nmj_host,
                'nmj_database': self.nmj_database,
                'nmj_mount': self.nmj_mount,
            },
            'NMJv2': {
                'use_nmjv2': int(self.use_nmjv2),
                'nmjv2_host': self.nmjv2_host,
                'nmjv2_database': self.nmjv2_database,
                'nmjv2_dbloc': self.nmjv2_dbloc,
            },
            'Synology': {
                'use_synoindex': int(self.use_synoindex),
            },
            'SynologyNotifier': {
                'use_synologynotifier': int(self.use_synologynotifier),
                'synologynotifier_notify_onsnatch': int(self.synologynotifier_notify_onsnatch),
                'synologynotifier_notify_ondownload': int(self.synologynotifier_notify_ondownload),
                'synologynotifier_notify_onsubtitledownload': int(self.synologynotifier_notify_onsubtitledownload),
            },
            'theTVDB': {
                'thetvdb_apitoken': self.thetvdb_apitoken,
            },
            'Slack': {
                'use_slack': int(self.use_slack),
                'slack_notify_onsnatch': int(self.slack_notify_onsnatch),
                'slack_notify_ondownload': int(self.slack_notify_ondownload),
                'slack_notify_onsubtitledownload': int(self.slack_notify_onsubtitledownload),
                'slack_webhook': self.slack_webhook
            },
            'Discord': {
                'use_discord': int(self.use_discord),
                'discord_notify_onsnatch': int(self.discord_notify_onsnatch),
                'discord_notify_ondownload': int(self.discord_notify_ondownload),
                'discord_notify_onsubtitledownload': int(self.discord_notify_onsubtitledownload),
                'discord_webhook': self.discord_webhook,
                'discord_name': self.discord_name,
                'discord_avatar_url': self.discord_avatar_url,
                'discord_tts': int(self.discord_tts)
            },
            'Trakt': {
                'use_trakt': int(self.use_trakt),
                'trakt_username': self.trakt_username,
                'trakt_oauth_token': pickle.dumps(self.trakt_oauth_token),
                'trakt_remove_watchlist': int(self.trakt_remove_watchlist),
                'trakt_remove_serieslist': int(self.trakt_remove_serieslist),
                'trakt_remove_show_from_sickrage': int(self.trakt_remove_show_from_sickrage),
                'trakt_sync_watchlist': int(self.trakt_sync_watchlist),
                'trakt_method_add': int(self.trakt_method_add),
                'trakt_start_paused': int(self.trakt_start_paused),
                'trakt_use_recommended': int(self.trakt_use_recommended),
                'trakt_sync': int(self.trakt_sync),
                'trakt_sync_remove': int(self.trakt_sync_remove),
                'trakt_default_indexer': int(self.trakt_default_indexer),
                'trakt_timeout': int(self.trakt_timeout),
                'trakt_blacklist_name': self.trakt_blacklist_name,
            },
            'pyTivo': {
                'use_pytivo': int(self.use_pytivo),
                'pytivo_notify_onsnatch': int(self.pytivo_notify_onsnatch),
                'pytivo_notify_ondownload': int(self.pytivo_notify_ondownload),
                'pytivo_notify_onsubtitledownload': int(self.pytivo_notify_onsubtitledownload),
                'pyTivo_update_library': int(self.pytivo_update_library),
                'pytivo_host': self.pytivo_host,
                'pytivo_share_name': self.pytivo_share_name,
                'pytivo_tivo_name': self.pytivo_tivo_name,
            },
            'NMA': {
                'use_nma': int(self.use_nma),
                'nma_notify_onsnatch': int(self.nma_notify_onsnatch),
                'nma_notify_ondownload': int(self.nma_notify_ondownload),
                'nma_notify_onsubtitledownload': int(self.nma_notify_onsubtitledownload),
                'nma_api': self.nma_api,
                'nma_priority': self.nma_priority,
            },
            'Pushalot': {
                'use_pushalot': int(self.use_pushalot),
                'pushalot_notify_onsnatch': int(self.pushalot_notify_onsnatch),
                'pushalot_notify_ondownload': int(self.pushalot_notify_ondownload),
                'pushalot_notify_onsubtitledownload': int(self.pushalot_notify_onsubtitledownload),
                'pushalot_authorizationtoken': self.pushalot_authorizationtoken,
            },
            'Pushbullet': {
                'use_pushbullet': int(self.use_pushbullet),
                'pushbullet_notify_onsnatch': int(self.pushbullet_notify_onsnatch),
                'pushbullet_notify_ondownload': int(self.pushbullet_notify_ondownload),
                'pushbullet_notify_onsubtitledownload': int(self.pushbullet_notify_onsubtitledownload),
                'pushbullet_api': self.pushbullet_api,
                'pushbullet_device': self.pushbullet_device,
            },
            'Email': {
                'use_email': int(self.use_email),
                'email_notify_onsnatch': int(self.email_notify_onsnatch),
                'email_notify_ondownload': int(self.email_notify_ondownload),
                'email_notify_onsubtitledownload': int(self.email_notify_onsubtitledownload),
                'email_host': self.email_host,
                'email_port': int(self.email_port),
                'email_tls': int(self.email_tls),
                'email_user': self.email_user,
                'email_password': self.email_password,
                'email_from': self.email_from,
                'email_list': self.email_list,
            },
            'Subtitles': {
                'use_subtitles': int(self.use_subtitles),
                'subtitles_languages': ','.join(self.subtitles_languages),
                'subtitles_services_list': ','.join(self.subtitles_services_list),
                'subtitles_services_enabled': '|'.join([str(x) for x in self.subtitles_services_enabled]),
                'subtitles_dir': self.subtitles_dir,
                'subtitles_default': int(self.subtitles_default),
                'subtitles_history': int(self.subtitles_history),
                'embedded_subtitles_all': int(self.embedded_subtitles_all),
                'subtitles_hearing_impaired': int(self.subtitles_hearing_impaired),
                'subtitles_finder_frequency': int(self.subtitle_searcher_freq),
                'subtitles_multi': int(self.subtitles_multi),
                'subtitles_extra_scripts': '|'.join(self.subtitles_extra_scripts),
                'addic7ed_username': self.addic7ed_user,
                'addic7ed_password': self.addic7ed_pass,
                'legendastv_username': self.legendastv_user,
                'legendastv_password': self.legendastv_pass,
                'itasa_username': self.itasa_user,
                'itasa_password': self.itasa_pass,
                'opensubtitles_username': self.opensubtitles_user,
                'opensubtitles_password': self.opensubtitles_pass,
            },
            'FailedDownloads': {
                'use_failed_downloads': int(self.use_failed_downloads),
                'delete_failed': int(self.delete_failed),
            },
            'ANIDB': {
                'use_anidb': int(self.use_anidb),
                'anidb_username': self.anidb_username,
                'anidb_password': self.anidb_password,
                'anidb_use_mylist': int(self.anidb_use_mylist),
            },
            'ANIME': {
                'anime_split_home': int(self.anime_split_home),
            },
            'Quality': {
                'sizes': pickle.dumps(self.quality_sizes),
            },
            'Providers': {
                'providers_order': sickrage.app.search_providers.provider_order,
                'custom_providers': self.custom_providers,
            },
            'MetadataProviders': {}
        })

        provider_keys = ['enabled', 'confirmed', 'ranked', 'engrelease', 'onlyspasearch', 'sorting', 'options', 'ratio',
                         'minseed', 'minleech', 'freeleech', 'search_mode', 'search_fallback', 'enable_daily', 'key',
                         'enable_backlog', 'cat', 'subtitle', 'api_key', 'hash', 'digest', 'username', 'password',
                         'passkey', 'pin', 'reject_m2ts', 'enable_cookies', 'cookies', 'custom_url']

        for providerID, providerObj in sickrage.app.search_providers.all().items():
            provider_settings = dict([(x, getattr(providerObj, x)) for x in provider_keys if hasattr(providerObj, x)])
            new_config['Providers'][providerID] = provider_settings

        for metadataProviderID, metadataProviderObj in sickrage.app.metadata_providers.items():
            new_config['MetadataProviders'][metadataProviderID] = metadataProviderObj.get_config()

        # encrypt settings
        new_config.walk(self.encrypt)
        new_config.write()

    def encrypt(self, section, key, _decrypt=False):
        """
        :rtype: basestring
        """

        if key in ['config_version', 'encryption_version', 'encryption_secret']:
            pass
        else:
            try:
                if self.encryption_version == 1:
                    unique_key1 = hex(uuid.getnode() ** 2)

                    if _decrypt:
                        section[key] = ''.join(
                            chr(ord(x) ^ ord(y)) for (x, y) in
                            izip(base64.decodestring(section[key]), cycle(unique_key1)))
                    else:
                        section[key] = base64.encodestring(
                            ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(section[key], cycle(unique_key1)))).strip()
                elif self.encryption_version == 2:
                    if _decrypt:
                        section[key] = ''.join(chr(ord(x) ^ ord(y)) for (x, y) in
                                               izip(base64.decodestring(section[key]),
                                                    cycle(sickrage.app.config.encryption_secret)))
                    else:
                        section[key] = base64.encodestring(
                            ''.join(chr(ord(x) ^ ord(y)) for (x, y) in izip(section[key], cycle(
                                sickrage.app.config.encryption_secret)))).strip()
            except:
                pass

    def decrypt(self, section, key):
        return self.encrypt(section, key, _decrypt=True)


class ConfigMigrator(Config):
    def __init__(self, config_obj):
        """
        Initializes a config migrator that can take the config from the version indicated in the config
        file up to the latest version
        """
        super(ConfigMigrator, self).__init__()
        self.config_obj = config_obj

        self.migration_names = {
            1: 'Sync backup number with version number',
            2: 'Sync backup number with version number',
            3: 'Sync backup number with version number',
            4: 'Sync backup number with version number',
            5: 'Sync backup number with version number',
            6: 'Sync backup number with version number',
            7: 'Sync backup number with version number',
            8: 'Use version 2 for password encryption',
            9: 'Rename slick gui template name to default',
            10: 'Add enabled attribute to metadata settings',
            11: 'Rename all metadata settings'
        }

    def migrate_config(self, current_version=0, expected_version=0):
        """
        Calls each successive migration until the config is the same version as SB expects
        """

        if current_version > expected_version:
            sickrage.app.log.error("Your config version (%i) has been incremented past what this version of supports "
                                   "(%i). If you have used other forks or a newer version of  your config file may be "
                                   "unusable due to their modifications." % (current_version,
                                                                             expected_version)
                                   )
            sys.exit(1)

        while current_version < expected_version:
            next_version = current_version + 1

            if next_version in self.migration_names:
                migration_name = ': ' + self.migration_names[next_version]
            else:
                migration_name = ''

            sickrage.app.log.info("Backing up config before upgrade")
            if not backupVersionedFile(sickrage.app.config_file, current_version):
                sickrage.app.log.exit("Config backup failed, abort upgrading config")
                sys.exit(1)
            else:
                sickrage.app.log.info("Proceeding with upgrade")

            # do the migration, expect a method named _migrate_v<num>
            sickrage.app.log.info("Migrating config up to version " + str(next_version) + migration_name)
            self.config_obj = getattr(self, '_migrate_v' + str(next_version))()
            current_version = next_version

            # update config version to newest
            self.config_obj['General']['config_version'] = current_version

        return self.config_obj

    # Migration v1: Dummy migration to sync backup number with config version number
    def _migrate_v1(self):
        return self.config_obj

    # Migration v2: Dummy migration to sync backup number with config version number
    def _migrate_v2(self):
        return self.config_obj

    # Migration v3: Dummy migration to sync backup number with config version number
    def _migrate_v3(self):
        return self.config_obj

    # Migration v4: Dummy migration to sync backup number with config version number
    def _migrate_v4(self):
        return self.config_obj

    # Migration v5: Dummy migration to sync backup number with config version number
    def _migrate_v5(self):
        return self.config_obj

    # Migration v6: Dummy migration to sync backup number with config version number
    def _migrate_v6(self):
        return self.config_obj

    # Migration v6: Dummy migration to sync backup number with config version number
    def _migrate_v7(self):
        return self.config_obj

    # Migration v8: Use version 2 for password encryption
    def _migrate_v8(self):
        self.config_obj['General']['encryption_version'] = 2
        return self.config_obj

    # Migration v9: Dummy migration to sync backup number with config version number
    def _migrate_v9(self):
        return self.config_obj

    # Migration v10: Metadata upgrade to add enabled attribute
    def _migrate_v10(self):
        """
        Updates metadata values to the new format
        Quick overview of what the upgrade does:

        new | old | description (new)
        ----+-----+--------------------
          1 |  1  | show metadata
          2 |  2  | episode metadata
          3 |  3  | show fanart
          4 |  4  | show poster
          5 |  5  | show banner
          6 |  6  | episode thumb
          7 |  7  | season poster
          8 |  8  | season banner
          9 |  9  | season all poster
         10 |  10 | season all banner
         11 |  -  | enabled

        Note that the ini places start at 1 while the list index starts at 0.
        old format: 0|0|0|0|0|0|0|0|0|0 -- 10 places
        new format: 0|0|0|0|0|0|0|0|0|0|0 -- 11 places
        """

        metadata_kodi = self.check_setting_str('General', 'metadata_kodi', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_kodi_12plus = self.check_setting_str('General', 'metadata_kodi_12plus', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_mediabrowser = self.check_setting_str('General', 'metadata_mediabrowser', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_ps3 = self.check_setting_str('General', 'metadata_ps3', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_wdtv = self.check_setting_str('General', 'metadata_wdtv', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_tivo = self.check_setting_str('General', 'metadata_tivo', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_mede8er = self.check_setting_str('General', 'metadata_mede8er', '0|0|0|0|0|0|0|0|0|0|0')

        def _migrate_metadata(metadata):
            cur_metadata = metadata.split('|')

            # if target has the old number of values, do upgrade
            if len(cur_metadata) == 10:
                # write new format
                cur_metadata.append('0')
                metadata = '|'.join(cur_metadata)
            elif len(cur_metadata) == 11:
                metadata = '|'.join(cur_metadata)
            else:
                metadata = '0|0|0|0|0|0|0|0|0|0|0'

            return metadata

        self.config_obj['General']['metadata_kodi'] = _migrate_metadata(metadata_kodi)
        self.config_obj['General']['metadata_kodi_12plus'] = _migrate_metadata(metadata_kodi_12plus)
        self.config_obj['General']['metadata_mediabrowser'] = _migrate_metadata(metadata_mediabrowser)
        self.config_obj['General']['metadata_ps3'] = _migrate_metadata(metadata_ps3)
        self.config_obj['General']['metadata_wdtv'] = _migrate_metadata(metadata_wdtv)
        self.config_obj['General']['metadata_tivo'] = _migrate_metadata(metadata_tivo)
        self.config_obj['General']['metadata_mede8er'] = _migrate_metadata(metadata_mede8er)

        return self.config_obj

    # Migration v11: Renames metadata setting keys
    def _migrate_v11(self):
        """
        Renames metadata setting keys
        """

        metadata_kodi = self.check_setting_str('General', 'metadata_kodi', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_kodi_12plus = self.check_setting_str('General', 'metadata_kodi_12plus', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_mediabrowser = self.check_setting_str('General', 'metadata_mediabrowser', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_ps3 = self.check_setting_str('General', 'metadata_ps3', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_wdtv = self.check_setting_str('General', 'metadata_wdtv', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_tivo = self.check_setting_str('General', 'metadata_tivo', '0|0|0|0|0|0|0|0|0|0|0')
        metadata_mede8er = self.check_setting_str('General', 'metadata_mede8er', '0|0|0|0|0|0|0|0|0|0|0')

        self.config_obj['MetadataProviders'] = {}
        self.config_obj['MetadataProviders']['kodi'] = metadata_kodi
        self.config_obj['MetadataProviders']['kodi_12plus'] = metadata_kodi_12plus
        self.config_obj['MetadataProviders']['mediabrowser'] = metadata_mediabrowser
        self.config_obj['MetadataProviders']['sony_ps3'] = metadata_ps3
        self.config_obj['MetadataProviders']['wdtv'] = metadata_wdtv
        self.config_obj['MetadataProviders']['tivo'] = metadata_tivo
        self.config_obj['MetadataProviders']['mede8er'] = metadata_mede8er

        return self.config_obj