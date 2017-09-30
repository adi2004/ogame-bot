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
	#self.in_research_mode = in_research_mode
        self.mines = (
            'metalMine',
            'crystalMine',
            'deuteriumMine'
        )
	self.deposits = (
	   'metalDeposit'
	   'crystalDeposit'
	   'deuteriumDeposit'
	)
        self.resources = {
            'metal': 0,
            'crystal': 0,
            'deuterium':0,
            'energy':0
        }
        
        self.buildings = {
            'metalMine': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': False
            },
            'crystalMine': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': False
            },
            'deuteriumMine': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': False
            },
            'solarPlant': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },
            'fusionPlant': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },
            'solarSatellite': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            }
	}
	self.deposits = {
	    'metalDeposit': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },
            'crystalDeposit': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },
            'deuteriumDeposit': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            }
	}
	self.stations = {
	    'roboticsFactory': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },

	    'shipyard': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },

            'researchLab': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },
		
            'naniteFactory': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
		'enabled': True,
                'sufficient_energy': True
            },

            'allianceDepot': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'missileSilo': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'terraformer': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            },

            'spaceDock': {
                'level': 0,
                'buildUrl':'',
                'can_build': False,
                'enabled': False,
                'sufficient_energy': True
            }
        }
	self.researches = {
		'energyTech': {
                	'level': 0,
                	'buildUrl':'',
                	'can_build': False,
                	'enabled': True,
                	'sufficient_energy': True
            	},
                'laserTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'ionTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'hyperspaceTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'plasmaTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'combustionDrive': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'impulseDrive': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'hyperspaceDrive': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'espionageTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'computerTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'astrophysics': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'intergalacticRes': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'gravitonTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'weaponTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'shieldingTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
                'armourTech': {
                        'level': 0,
                        'buildUrl':'',
                        'can_build': False,
                        'enabled': True,
                        'sufficient_energy': True
                },
	}

        self.ships = {
            'lm': 0,
            'hm': 0,
            'cr': 0,
            'ow': 0,
            'pn': 0,
            'bb': 0,
            'ns': 0,
            'gs': 0,
            'lt': 0,
            'dt': 0,
            'cs': 0,
            'rc': 0,
            'ss': 0
        }
        
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.id == other.id
    
    
    def get_deposit_url(self,deposit):
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
	maxlv = max(b, key=lambda k:b[k]['level'] if b[k]['enabled'] else None)
	minlv = min(b, key=lambda k:b[k]['level'] if b[k]['enabled'] and b[k]['can_build'] else None)
	
	if(b[priority]['level'] == b[maxlv]['level'] and b[priority]['level'] == b[minlv]['level'] and b[priority]['can_build']):
		#print "1"
		return priority, b[priority]['build_url']
	elif(b[priority]['level'] == b[minlv]['level'] and b[priority]['can_build']):
		#print "2"
		return priority, b[priority]['build_url']
	elif(b[priority]['level'] == b[maxlv]['level']):
		if(b[priority]['level']-b[minlv]['level'] >= levels_diff and b[minlv]['enabled'] and b[minlv]['can_build']):
			#print "3"
			return minlv, b[minlv]['build_url']
	elif(b[priority]['can_build']):
			#print "4"
			return priority, b[priority]['build_url']
	return None,None
    
    def get_research_url(self):
        b = self.researches
        #minlv = min(b, key=lambda k:b[k]['level'] if b[k]['enabled'] and b[k]['can_build'] else None)
	minlv = float('inf')
	min = ''
	for elem, details in b.iteritems():
		if(details['can_build'] and details['enabled'] and details['level']<minlv):
			minlv = details['level']
			min = elem
	
	if(min):
		return min, b[min]['build_url']
        return None,None	

    def get_mine_to_upgrade(self):
        build_options = options['building']
        min_energy_level = int(build_options['min_energy_level'])
        levels_diff = map(int, build_options['levels_diff'].split(','))
        max_fusion_lvl = int(build_options['max_fusion_plant_level'])

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
        if proposed_levels == mine_levels or (mine_levels[1] >= proposed_levels[1] and mine_levels[2] >= proposed_levels[2]):
            proposed_levels[0] += 1

        num_suff_energy = 0
        for i in xrange(3):
            building = self.mines[i]
            if b[building]['sufficient_energy']:
                num_suff_energy += 1
            if b[building]['can_build'] and proposed_levels[i] > b[building]['level']:
                if b[building]['sufficient_energy']:
                    return building, b[building]['build_url']
                else:
                    build_power_plant = True

        if build_power_plant or num_suff_energy == 0:
            if b['solarPlant']['can_build']:
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
        ships = {'dt': 0, 'lt': 0}
        for kind in ('dt', 'lt'):
            if self.ships[kind] > 0:
                for i in xrange(self.ships[kind]):
                    to_send += (25000 if kind == 'dt' else 5000)
                    ships[kind] += 1
                    if to_send > total:
                        return ships
        return ships
    
    def get_nearby_systems(self, radius):
        g, s, p = map(int, self.coords.split(":"))
        start_system = max(1, s-radius)
        end_system = min(499, s+radius)
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
