# -*- coding: utf-8 -*-
import socket
import random
from bs4 import BeautifulSoup
from logging.handlers import RotatingFileHandler
import time
import logging
import mechanize
import os
import re
import sys
import json
import unicodedata
import pdb
from decimal import Decimal
from random import randint
from datetime import datetime, timedelta
from utils import *
from urllib import urlencode
from planet import Planet, Moon
from attack import Attack
from transport_manager import TransportManager
from config import options
from sim import Sim

socket.setdefaulttimeout(float(options['general']['timeout']))


class Bot(object):
    BASE_URL = 'https://', options['credentials']['server'], '.ogame.gameforge.com/'
    LOGIN_URL = 'https://', options['credentials']['server'], '.ogame.gameforge.com/main/login'
    HEADERS = [('User-agent',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')]
    RE_BUILD_REQUEST = re.compile(r"sendBuildRequest\(\'(.*)\',null,(1|0|false|true)\)")
    RE_SERVER_TIME = re.compile(r"var serverTime=new Date\((.*)\);var localTime")

    # ship -> ship id on the page
    SHIPS = {
        'lf': '204',
        'hf': '205',
        'cr': '206',
        'bs': '207',
        'bc': '215',
        'bo': '211',
        'de': '213',
        'ds': '214',
        'sc': '202',  # small c
        'lc': '203',  # large c
        'cs': '208',
        'rc': '209',
        'ep': '210'
    }

    # mission ids
    MISSIONS = {
        'attack': '1',
        'transport': '3',
        'station': '4',
        'expedition': '15',
        'collect': '8'
    }

    TARGETS = {
        'planet': '1',
        'moon': '3',
        'debris': '2'
    }

    SPEEDS = {
        100: '10',
        90: '9',
        80: '8',
        70: '7',
        60: '6',
        50: '5',
        40: '4',
        30: '3',
        20: '2',
        10: '1'
    }

    d = {
        'M': 6,
        'B': 9
    }

    def __init__(self, username=None, password=None, uni='69'):
        self.uni = uni
        self.username = username
        self.password = password
        self.logged_in = False

        self._prepare_logger()
        self._prepare_browser()
        farms = options['farming']['farms']
        self.farm_no = randint(0, len(farms) - 1) if farms else 0

        self.MAIN_URL = 'https://s%s-%s.ogame.gameforge.com/game/index.php' % (
        self.uni, options['credentials']['server'])
        self.PAGES = {
            'main': self.MAIN_URL + '?page=overview',
            'resources': self.MAIN_URL + '?page=resources',
            'station': self.MAIN_URL + '?page=station',
            'research': self.MAIN_URL + '?page=research',
            'shipyard': self.MAIN_URL + '?page=shipyard',
            'defense': self.MAIN_URL + '?page=defense',
            'fleet': self.MAIN_URL + '?page=fleet1',
            'galaxy': self.MAIN_URL + '?page=galaxy',
            'galaxyCnt': self.MAIN_URL + '?page=galaxyContent',
            'events': self.MAIN_URL + '?page=eventList',
            'resSettings': self.MAIN_URL + '?page=resourceSettings',
        }
        self.planets = []
        self.moons = []
        self.active_attacks = []

        self.fleet_slots = 0
        self.active_fleets = 0

        self.server_time = self.local_time = datetime.now()
        self.time_diff = 0
        self.emergency_sms_sent = False
        self.transport_manager = TransportManager()
        self.sim = Sim()

    def _get_url(self, page, planet=None):
        url = self.PAGES[page]
        if planet is not None:
            url += '&cp=%s' % planet.id
        return url

    def text_to_num(self, text):
        d = self.d
        if text[-1] in d:
            num, magnitude = text[:-1], text[-1]
            return Decimal(unicodedata.normalize('NFKD', num).encode('ascii', 'ignore').replace(',', '.')) * 10 ** d[
                magnitude]
        else:
            return Decimal(text.replace(',', '.').replace('Mn', '0000'))

    def _prepare_logger(self):
        self.logger = logging.getLogger("mechanize")
        fh = RotatingFileHandler('bot.log', maxBytes=100000, backupCount=5)
        sh = logging.StreamHandler()
        fmt = logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s',
                                datefmt='%m-%d, %H:%M:%S')
        fh.setFormatter(fmt)
        sh.setFormatter(fmt)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def _prepare_browser(self):
        self.br = mechanize.Browser()
        self.br.set_handle_equiv(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.addheaders = self.HEADERS

    def _parse_build_url(self, js):
        """
        convert: `sendBuildRequest('url', null, 1)`; into: `url`
        """
        # print js
        return self.RE_BUILD_REQUEST.findall(js)[0]

    def _parse_server_time(self, content):
        return self.RE_SERVER_TIME.findall(content)[0]

    def get_mother(self):
        for p in self.planets:
            if p.mother:
                return p
        return p[0] if self.planets else None

    def get_closest_planet(self, p):
        def min_dist(p, d):
            return d

        _, d, _ = p.split(":")
        return sorted([(planet, planet.get_distance(p)) for planet in self.planets],
                      key=lambda x: x[1])[0][0]

    def find_planet(self, name=None, coords=None, id=None, is_moon=None):
        if is_moon:
            planets = self.moons
        else:
            planets = self.planets
        for p in planets:
            if name == p.name or coords == p.coords or id == p.id:
                return p

    def get_safe_planet(self, planet):
        '''
        Get first planet which is not under attack and isn't `planet`
        '''
        unsafe_planets = [a.planet for a in self.active_attacks]
        for p in self.planets:
            if not p in unsafe_planets and p != planet:
                return p
        # no safe planets! go to mother
        return self.planets[0]

    def login(self, username=None, password=None):
        username = username or self.username
        password = password or self.password

        # pdb.set_trace()

        try:
            resp = self.br.open(self.MAIN_URL, timeout=10)
            soup = BeautifulSoup(resp, "html5lib")
        except:
            return False

        alert = soup.find(id='attack_alert')

        # no redirect on main page == user logged in
        if resp.geturl() != self.BASE_URL and alert:
            self.logged_in = True
            self.logger.info('Logged as: %s' % username)
            return True

        self.logger.info('Logging in..')
        self.br.select_form(name='loginForm')
        self.br.form['uni'] = ['s%s-%s.ogame.gameforge.com' % (self.uni, options['credentials']['server'])]
        self.br.form['login'] = username
        self.br.form['pass'] = password
        self.br.submit()

        if self.br.geturl().startswith(self.MAIN_URL):
            self.logged_in = True
            self.logger.info('Logged as: %s' % username)
            return True
        else:
            self.logged_in = False
            self.logger.error('Login failed!')
            return False

    def calc_time(self, resp):
        try:
            y, mo, d, h, mi, sec = map(int, self._parse_server_time(resp).split(','))
        except:
            self.logger.error('Exception while calculating time')
        else:
            self.local_time = n = datetime.now()
            self.server_time = datetime(n.year, n.month, n.day, h, mi, sec)
            self.time_diff = self.server_time - self.local_time

            self.logger.info('Server time: %s, local time: %s' % \
                             (self.server_time, self.local_time))

    def fetch_planets(self):
        self.logger.info('Fetching planets..')
        resp = self.br.open(self.PAGES['main']).read()

        self.calc_time(resp)

        soup = BeautifulSoup(resp, "html5lib")
        self.planets = []
        self.moons = []

        try:
            for i, c in enumerate(soup.findAll('a', 'planetlink')):
                name = c.find('span', 'planet-name').text
                coords = c.find('span', 'planet-koords').text[1:-1]
                url = c.get('href')
                p_id = int(c.parent.get('id').split('-')[1])
                construct_mode = len(c.parent.findAll('a', 'constructionIcon')) != 0
                p = Planet(p_id, name, coords, url, construct_mode)
                if i == 0:
                    p.mother = True
                self.planets.append(p)

                # check if planet has moon
                moon = c.parent.find('a', 'moonlink')
                if moon and 'moonlink' in moon['class']:
                    url = moon.get('href')
                    m_id = url.split('cp=')[1]
                    m = Moon(m_id, coords, url)
                    self.moons.append(m)
        except:
            self.logger.exception('Exception while fetching planets')
        else:
            self.check_attacks(soup)

    def handle_planets(self):
        self.fetch_planets()

        for p in iter(self.planets):
            self.update_planet_info(p)
            self.update_planet_fleet(p)
            self.update_planet_struct(p)
            self.update_planet_researches(p)
        for m in iter(self.moons):
            self.update_planet_info(m)
            self.update_planet_fleet(m)

    def update_planet_fleet(self, planet):
        resp = self.br.open(self._get_url('fleet', planet))
        soup = BeautifulSoup(resp, "html5lib")
        ships = {}
        for k, v in self.SHIPS.iteritems():
            available = 0
            try:
                s = soup.find(id='button' + v)
                available = int(s.find('span', 'textlabel').nextSibling.replace('.', ''))
            except:
                available = 0
            ships[k] = available

        # self.logger.info('Updating %s fleet' % planet)
        # self.logger.info('%s' % fleet)
        planet.ships = ships

    def update_planet_info(self, planet):
        if (int(options['building']['enabled']) != 1):
            return True
        in_construction_mode = False
        resp = self.br.open(self._get_url('resSettings', planet))
        soup = BeautifulSoup(resp, "html5lib")
        resSentence = u'Storage capacity'

        try:
            table = soup.find_all('table', {'class': 'listOfResourceSettingsPerPlanet'})
            for tag in table:
                trTags = tag.find_all("tr", {"class": ""})
                for t in trTags:
                    td = t.find_all('td')
                    if len(td) > 0 and td[0].text == resSentence:
                        planet.resources['maxMetal'] = td[1].text.replace(' ', '').replace('\n', '').replace('.', '').replace("Mn", "0000")
                        planet.resources['maxCrystal'] = td[2].text.replace(' ', '').replace('\n', '').replace('.', '').replace("Mn", "0000")
                        planet.resources['maxDeuterium'] = td[3].text.replace(' ', '').replace('\n', '').replace('.', '').replace("Mn", "0000")
                        break
        except:
            self.logger.exception('Exception while updating resources info (capacity)')

        resp = self.br.open(self._get_url('resources', planet))
        soup = BeautifulSoup(resp, "html5lib")

        try:
            metal = int(soup.find(id='resources_metal').text.replace('.', ''))
            planet.resources['metal'] = metal
            crystal = int(soup.find(id='resources_crystal').text.replace('.', ''))
            planet.resources['crystal'] = crystal
            deuterium = int(soup.find(id='resources_deuterium').text.replace('.', ''))
            planet.resources['deuterium'] = deuterium
            energy = int(soup.find(id='resources_energy').text.replace('.', ''))
            planet.resources['energy'] = energy
        except:
            self.logger.exception('Exception while updating resources info (resources)')
        else:
            # self.logger.info('Updating resources info for %s:' % planet)
            s = planet.name + ': metal - %(metal)s (%(maxMetal)s), crystal - %(crystal)s (%(maxCrystal)s), deuterium - %(deuterium)s (%(maxDeuterium)s)'
            self.logger.info(s % planet.resources)
        if planet.is_moon():
            return
        maxReached = [int(planet.resources['metal']) >= self.text_to_num(planet.resources['maxMetal']),
                      int(planet.resources['crystal']) >= self.text_to_num(planet.resources['maxCrystal']),
                      int(planet.resources['deuterium']) >= self.text_to_num(planet.resources['maxDeuterium'])]
        next = ''
        if maxReached[0]:
            next = 'metalDeposit'
        elif maxReached[1]:
            next = 'crystalDeposit'
        elif maxReached[2]:
            next = 'deuteriumDeposit'
        try:
            if (next == ''):
                buildingList = soup.find(id='building')
                buildings = ('metalMine', 'crystalMine', 'deuteriumMine', 'solarPlant',
                             'fusionPlant', 'solarSatellite'
                             )
                for building, b in zip(buildings, buildingList.findAll('li')):
                    can_build = 'on' in b.get('class')
                    fb = b.find('a', 'fastBuild')
                    build_url = fb.get('onclick') if fb else ''
                    if build_url:
                        build_url = self._parse_build_url(build_url.replace(' ', ''))
                    try:
                        t = b.find('span', 'textlabel').nextSibling.replace('.', '')
                        level = int(t)
                    except AttributeError:
                        try:
                            level = int(b.find('span', 'level').text)
                        except:
                            pass
                    suff_energy = planet.resources['energy'] - self.sim.upgrade_energy_cost(building, level + 1) > 0

                    res = dict(
                        level=level,
                        can_build=can_build,
                        build_url=build_url,
                        sufficient_energy=suff_energy
                    )

                    planet.buildings[building] = res
            else:
                buildingList = soup.find(id='storage')
                buildings = ('metalDeposit', 'crystalDeposit', 'deuteriumDeposit')
                for building, b in zip(buildings, buildingList.findAll('li')):
                    can_build = 'on' in b.get('class')
                    fb = b.find('a', 'fastBuild')
                    build_url = fb.get('onclick') if fb else ''
                    if build_url:
                        build_url = self._parse_build_url(build_url.replace(' ', ''))
                    try:
                        level = int(b.find('span', 'textlabel').nextSibling)
                    except AttributeError:
                        try:
                            level = int(b.find('span', 'level').text)
                        except:
                            pass

                    res = dict(
                        level=level,
                        can_build=can_build,
                        build_url=build_url,
                        sufficient_energy=True
                    )

                    planet.deposits[building] = res

            if buildingList.find('div', 'construction'):
                in_construction_mode = True
        except:
            self.logger.exception('Exception while updating buildings info')
            return False
        else:
            # self.logger.info('%s buildings were updated' % planet)
            pass

        if not in_construction_mode and next != '':
            text, url = planet.get_deposit_url(next)
            if url:
                self.logger.info('Building upgrade on %s: \033[92m%s\033[0m' % (planet, text))
                self.br.open(url[0])
                planet.in_construction_mode = True
                # let now transport manager to clear building queue
                self.transport_manager.update_building(planet)
        elif not in_construction_mode and next == '':
            text, url = planet.get_mine_to_upgrade()
            if url:
                self.logger.info('Building upgrade on %s: \033[92m%s\033[0m' % (planet, text))
                self.br.open(url[0])
                planet.in_construction_mode = True
                # let now transport manager to clear building queue
                self.transport_manager.update_building(planet)
        else:
            self.logger.info('Building queue is not empty')
        return True

    def update_planet_struct(self, planet):
        if (int(options['station']['enabled']) != 1):
            return True
        self.logger.info('Checking structures update')
        in_construction_mode = False
        resp = self.br.open(self._get_url('station', planet))
        soup = BeautifulSoup(resp, "html5lib")
        try:
            stationList = soup.find(id='stationbuilding')
            structures = ('roboticsFactory', 'shipyard', 'naniteFactory', 'terraformer', 'spaceDock')
            for station, b in zip(structures, stationList.findAll('li')):
                can_build = 'on' in b.get('class')
                fb = b.find('a', 'fastBuild')
                stat_url = fb.get('onclick') if fb else ''
                if stat_url:
                    stat_url = self._parse_build_url(stat_url.replace('\n', '').replace(' ', ''))
                try:
                    level = int(b.find('span', 'textlabel').nextSibling)
                except AttributeError:
                    try:
                        level = int(b.find('span', 'level').text)
                    except:
                        pass
                res = dict(
                    level=level,
                    can_build=can_build,
                    build_url=stat_url,
                    enabled=planet.stations[station]['enabled'],
                    sufficient_energy=True
                )

                planet.stations[station] = res

            if stationList.find('div', 'construction'):
                in_construction_mode = True
        except:
            self.logger.exception('Exception while updating stations info')
            return False
        else:
            self.logger.info('%s stations were updated' % planet)

        if not in_construction_mode:
            text, url = planet.get_station_url()
            if url:
                self.logger.info('Stations upgrade on %s: \033[94m%s\033[0m' % (planet, text))
                self.br.open(url[0])
                planet.in_construction_mode = True
                # let now transport manager to clear building queue
                self.transport_manager.update_building(planet)
        else:
            self.logger.info('Building queue is not empty')
        return True

    def update_planet_researches(self, planet):
        if int(options['research']['enabled']) != 1:
            return True
        self.logger.info('Checking researches update')
        in_research_mode = False
        resp = self.br.open(self._get_url('research', planet))
        soup = BeautifulSoup(resp, "html5lib")
        try:
            researchList = soup.find(id='buttonz')
            resTemp = researchList.findChildren(id='wrapBattle')
            researches = (
            ('energyTech', 'laserTech', 'ionTech', 'hyperspaceTech', 'plasmaTech'), ('combustionDrive', 'impulseDrive',
                                                                                     'hyperspaceDrive'),
            ('espionageTech', 'computerTech', 'astrophysics', 'intergalacticRes',
             'gravitonTech'), ('weaponTech', 'shieldingTech', 'armourTech'))

            for category, resCategory in zip(researches, resTemp):
                for research, b in zip(category, resCategory.findAll('li')):
                    can_build = 'on' in b.get('class')
                    fb = b.find('a', 'fastBuild')
                    res_url = fb.get('onclick') if fb else ''
                    if res_url:
                        res_url = self._parse_build_url(res_url.replace('\n', '').replace(' ', ''))
                    try:
                        level = int(b.find('span', 'textlabel').nextSibling)
                    except AttributeError:
                        try:
                            level = int(b.find('span', 'level').text)
                        except:
                            pass
                    res = dict(
                        level=level,
                        can_build=can_build,
                        build_url=res_url,
                        enabled=planet.researches[research]['enabled'],
                        sufficient_energy=True
                    )

                    planet.researches[research] = res

            if researchList.find('div', 'construction'):
                in_research_mode = True
        except:
            self.logger.exception('Exception while updating stations info')
            return False
        else:
            self.logger.info('%s researches were updated' % planet)

        if not in_research_mode:
            text, url = planet.get_research_url()
            if url:
                self.logger.info('Research upgrade on %s: \033[95m%s\033[0m' % (planet, text))
                self.br.open(url[0])
        else:
            self.logger.info('Research queue is not empty')
        return True

    def transport_resources(self):
        tasks = self.transport_manager.find_dest_planet(self.planets)
        if tasks is None:
            return False
        self.logger.info(self.transport_manager.get_summary())
        for task in iter(tasks):
            self.logger.info('Transport attempt from: %s, to: %s with resources %s' \
                             % (task['from'], task['where'], task['resources']))
            result = self.send_fleet(
                task['from'],
                task['where'].coords,
                fleet=task['from'].get_fleet_for_resources(task['resources']),
                resources=task['resources'],
                mission='transport'
            )
            if result:
                self.transport_manager.update_sent_resources(task['resources'])
                self.logger.info('Resources sent: %s, resources needed: %s' \
                                 % (task['resources'], self.transport_manager.get_resources_needed()))

        return True

    def build_defense(self, planet):
        """
        Build defense for all resources on the planet
        1. plasma
        2. gauss
        3. heavy cannon
        4. light cannon
        5. rocket launcher
        """
        url = self._get_url('defense', planet)
        resp = self.br.open(url)
        for t in ('406', '404', '403', '402', '401'):
            self.br.select_form(name='form')
            self.br.form.new_control('text', 'menge', {'value': '100'})
            self.br.form.fixup()
            self.br['menge'] = '100'

            self.br.form.new_control('text', 'type', {'value': t})
            self.br.form.fixup()
            self.br['type'] = t

            self.br.form.new_control('text', 'modus', {'value': '1'})
            self.br.form.fixup()
            self.br['modus'] = '1'

            self.br.submit()

    def get_player_status(self, destination, origin_planet=None):
        if not destination:
            return

        status = {}
        origin_planet = origin_planet or self.get_closest_planet(destination)
        galaxy, system, position = destination.split(':')

        url = self._get_url('galaxyCnt', origin_planet)
        data = urlencode({'galaxy': galaxy, 'system': system})
        resp = self.br.open(url, data=data)

        j = json.loads(resp.read())

        s = '<html><body>' + j['galaxy'] + '</body></html>'
        soup = BeautifulSoup(s, "html5lib")
        planets = soup.find_all('tr', {'class': 'row'})
        target_planet = planets[int(position) - 1]
        name_el = target_planet.find('td', 'playername')
        status['name'] = name_el.find('span').text
        status['inactive'] = 'inactive' in name_el.get('class', '') or 'longinactive' in name_el.get('class', '')

        return status

    def find_inactive_nearby(self, planet, radius=15):

        self.logger.info("Searching idlers near %s in radius %s"
                         % (planet, radius))

        nearby_systems = planet.get_nearby_systems(radius)
        idlers = []

        for system in nearby_systems:
            galaxy, system = system.split(":")
            url = self._get_url('galaxyCnt', planet)
            data = urlencode({'galaxy': galaxy, 'system': system})
            resp = self.br.open(url, data=data)
            soup = BeautifulSoup(resp, "html5lib")

            galaxy_el = soup.find(id="galaxytable")
            soup.find("table", id='galaxytable')
            planets = galaxy_el.findAll('tr', {'class': 'row'})
            for pl in planets:
                name_el = pl.find('td', 'playername')
                debris_el = pl.find('td', 'debris')
                inactive = 'inactive' in name_el.get('class', '')
                debris_not_found = 'js_no_action' in debris_el.get('class', '')
                if not inactive or not debris_not_found:
                    continue
                position = pl.find('td', 'position').text
                coords = "%s:%s:%s" % (galaxy, system, position)
                player_id = name_el.find('a').get('rel')

                player_info = soup.find(id=player_id)
                rank_el = player_info.find('li', 'rank')

                if not rank_el:
                    continue

                rank = int(rank_el.find('a').text)
                if rank > 4000 or rank < 900:
                    continue

                idlers.append(coords)
                time.sleep(2)

        return idlers

    def find_inactives(self):

        inactives = []
        for p in self.planets:
            try:
                idlers = self.find_inactive_nearby(p)
                self.logger.info(" ".join(idlers))
                inactives.extend(idlers)
            except Exception as e:
                self.logger.exception(e)
                continue
            time.sleep(5)

        self.logger.info(" ".join(inactives))
        self.inactives = list(set(inactives))
        self.logger.info(inactives)

    def send_fleet(self, origin_planet, destination, fleet={}, resources={},
                   mission='attack', target='planet', speed=None):
        if origin_planet.coords == destination:
            self.logger.error('Cannot send fleet to the same planet')
            return False
        self.logger.info('Sending fleet from \033[0;36m%s\033[0m to \033[0;36m%s\033[0m (%s)' \
                         % (origin_planet, destination, mission))
        resp = self.br.open(self._get_url('fleet', origin_planet))
        try:
            try:
                self.br.select_form(name='shipsChosen')
            except mechanize.FormNotFoundError:
                self.logger.info('No available ships on the planet')
                return False

            soup = BeautifulSoup(resp, "html5lib")
            for ship, num in fleet.iteritems():
                s = soup.find(id='button' + self.SHIPS[ship])
                num = int(num)
                try:
                    available = int(s.find('span', 'textlabel').nextSibling.replace('.', ''))
                except:
                    available = 0
                if available < num and mission in ('attack', 'expedition'):
                    self.logger.info('No available ships to send')
                    return False
                if num > 0:
                    self.br.form['am' + self.SHIPS[ship]] = str(num)

            self.br.submit()

            try:
                self.br.select_form(name='details')
            except mechanize.FormNotFoundError:
                self.logger.info('No available ships on the planet')
                return False

            galaxy, system, position = destination.split(':')
            self.br['galaxy'] = galaxy
            self.br['system'] = system
            self.br['position'] = position
            self.br.form.find_control("type").readonly = False
            self.br['type'] = self.TARGETS[target]
            self.br.form.find_control("speed").readonly = False
            if speed:
                self.br['speed'] = self.SPEEDS[speed]
            self.br.submit()

            self.br.select_form(name='sendForm')
            self.br.form.find_control("mission").readonly = False
            self.br.form['mission'] = self.MISSIONS[mission]
            if 'metal' in resources:
                self.br.form['metal'] = str(resources['metal'])
            if 'crystal' in resources:
                self.br.form['crystal'] = str(resources['crystal'])
            if 'deuterium' in resources:
                self.br.form['deuterium'] = str(resources['deuterium'])
            self.br.submit()
        except Exception as e:
            self.logger.exception(e)
            return False
        else:
            if mission == 'attack':
                self.farm_no += 1
        return True

    def send_message(self, url, player, subject, message):
        self.logger.info('Sending message to %s: %s' % (player, message))
        self.br.open(url)
        self.br.select_form(nr=0)
        self.br.form['betreff'] = subject
        self.br.form['text'] = message
        self.br.submit()

    def send_sms(self, msg):
        from smsapigateway import SMSAPIGateway
        try:
            SMSAPIGateway().send(msg)
        except Exception as e:
            self.logger.exception(str(e))

    def handle_attacks(self):
        attack_opts = options['attack']
        send_sms = bool(options['sms']['send_sms'])

        for a in self.active_attacks:
            if a.is_dangerous():
                self.logger.info('Handling attack: %s' % a)
                if not a.planet.is_moon():
                    self.build_defense(a.planet)
                if send_sms and not a.sms_sent:
                    self.send_sms(a.get_sms_text())
                    a.sms_sent = True
                if send_sms and not a.message_sent:
                    self.send_message(a.message_url, a.player, attack_opts['message_topic'],
                                      a.get_random_message())
                    a.message_sent = True
                self.fleet_save(a.planet)

    def check_attacks(self, soup):
        alert = soup.find(id='attack_alert')
        if not alert:
            self.logger.exception('Check attack failed')
            return
        if 'noAttack' in alert.get('class', ''):
            self.logger.info('No attacks')
            self.active_attacks = []
        else:
            self.logger.info('ATTACK!')
            resp = self.br.open(self.PAGES['events'])
            soup = BeautifulSoup(resp, "html5lib")
            hostile = False
            try:
                for tr in soup.findAll('tr'):
                    countDown = tr.find('td', 'countDown')
                    if countDown and 'hostile' in countDown.get('class', ''):
                        hostile = True
                        # First: check if attack was noticed
                        if tr.get('id'):
                            attack_id = tr.get('id').split('-')[1]
                        elif countDown.get('id'):
                            attack_id = countDown.get('id').split('-')[2]
                        if not attack_id or attack_id in [a.id for a in self.active_attacks]:
                            continue
                        try:
                            # Attack first discovered: save attack info
                            arrivalTime = tr.find('td', 'arrivalTime').text.split(' ')[0]
                            coordsOrigin = tr.find('td', 'coordsOrigin')
                            if coordsOrigin:
                                if coordsOrigin.find('a'):
                                    coordsOrigin = coordsOrigin.find('a').text.strip()[1:-1]
                            destCoords = tr.find('td', 'destCoords')
                            if destCoords:
                                destCoords = destCoords.find('a').text.strip()[1:-1]
                            originFleet = tr.find('td', 'originFleet')
                            detailsFleet = int(tr.find('td', 'detailsFleet').span.text.replace('.', ''))
                            player_info = originFleet.find('a')
                            message_url = player_info.get('href')
                            player = player_info.get('data-player-name')
                            is_moon = False  # TODO!
                            planet = self.find_planet(coords=destCoords, is_moon=is_moon)
                            a = Attack(planet, attack_id, arrivalTime, coordsOrigin,
                                       destCoords, detailsFleet, player, message_url)

                            self.active_attacks.append(a)
                        except Exception as e:
                            self.logger.exception(e)
                            self.send_sms('ATTACKEROR')
                if not hostile:
                    self.active_attacks = []
            except Exception as e:
                self.logger.exception(e)

    def fleet_save(self, p):
        if not p.has_ships():
            return
        fleet = p.ships
        # recyclers are staying!
        # fleet['rc'] = 0
        self.logger.info('Making fleet save from %s' % p)
        self.send_fleet(p,
                        self.get_safe_planet(p).coords,
                        fleet=fleet,
                        mission='station',
                        speed=10,
                        resources={'metal': p.resources['metal'] + 500,
                                   'crystal': p.resources['crystal'] + 500,
                                   'deuterium': p.resources['deuterium'] + 500})

    def collect_debris(self, p):
        if not p.has_ships():
            return
        self.logger.info('Collecting debris from %s using %s recyclers' % (p, p.ships['rc']))
        self.send_fleet(p,
                        p.coords,
                        fleet={'rc': p.ships['rc']},
                        mission='collect',
                        target='debris')

    def send_expedition(self):
        expedition = options['expedition']
        planets = expedition['planets'].split(' ')
        ships_kind = expedition['ships_kind'].split(' ')
        ships_number = expedition['ships_number'].split(' ')
        fleets = dict(zip(ships_kind, ships_number))

        random.shuffle(planets)
        for coords in planets[:3]:
            planet = self.find_planet(coords=coords)
            if planet:
                galaxy, system, position = planet.coords.split(':')
                expedition_coords = '%s:%s:16' % (galaxy, system)
                self.send_fleet(planet, expedition_coords,
                                fleet=fleets,
                                mission='expedition')

    def farm(self):
        farms = options['farming']['farms'].split(' ')
        ships_kind = options['farming']['ships_kind'].split(' ')
        ships_number = options['farming']['ships_number'].split(' ')
        fleets = dict(zip(ships_kind, ships_number))
        l = len(farms)
        if l == 0 or not farms[0]:
            return
        farm = farms[self.farm_no % l]

        if not self.get_player_status(farm)['inactive']:
            self.farm_no += 1
            self.logger.error('\033[93mfarm %s seems not to be inactive!\033[0m', farm)
            return
        self.send_fleet(
            self.planets[0],  # self.get_closest_planet(farm) quick fix
            farm,
            fleet=fleets
        )

    def sleep(self):
        sleep_options = options['general']
        sleep_time = randint(0, int(sleep_options['seed'])) + int(sleep_options['check_interval'])
        self.logger.info('Sleeping for %s secs' % sleep_time)
        if self.active_attacks:
            sleep_time = 60
        time.sleep(sleep_time)

    def stop(self):
        self.logger.info('Stopping bot')
        os.unlink(self.pidfile)

    def start(self):
        self.logger.info('Starting bot')
        self.pid = str(os.getpid())
        self.pidfile = 'bot.pid'
        file(self.pidfile, 'w').write(self.pid)

        # main loop
        while True:
            if self.login():
                try:
                    self.handle_planets()
                    # self.find_inactives() # currently not working
                    if not self.active_attacks:
                        # self.transport_resources()
                        if True or not self.transport_resources():
                            self.send_expedition()
                            self.farm()
                    else:
                        self.handle_attacks()

                except Exception as e:
                    self.logger.exception(e)
                    # self.stop()
                    # return
            else:
                self.logger.error('Login failed!')
                # self.stop()
                # return
            self.sleep()


if __name__ == "__main__":
    credentials = options['credentials']
    bot = Bot(credentials['username'], credentials['password'], credentials['uni'])
    bot.start()
