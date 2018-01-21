# -*- coding: utf-8 -*-
from config import options
import operator


class Planet(object):
    def __init__(self, id, name, coords, url, in_construction_mode=False, in_research_mode=False):
        self.id = id
        self.name = name
        self.url = url
        self.coords = coords
        self.mother = False
        self.galaxy, self.system, self.position = map(int, self.coords.split(":"))
        self.in_construction_mode = in_construction_mode
        # self.in_research_mode = in_research_mode
        self.mines = (
            'metalMine',
            'crystalMine',
            'deuteriumMine'
        )
        self.resources = {
            'metal': 0,
            'crystal': 0,
            'deuterium': 0,
            'energy': 0
        }

        self.buildings = {
            'metalMine': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': False
            },
            'crystalMine': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': False
            },
            'deuteriumMine': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': False
            },
            'solarPlant': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'fusionPlant': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'solarSatellite': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            }
        }
        self.deposits = {
            'metalDeposit': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'crystalDeposit': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'deuteriumDeposit': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            }
        }
        self.stations = {
            'roboticsFactory': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },

            'shipyard': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },

            'researchLab': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },

            'naniteFactory': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },

            'allianceDepot': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'missileSilo': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'terraformer': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'spaceDock': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            }
        }
        self.researches = {
            'energyTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'laserTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'ionTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'hyperspaceTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'plasmaTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'combustionDrive': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'impulseDrive': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'hyperspaceDrive': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'espionageTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'computerTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'astrophysics': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'intergalacticRes': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'gravitonTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'weaponTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'shieldingTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
            'armourTech': {
                'level': 0,
                'buildUrl': '',
                'can_build': False,
                'enabled': True,
                'sufficient_energy': True
            },
        }

        self.ships = {
            'lf': 0,
            'hf': 0,
            'cr': 0,
            'bs': 0,
            'bc': 0,
            'bo': 0,
            'de': 0,
            'ds': 0,
            'sc': 0,  # small c
            'lc': 0,  # large c
            'cs': 0,
            'rc': 0,
            'ep': 0
        }

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id

    def get_deposit_url(self, deposit):
        build_options = options['building']
        levels_diff = map(int, build_options['levels_diff'].split(','))

        b = self.deposits

        if b[deposit]['can_build']:
            return deposit, b[deposit]['build_url']
        else:
            return None, None

    def get_station_url(self):
        station_options = options['station']
        levels_diff = int(station_options['levels_diff'])
        priority = station_options['priority']
        b = self.stations
        # maxlv = max(b, key=lambda k:b[k]['level'] if b[k]['enabled'] else None)
        # minlv = min(b, key=lambda k:b[k]['level'] if b[k]['enabled'] and b[k]['can_build'] else None)

        minlv = float('inf')
        min = ''
        for elem, value in b.iteritems():
            if (value['can_build'] and value['enabled'] and value['level'] < minlv):
                minlv = elem
                min = value['level']

        maxlv = float('-inf')
        max = ''
        for elem, value in b.iteritems():
            if (value['can_build'] and value['enabled'] and value['level'] > maxlv):
                maxlv = elem
                max = value['level']

        if (maxlv == float('-inf') or minlv == float('inf')):
            return None, None
        # ritorna shipyard, rivedere codice
        if (b[priority]['level'] == b[maxlv]['level'] and b[priority]['level'] == b[minlv]['level'] and b[priority][
            'can_build']):
            return priority, b[priority]['build_url']
        elif (b[priority]['level'] == b[minlv]['level'] and b[priority]['can_build']):
            return priority, b[priority]['build_url']
        elif (b[priority]['level'] == b[maxlv]['level']):
            if (b[priority]['level'] - b[minlv]['level'] >= levels_diff):
                return minlv, b[minlv]['build_url']
        elif (not (b[priority]['can_build']) and b[minlv]['level'] < b[priority]['level']):
            return minlv, b[minlv]['build_url']
        elif (b[priority]['can_build']):
            return priority, b[priority]['build_url']
        return None, None

    def get_research_url(self):
        b = self.researches
        high_prior = options['research']['high_prior'].split(' ')
        medium_prior = options['research']['medium_prior'].split(' ')
        low_prior = options['research']['low_prior'].split(' ')
        minlv = float('inf')
        min = ''
        for elem in high_prior:
            if (b[elem]['can_build'] and b[elem]['enabled'] and b[elem]['level'] < minlv):
                minlv = b[elem]['level']
                min = elem

        if (min):
            return min, b[min]['build_url']

        minlv = float('inf')
        min = ''
        for elem in medium_prior:
            if (b[elem]['can_build'] and b[elem]['enabled'] and b[elem]['level'] < minlv):
                minlv = b[elem]['level']
                min = elem

        if (min):
            return min, b[min]['build_url']

        minlv = float('inf')
        min = ''
        for elem in low_prior:
            if (b[elem]['can_build'] and b[elem]['enabled'] and b[elem]['level'] < minlv):
                minlv = b[elem]['level']
                min = elem

        if (min):
            return min, b[min]['build_url']

        return None, None

    def get_mine_to_upgrade(self):
        build_options = options['building']
        levels_diff = map(int, build_options['levels_diff'].split(','))
        max_fusion_lvl = int(build_options['max_fusion_plant_level'])
        max_solar_lvl = int(build_options['max_solar_plant_level'])

        b = self.buildings
        build_power_plant = self.resources['energy'] <= 0

        mine_levels = [0, 0, 0]

        for i, mine in enumerate(self.mines):
            mine_levels[i] = b[mine]['level']

        proposed_levels = [
            b['metalMine']['level'],
            b['metalMine']['level'] - levels_diff[0],
            b['metalMine']['level'] - levels_diff[0] - levels_diff[1]
        ]
        proposed_levels = [0 if l < 0 else l for l in proposed_levels]
        if proposed_levels == mine_levels or (
                mine_levels[1] >= proposed_levels[1] and mine_levels[2] >= proposed_levels[2]):
            proposed_levels[0] += 1

        num_suff_energy = 0
        for i in xrange(3):
            building = self.mines[i]
            if b[building]['sufficient_energy']:
                num_suff_energy += 1
            if b[building]['can_build'] and proposed_levels[i] > b[building]['level']:
                if b[building]['sufficient_energy'] or \
                    b['solarPlant']['level'] >= max_solar_lvl:
                    return building, b[building]['build_url']
                else:
                    build_power_plant = True

        if build_power_plant or num_suff_energy == 0:
            if b['solarPlant']['can_build'] and \
                    b['solarPlant']['level'] < max_solar_lvl:
                return u'Solar plant', b['solarPlant']['build_url']
            elif b['fusionPlant']['can_build'] and \
                    b['fusionPlant']['level'] < max_fusion_lvl:
                return u'Fusion plant', b['fusionPlant']['build_url']
            else:
                return None, None
        else:
            return None, None

    def is_moon(self):
        return False

    def has_ships(self):
        '''
        Return true if any ship is stationing on the planet
        '''
        return any(self.ships.values())

    def get_distance(self, planet):
        """
        Return distance to planet `planet`
        """
        try:
            g, s, p = map(int, planet.split(":"))
        except Exception:
            return 100000
        d = 0
        d += (abs(g - self.galaxy) * 100)
        d += (abs(s - self.system) * 10)
        d += (abs(p - self.position))

        return d

    def get_fleet_for_resources(self, r):
        total = sum([r.get('metal', 0), r.get('crystal', 0), r.get('deuterium', 0)])
        to_send = 0
        ships = {'lc': 0, 'sc': 0}
        for kind in ('lc', 'sc'):
            if self.ships[kind] > 0:
                for i in xrange(self.ships[kind]):
                    to_send += (25000 if kind == 'lc' else 5000)
                    ships[kind] += 1
                    if to_send > total:
                        return ships
        return ships

    def get_nearby_systems(self, radius):
        g, s, p = map(int, self.coords.split(":"))
        start_system = max(1, s - radius)
        end_system = min(499, s + radius)
        systems = []
        for system in xrange(start_system, end_system):
            systems.append("%s:%s" % (g, system))

        return systems


class Moon(Planet):

    def __init__(self, id, coords, url):
        super(Moon, self).__init__(id, 'Moon', coords, url)

    def get_mine_to_upgrade(self):
        return None, None

    def is_moon(self):
        return True

    def __str__(self):
        return '[%s] %s' % (self.coords, self.name)
