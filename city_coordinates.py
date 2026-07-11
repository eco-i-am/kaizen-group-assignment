"""
Static city coordinates lookup for USA and Canada.
Key: (city_lower, state_or_province_lower) -> (latitude, longitude)

Used for proximity-based grouping of USA/Canada participants.
If a city is not in this table, timezone grouping is used as fallback.
"""

import math

CITY_COORDS = {
    # ─── UNITED STATES ───────────────────────────────────────────────────────

    # Alabama
    ('birmingham',   'alabama'): (33.5186,  -86.8104),
    ('huntsville',   'alabama'): (34.7304,  -86.5861),
    ('montgomery',   'alabama'): (32.3668,  -86.3000),
    ('mobile',       'alabama'): (30.6954,  -88.0399),

    # Alaska
    ('anchorage',    'alaska'):  (61.2181, -149.9003),
    ('fairbanks',    'alaska'):  (64.8378, -147.7164),
    ('juneau',       'alaska'):  (58.3005, -134.4197),

    # Arizona
    ('phoenix',      'arizona'): (33.4484, -112.0740),
    ('tucson',       'arizona'): (32.2226, -110.9747),
    ('mesa',         'arizona'): (33.4152, -111.8315),
    ('chandler',     'arizona'): (33.3062, -111.8413),
    ('scottsdale',   'arizona'): (33.4942, -111.9261),
    ('glendale',     'arizona'): (33.5387, -112.1860),
    ('gilbert',      'arizona'): (33.3528, -111.7890),
    ('tempe',        'arizona'): (33.4255, -111.9400),
    ('peoria',       'arizona'): (33.5806, -112.2374),
    ('surprise',     'arizona'): (33.6292, -112.3679),

    # Arkansas
    ('little rock',  'arkansas'): (34.7465,  -92.2896),
    ('fort smith',   'arkansas'): (35.3859,  -94.3985),
    ('fayetteville', 'arkansas'): (36.0626,  -94.1574),

    # California
    ('los angeles',      'california'): (34.0522, -118.2437),
    ('san diego',        'california'): (32.7157, -117.1611),
    ('san jose',         'california'): (37.3382, -121.8863),
    ('san francisco',    'california'): (37.7749, -122.4194),
    ('fresno',           'california'): (36.7378, -119.7871),
    ('sacramento',       'california'): (38.5816, -121.4944),
    ('long beach',       'california'): (33.7701, -118.1937),
    ('oakland',          'california'): (37.8044, -122.2712),
    ('bakersfield',      'california'): (35.3733, -119.0187),
    ('anaheim',          'california'): (33.8366, -117.9143),
    ('santa ana',        'california'): (33.7455, -117.8677),
    ('riverside',        'california'): (33.9533, -117.3962),
    ('irvine',           'california'): (33.6846, -117.8265),
    ('stockton',         'california'): (37.9577, -121.2908),
    ('chula vista',      'california'): (32.6401, -117.0842),
    ('fremont',          'california'): (37.5485, -121.9886),
    ('san bernardino',   'california'): (34.1083, -117.2898),
    ('modesto',          'california'): (37.6391, -120.9969),
    ('fontana',          'california'): (34.0922, -117.4350),
    ('moreno valley',    'california'): (33.9425, -117.2297),
    ('glendale',         'california'): (34.1425, -118.2551),
    ('huntington beach', 'california'): (33.6595, -117.9988),
    ('santa clarita',    'california'): (34.3917, -118.5426),
    ('garden grove',     'california'): (33.7743, -117.9378),
    ('oceanside',        'california'): (33.1959, -117.3795),
    ('rancho cucamonga', 'california'): (34.1064, -117.5931),
    ('santa rosa',       'california'): (38.4404, -122.7141),
    ('ontario',          'california'): (34.0633, -117.6509),
    ('elk grove',        'california'): (38.4088, -121.3716),
    ('corona',           'california'): (33.8753, -117.5664),
    ('salinas',          'california'): (36.6777, -121.6555),
    ('torrance',         'california'): (33.8358, -118.3406),
    ('pomona',           'california'): (34.0552, -117.7500),
    ('escondido',        'california'): (33.1192, -117.0864),
    ('hayward',          'california'): (37.6688, -122.0808),
    ('sunnyvale',        'california'): (37.3688, -122.0363),
    ('pasadena',         'california'): (34.1478, -118.1445),
    ('concord',          'california'): (37.9780, -122.0311),
    ('orange',           'california'): (33.7879, -117.8531),
    ('fullerton',        'california'): (33.8704, -117.9242),
    ('roseville',        'california'): (38.7521, -121.2880),
    ('visalia',          'california'): (36.3302, -119.2921),
    ('santa clara',      'california'): (37.3541, -121.9552),
    ('thousand oaks',    'california'): (34.1706, -118.8376),
    ('simi valley',      'california'): (34.2694, -118.7815),
    ('west covina',      'california'): (34.0686, -117.9390),
    ('vallejo',          'california'): (38.1041, -122.2566),

    # Colorado
    ('denver',           'colorado'): (39.7392, -104.9903),
    ('colorado springs', 'colorado'): (38.8339, -104.8214),
    ('aurora',           'colorado'): (39.7294, -104.8319),
    ('fort collins',     'colorado'): (40.5853, -105.0844),
    ('lakewood',         'colorado'): (39.7047, -105.0814),
    ('thornton',         'colorado'): (39.8680, -104.9719),
    ('arvada',           'colorado'): (39.8028, -105.0875),
    ('westminster',      'colorado'): (39.8367, -105.0372),
    ('pueblo',           'colorado'): (38.2544, -104.6091),
    ('boulder',          'colorado'): (40.0150, -105.2705),

    # Connecticut
    ('bridgeport',  'connecticut'): (41.1865,  -73.1952),
    ('new haven',   'connecticut'): (41.3083,  -72.9279),
    ('hartford',    'connecticut'): (41.7658,  -72.6851),
    ('stamford',    'connecticut'): (41.0534,  -73.5387),
    ('waterbury',   'connecticut'): (41.5582,  -73.0515),

    # Delaware
    ('wilmington',  'delaware'):    (39.7447,  -75.5484),
    ('dover',       'delaware'):    (39.1582,  -75.5244),

    # District of Columbia
    ('washington',    'district of columbia'): (38.9072, -77.0369),
    ('washington dc', 'district of columbia'): (38.9072, -77.0369),
    ('washington',    'dc'):                   (38.9072, -77.0369),

    # Florida
    ('jacksonville',   'florida'): (30.3322,  -81.6557),
    ('miami',          'florida'): (25.7617,  -80.1918),
    ('tampa',          'florida'): (27.9506,  -82.4572),
    ('orlando',        'florida'): (28.5383,  -81.3792),
    ('st. petersburg', 'florida'): (27.7676,  -82.6403),
    ('st petersburg',  'florida'): (27.7676,  -82.6403),
    ('hialeah',        'florida'): (25.8576,  -80.2781),
    ('tallahassee',    'florida'): (30.4518,  -84.2807),
    ('fort lauderdale','florida'): (26.1224,  -80.1373),
    ('port st. lucie', 'florida'): (27.2939,  -80.3503),
    ('port st lucie',  'florida'): (27.2939,  -80.3503),
    ('cape coral',     'florida'): (26.5629,  -81.9495),
    ('pembroke pines', 'florida'): (26.0076,  -80.3417),
    ('hollywood',      'florida'): (26.0112,  -80.1495),
    ('miramar',        'florida'): (25.9860,  -80.2327),
    ('gainesville',    'florida'): (29.6516,  -82.3248),
    ('coral springs',  'florida'): (26.2708,  -80.2706),
    ('clearwater',     'florida'): (27.9659,  -82.8001),
    ('palm bay',       'florida'): (28.0345,  -80.5887),
    ('west palm beach','florida'): (26.7153,  -80.0534),
    ('lakeland',       'florida'): (28.0395,  -81.9498),

    # Georgia
    ('atlanta',       'georgia'): (33.7490,  -84.3880),
    ('columbus',      'georgia'): (32.4610,  -84.9877),
    ('augusta',       'georgia'): (33.4735,  -82.0105),
    ('savannah',      'georgia'): (32.0835,  -81.0998),
    ('athens',        'georgia'): (33.9519,  -83.3576),
    ('macon',         'georgia'): (32.8407,  -83.6324),
    ('sandy springs', 'georgia'): (33.9304,  -84.3733),
    ('roswell',       'georgia'): (34.0232,  -84.3616),

    # Hawaii
    ('honolulu', 'hawaii'): (21.3069, -157.8583),
    ('hilo',     'hawaii'): (19.7297, -155.0900),

    # Idaho
    ('boise',       'idaho'): (43.6150, -116.2023),
    ('nampa',       'idaho'): (43.5407, -116.5635),
    ('meridian',    'idaho'): (43.6121, -116.3915),
    ('idaho falls', 'idaho'): (43.4917, -112.0339),
    ('pocatello',   'idaho'): (42.8713, -112.4455),

    # Illinois
    ('chicago',      'illinois'): (41.8781,  -87.6298),
    ('aurora',       'illinois'): (41.7606,  -88.3201),
    ('rockford',     'illinois'): (42.2711,  -89.0940),
    ('joliet',       'illinois'): (41.5250,  -88.0817),
    ('naperville',   'illinois'): (41.7508,  -88.1535),
    ('springfield',  'illinois'): (39.7817,  -89.6501),
    ('peoria',       'illinois'): (40.6936,  -89.5890),
    ('elgin',        'illinois'): (42.0354,  -88.2826),
    ('waukegan',     'illinois'): (42.3636,  -87.8448),
    ('champaign',    'illinois'): (40.1164,  -88.2434),

    # Indiana
    ('indianapolis', 'indiana'): (39.7684,  -86.1581),
    ('fort wayne',   'indiana'): (41.0793,  -85.1394),
    ('evansville',   'indiana'): (37.9716,  -87.5711),
    ('south bend',   'indiana'): (41.6764,  -86.2520),
    ('carmel',       'indiana'): (39.9784,  -86.1180),
    ('fishers',      'indiana'): (39.9567,  -85.9669),
    ('bloomington',  'indiana'): (39.1653,  -86.5264),

    # Iowa
    ('des moines',  'iowa'): (41.5868,  -93.6250),
    ('cedar rapids','iowa'): (41.9779,  -91.6656),
    ('davenport',   'iowa'): (41.5236,  -90.5776),
    ('sioux city',  'iowa'): (42.4999,  -96.4003),
    ('iowa city',   'iowa'): (41.6611,  -91.5302),

    # Kansas
    ('wichita',      'kansas'): (37.6872,  -97.3301),
    ('overland park','kansas'): (38.9822,  -94.6708),
    ('kansas city',  'kansas'): (39.1155,  -94.6268),
    ('topeka',       'kansas'): (39.0558,  -95.6890),
    ('olathe',       'kansas'): (38.8814,  -94.8191),

    # Kentucky
    ('louisville',   'kentucky'): (38.2527,  -85.7585),
    ('lexington',    'kentucky'): (38.0406,  -84.5037),
    ('bowling green','kentucky'): (36.9903,  -86.4436),
    ('owensboro',    'kentucky'): (37.7719,  -87.1112),

    # Louisiana
    ('new orleans',  'louisiana'): (29.9511,  -90.0715),
    ('baton rouge',  'louisiana'): (30.4515,  -91.1871),
    ('shreveport',   'louisiana'): (32.5252,  -93.7502),
    ('metairie',     'louisiana'): (29.9924,  -90.1613),
    ('lafayette',    'louisiana'): (30.2241,  -92.0198),

    # Maine
    ('portland',  'maine'): (43.6591,  -70.2568),
    ('lewiston',  'maine'): (44.1004,  -70.2148),
    ('bangor',    'maine'): (44.8016,  -68.7712),

    # Maryland
    ('baltimore',   'maryland'): (39.2904,  -76.6122),
    ('frederick',   'maryland'): (39.4143,  -77.4105),
    ('gaithersburg','maryland'): (39.1434,  -77.2014),
    ('rockville',   'maryland'): (39.0840,  -77.1528),
    ('columbia',    'maryland'): (39.2037,  -76.8610),

    # Massachusetts
    ('boston',      'massachusetts'): (42.3601,  -71.0589),
    ('worcester',   'massachusetts'): (42.2626,  -71.8023),
    ('springfield', 'massachusetts'): (42.1015,  -72.5898),
    ('lowell',      'massachusetts'): (42.6334,  -71.3162),
    ('cambridge',   'massachusetts'): (42.3736,  -71.1097),
    ('new bedford', 'massachusetts'): (41.6362,  -70.9342),
    ('brockton',    'massachusetts'): (42.0834,  -71.0184),
    ('quincy',      'massachusetts'): (42.2529,  -71.0023),

    # Michigan
    ('detroit',          'michigan'): (42.3314,  -83.0458),
    ('grand rapids',     'michigan'): (42.9634,  -85.6681),
    ('warren',           'michigan'): (42.4775,  -83.0277),
    ('sterling heights', 'michigan'): (42.5803,  -83.0302),
    ('ann arbor',        'michigan'): (42.2808,  -83.7430),
    ('lansing',          'michigan'): (42.7325,  -84.5555),
    ('flint',            'michigan'): (43.0125,  -83.6875),
    ('dearborn',         'michigan'): (42.3223,  -83.1763),
    ('livonia',          'michigan'): (42.3684,  -83.3527),
    ('troy',             'michigan'): (42.6064,  -83.1498),
    ('kalamazoo',        'michigan'): (42.2917,  -85.5872),

    # Minnesota
    ('minneapolis',   'minnesota'): (44.9778,  -93.2650),
    ('st. paul',      'minnesota'): (44.9537,  -93.0900),
    ('st paul',       'minnesota'): (44.9537,  -93.0900),
    ('rochester',     'minnesota'): (44.0121,  -92.4802),
    ('duluth',        'minnesota'): (46.7867,  -92.1005),
    ('bloomington',   'minnesota'): (44.8408,  -93.3777),
    ('brooklyn park', 'minnesota'): (45.0941,  -93.3563),

    # Mississippi
    ('jackson',  'mississippi'): (32.2988,  -90.1848),
    ('gulfport', 'mississippi'): (30.3674,  -89.0928),
    ('biloxi',   'mississippi'): (30.3960,  -88.8853),

    # Missouri
    ('kansas city',  'missouri'): (39.0997,  -94.5786),
    ('st. louis',    'missouri'): (38.6270,  -90.1994),
    ('st louis',     'missouri'): (38.6270,  -90.1994),
    ('springfield',  'missouri'): (37.2090,  -93.2923),
    ('columbia',     'missouri'): (38.9517,  -92.3341),
    ('independence', 'missouri'): (39.0911,  -94.4155),

    # Montana
    ('billings',    'montana'): (45.7833, -108.5007),
    ('missoula',    'montana'): (46.8721, -113.9940),
    ('great falls', 'montana'): (47.5002, -111.3008),
    ('bozeman',     'montana'): (45.6770, -111.0429),

    # Nebraska
    ('omaha',    'nebraska'): (41.2565,  -95.9345),
    ('lincoln',  'nebraska'): (40.8136,  -96.7026),
    ('bellevue', 'nebraska'): (41.1544,  -95.9146),

    # Nevada
    ('las vegas',      'nevada'): (36.1699, -115.1398),
    ('henderson',      'nevada'): (36.0395, -114.9817),
    ('reno',           'nevada'): (39.5296, -119.8138),
    ('north las vegas','nevada'): (36.1989, -115.1175),
    ('sparks',         'nevada'): (39.5349, -119.7527),

    # New Hampshire
    ('manchester', 'new hampshire'): (42.9956,  -71.4548),
    ('nashua',     'new hampshire'): (42.7654,  -71.4676),
    ('concord',    'new hampshire'): (43.2081,  -71.5376),

    # New Jersey
    ('newark',      'new jersey'): (40.7357,  -74.1724),
    ('jersey city', 'new jersey'): (40.7178,  -74.0431),
    ('paterson',    'new jersey'): (40.9168,  -74.1718),
    ('elizabeth',   'new jersey'): (40.6640,  -74.2107),
    ('trenton',     'new jersey'): (40.2171,  -74.7429),
    ('camden',      'new jersey'): (39.9259,  -75.1196),
    ('cherry hill', 'new jersey'): (39.9348,  -74.9999),
    ('toms river',  'new jersey'): (39.9537,  -74.1979),
    ('edison',      'new jersey'): (40.5187,  -74.4121),

    # New Mexico
    ('albuquerque', 'new mexico'): (35.0844, -106.6504),
    ('las cruces',  'new mexico'): (32.3199, -106.7637),
    ('rio rancho',  'new mexico'): (35.2328, -106.6630),
    ('santa fe',    'new mexico'): (35.6870, -105.9378),

    # New York
    ('new york',     'new york'): (40.7128,  -74.0060),
    ('new york city','new york'): (40.7128,  -74.0060),
    ('nyc',          'new york'): (40.7128,  -74.0060),
    ('buffalo',      'new york'): (42.8864,  -78.8784),
    ('rochester',    'new york'): (43.1566,  -77.6088),
    ('yonkers',      'new york'): (40.9312,  -73.8988),
    ('syracuse',     'new york'): (43.0481,  -76.1474),
    ('albany',       'new york'): (42.6526,  -73.7562),
    ('brooklyn',     'new york'): (40.6782,  -73.9442),
    ('queens',       'new york'): (40.7282,  -73.7949),
    ('bronx',        'new york'): (40.8448,  -73.8648),
    ('staten island','new york'): (40.5795,  -74.1502),
    ('manhattan',    'new york'): (40.7831,  -73.9712),

    # North Carolina
    ('charlotte',     'north carolina'): (35.2271,  -80.8431),
    ('raleigh',       'north carolina'): (35.7796,  -78.6382),
    ('greensboro',    'north carolina'): (36.0726,  -79.7920),
    ('durham',        'north carolina'): (35.9940,  -78.8986),
    ('winston-salem', 'north carolina'): (36.0999,  -80.2442),
    ('fayetteville',  'north carolina'): (35.0527,  -78.8784),
    ('cary',          'north carolina'): (35.7915,  -78.7811),
    ('wilmington',    'north carolina'): (34.2257,  -77.9447),

    # North Dakota
    ('fargo',       'north dakota'): (46.8772,  -96.7898),
    ('bismarck',    'north dakota'): (46.8083, -100.7837),
    ('grand forks', 'north dakota'): (47.9253,  -97.0329),

    # Ohio
    ('columbus',   'ohio'): (39.9612,  -82.9988),
    ('cleveland',  'ohio'): (41.4993,  -81.6944),
    ('cincinnati', 'ohio'): (39.1031,  -84.5120),
    ('toledo',     'ohio'): (41.6528,  -83.5379),
    ('akron',      'ohio'): (41.0814,  -81.5190),
    ('dayton',     'ohio'): (39.7589,  -84.1916),
    ('youngstown', 'ohio'): (41.0998,  -80.6495),

    # Oklahoma
    ('oklahoma city', 'oklahoma'): (35.4676,  -97.5164),
    ('tulsa',         'oklahoma'): (36.1539,  -95.9928),
    ('norman',        'oklahoma'): (35.2226,  -97.4395),
    ('broken arrow',  'oklahoma'): (36.0526,  -95.7908),

    # Oregon
    ('portland',  'oregon'): (45.5051, -122.6750),
    ('eugene',    'oregon'): (44.0521, -123.0868),
    ('salem',     'oregon'): (44.9429, -123.0351),
    ('gresham',   'oregon'): (45.5001, -122.4302),
    ('hillsboro', 'oregon'): (45.5229, -122.9898),
    ('beaverton', 'oregon'): (45.4871, -122.8037),
    ('bend',      'oregon'): (44.0582, -121.3153),
    ('medford',   'oregon'): (42.3265, -122.8756),

    # Pennsylvania
    ('philadelphia', 'pennsylvania'): (39.9526,  -75.1652),
    ('pittsburgh',   'pennsylvania'): (40.4406,  -79.9959),
    ('allentown',    'pennsylvania'): (40.6084,  -75.4902),
    ('erie',         'pennsylvania'): (42.1292,  -80.0851),
    ('reading',      'pennsylvania'): (40.3356,  -75.9269),
    ('scranton',     'pennsylvania'): (41.4090,  -75.6624),
    ('bethlehem',    'pennsylvania'): (40.6259,  -75.3705),
    ('lancaster',    'pennsylvania'): (40.0379,  -76.3055),
    ('harrisburg',   'pennsylvania'): (40.2732,  -76.8867),

    # Rhode Island
    ('providence', 'rhode island'): (41.8240,  -71.4128),
    ('warwick',    'rhode island'): (41.7001,  -71.4162),
    ('cranston',   'rhode island'): (41.7798,  -71.4373),

    # South Carolina
    ('columbia',         'south carolina'): (34.0007,  -81.0348),
    ('charleston',       'south carolina'): (32.7765,  -79.9311),
    ('north charleston', 'south carolina'): (32.8546,  -79.9748),
    ('greenville',       'south carolina'): (34.8526,  -82.3940),

    # South Dakota
    ('sioux falls', 'south dakota'): (43.5446,  -96.7311),
    ('rapid city',  'south dakota'): (44.0805, -103.2310),

    # Tennessee
    ('nashville',    'tennessee'): (36.1627,  -86.7816),
    ('memphis',      'tennessee'): (35.1495,  -90.0490),
    ('knoxville',    'tennessee'): (35.9606,  -83.9207),
    ('chattanooga',  'tennessee'): (35.0456,  -85.3097),
    ('clarksville',  'tennessee'): (36.5298,  -87.3595),
    ('murfreesboro', 'tennessee'): (35.8456,  -86.3903),

    # Texas
    ('houston',       'texas'): (29.7604,  -95.3698),
    ('san antonio',   'texas'): (29.4241,  -98.4936),
    ('dallas',        'texas'): (32.7767,  -96.7970),
    ('austin',        'texas'): (30.2672,  -97.7431),
    ('fort worth',    'texas'): (32.7555,  -97.3308),
    ('el paso',       'texas'): (31.7619, -106.4850),
    ('arlington',     'texas'): (32.7357,  -97.1081),
    ('corpus christi','texas'): (27.8006,  -97.3964),
    ('plano',         'texas'): (33.0198,  -96.6989),
    ('laredo',        'texas'): (27.5064,  -99.5075),
    ('lubbock',       'texas'): (33.5779, -101.8552),
    ('garland',       'texas'): (32.9126,  -96.6389),
    ('irving',        'texas'): (32.8140,  -96.9489),
    ('frisco',        'texas'): (33.1507,  -96.8236),
    ('amarillo',      'texas'): (35.2220, -101.8313),
    ('mckinney',      'texas'): (33.1972,  -96.6397),
    ('grand prairie', 'texas'): (32.7460,  -96.9978),
    ('brownsville',   'texas'): (25.9017,  -97.4975),
    ('killeen',       'texas'): (31.1171,  -97.7278),
    ('mcallen',       'texas'): (26.2034,  -98.2300),
    ('mesquite',      'texas'): (32.7668,  -96.5992),
    ('pasadena',      'texas'): (29.6911,  -95.2091),
    ('denton',        'texas'): (33.2148,  -97.1331),
    ('midland',       'texas'): (31.9974, -102.0779),
    ('carrollton',    'texas'): (32.9537,  -96.8903),
    ('waco',          'texas'): (31.5493,  -97.1467),
    ('beaumont',      'texas'): (30.0860,  -94.1018),
    ('odessa',        'texas'): (31.8457, -102.3676),
    ('round rock',    'texas'): (30.5083,  -97.6789),
    ('lewisville',    'texas'): (33.0462,  -96.9942),
    ('tyler',         'texas'): (32.3513,  -95.3011),
    ('abilene',       'texas'): (32.4487,  -99.7331),

    # Utah
    ('salt lake city',  'utah'): (40.7608, -111.8910),
    ('west valley city','utah'): (40.6916, -112.0010),
    ('provo',           'utah'): (40.2338, -111.6585),
    ('west jordan',     'utah'): (40.6097, -111.9391),
    ('orem',            'utah'): (40.2969, -111.6946),
    ('sandy',           'utah'): (40.5649, -111.8389),
    ('ogden',           'utah'): (41.2230, -111.9738),
    ('st. george',      'utah'): (37.0965, -113.5684),
    ('st george',       'utah'): (37.0965, -113.5684),

    # Vermont
    ('burlington',      'vermont'): (44.4759,  -73.2121),
    ('south burlington','vermont'): (44.4669,  -73.1710),

    # Virginia
    ('virginia beach', 'virginia'): (36.8529,  -75.9780),
    ('norfolk',        'virginia'): (36.8508,  -76.2859),
    ('chesapeake',     'virginia'): (36.7682,  -76.2875),
    ('richmond',       'virginia'): (37.5407,  -77.4360),
    ('newport news',   'virginia'): (37.0871,  -76.4730),
    ('alexandria',     'virginia'): (38.8048,  -77.0469),
    ('hampton',        'virginia'): (37.0299,  -76.3452),
    ('roanoke',        'virginia'): (37.2710,  -79.9414),

    # Washington
    ('seattle',      'washington'): (47.6062, -122.3321),
    ('spokane',      'washington'): (47.6588, -117.4260),
    ('tacoma',       'washington'): (47.2529, -122.4443),
    ('vancouver',    'washington'): (45.6387, -122.6615),
    ('bellevue',     'washington'): (47.6101, -122.2015),
    ('kent',         'washington'): (47.3809, -122.2348),
    ('everett',      'washington'): (47.9790, -122.2021),
    ('renton',       'washington'): (47.4799, -122.2171),
    ('federal way',  'washington'): (47.3223, -122.3126),
    ('bellingham',   'washington'): (48.7519, -122.4787),
    ('kirkland',     'washington'): (47.6769, -122.2060),

    # West Virginia
    ('charleston',  'west virginia'): (38.3498,  -81.6326),
    ('huntington',  'west virginia'): (38.4193,  -82.4452),
    ('morgantown',  'west virginia'): (39.6295,  -79.9559),

    # Wisconsin
    ('milwaukee',  'wisconsin'): (43.0389,  -87.9065),
    ('madison',    'wisconsin'): (43.0731,  -89.4012),
    ('green bay',  'wisconsin'): (44.5133,  -88.0133),
    ('kenosha',    'wisconsin'): (42.5847,  -87.8212),
    ('racine',     'wisconsin'): (42.7261,  -87.7829),
    ('appleton',   'wisconsin'): (44.2619,  -88.4154),
    ('waukesha',   'wisconsin'): (43.0117,  -88.2315),

    # Wyoming
    ('cheyenne', 'wyoming'): (41.1400, -104.8202),
    ('casper',   'wyoming'): (42.8501, -106.3252),

    # ─── CANADA ──────────────────────────────────────────────────────────────

    # Ontario
    ('toronto',        'ontario'): (43.6532,  -79.3832),
    ('ottawa',         'ontario'): (45.4215,  -75.6972),
    ('mississauga',    'ontario'): (43.5890,  -79.6441),
    ('brampton',       'ontario'): (43.7315,  -79.7624),
    ('hamilton',       'ontario'): (43.2557,  -79.8711),
    ('london',         'ontario'): (42.9849,  -81.2453),
    ('markham',        'ontario'): (43.8561,  -79.3370),
    ('vaughan',        'ontario'): (43.8361,  -79.4985),
    ('kitchener',      'ontario'): (43.4516,  -80.4925),
    ('windsor',        'ontario'): (42.3149,  -83.0364),
    ('richmond hill',  'ontario'): (43.8828,  -79.4403),
    ('oakville',       'ontario'): (43.4675,  -79.6877),
    ('burlington',     'ontario'): (43.3255,  -79.7990),
    ('sudbury',        'ontario'): (46.4900,  -80.9930),
    ('thunder bay',    'ontario'): (48.3809,  -89.2477),
    ('waterloo',       'ontario'): (43.4668,  -80.5164),
    ('oshawa',         'ontario'): (43.8971,  -78.8658),
    ('barrie',         'ontario'): (44.3894,  -79.6903),
    ('st. catharines', 'ontario'): (43.1594,  -79.2469),
    ('st catharines',  'ontario'): (43.1594,  -79.2469),
    ('cambridge',      'ontario'): (43.3616,  -80.3144),
    ('ajax',           'ontario'): (43.8509,  -79.0204),
    ('whitby',         'ontario'): (43.8975,  -78.9429),
    ('pickering',      'ontario'): (43.8384,  -79.0868),
    ('niagara falls',  'ontario'): (43.0962,  -79.0377),
    ('brantford',      'ontario'): (43.1394,  -80.2644),
    ('guelph',         'ontario'): (43.5448,  -80.2482),
    ('kingston',       'ontario'): (44.2312,  -76.4860),

    # Quebec
    ('montreal',        'quebec'): (45.5017,  -73.5673),
    ('quebec city',     'quebec'): (46.8139,  -71.2080),
    ('laval',           'quebec'): (45.6066,  -73.7124),
    ('gatineau',        'quebec'): (45.4765,  -75.7013),
    ('longueuil',       'quebec'): (45.5312,  -73.5185),
    ('sherbrooke',      'quebec'): (45.4042,  -71.8929),
    ('saguenay',        'quebec'): (48.4282,  -71.0664),
    ('trois-rivieres',  'quebec'): (46.3432,  -72.5417),
    ('trois rivieres',  'quebec'): (46.3432,  -72.5417),

    # British Columbia
    ('vancouver',    'british columbia'): (49.2827, -123.1207),
    ('surrey',       'british columbia'): (49.1913, -122.8490),
    ('burnaby',      'british columbia'): (49.2488, -122.9805),
    ('richmond',     'british columbia'): (49.1666, -123.1336),
    ('kelowna',      'british columbia'): (49.8880, -119.4960),
    ('abbotsford',   'british columbia'): (49.0504, -122.3045),
    ('coquitlam',    'british columbia'): (49.2838, -122.7932),
    ('langley',      'british columbia'): (49.1044, -122.6602),
    ('victoria',     'british columbia'): (48.4284, -123.3656),
    ('delta',        'british columbia'): (49.0847, -123.0586),
    ('kamloops',     'british columbia'): (50.6745, -120.3273),
    ('nanaimo',      'british columbia'): (49.1659, -123.9401),
    ('prince george','british columbia'): (53.9171, -122.7497),

    # Alberta
    ('calgary',       'alberta'): (51.0447, -114.0719),
    ('edmonton',      'alberta'): (53.5461, -113.4938),
    ('red deer',      'alberta'): (52.2681, -113.8112),
    ('lethbridge',    'alberta'): (49.6956, -112.8451),
    ('st. albert',    'alberta'): (53.6303, -113.6258),
    ('st albert',     'alberta'): (53.6303, -113.6258),
    ('medicine hat',  'alberta'): (50.0405, -110.6764),
    ('grande prairie','alberta'): (55.1707, -118.7884),

    # Manitoba
    ('winnipeg', 'manitoba'): (49.8951,  -97.1384),
    ('brandon',  'manitoba'): (49.8485,  -99.9500),

    # Saskatchewan
    ('saskatoon',   'saskatchewan'): (52.1332, -106.6700),
    ('regina',      'saskatchewan'): (50.4452, -104.6189),
    ('prince albert','saskatchewan'): (53.2033, -105.7531),
    ('moose jaw',   'saskatchewan'): (50.3933, -105.5519),

    # Nova Scotia
    ('halifax',   'nova scotia'): (44.6488,  -63.5752),
    ('dartmouth', 'nova scotia'): (44.6717,  -63.5679),
    ('sydney',    'nova scotia'): (46.1368,  -60.1942),

    # New Brunswick
    ('moncton',    'new brunswick'): (46.0878,  -64.7782),
    ('saint john', 'new brunswick'): (45.2733,  -66.0633),
    ('fredericton','new brunswick'): (45.9636,  -66.6431),

    # Newfoundland and Labrador
    ("st. john's",  'newfoundland and labrador'): (47.5615,  -52.7126),
    ("st. johns",   'newfoundland and labrador'): (47.5615,  -52.7126),
    ('corner brook','newfoundland and labrador'): (48.9500,  -57.9500),

    # Prince Edward Island
    ('charlottetown','prince edward island'): (46.2382,  -63.1311),

    # Yukon
    ('whitehorse', 'yukon'): (60.7212, -135.0568),

    # Northwest Territories
    ('yellowknife', 'northwest territories'): (62.4540, -114.3718),

    # Nunavut
    ('iqaluit', 'nunavut'): (63.7467,  -68.5170),
}


def get_city_coords(city, state):
    """
    Look up coordinates for a city + state/province.
    Returns (lat, lng) tuple or None if not found.
    """
    if not city or not state:
        return None
    key = (str(city).strip().lower(), str(state).strip().lower())
    return CITY_COORDS.get(key)


def haversine_miles(lat1, lng1, lat2, lng2):
    """Return the great-circle distance in miles between two lat/lng points."""
    R = 3958.8
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def proximity_sort(members, get_city_fn, get_state_fn):
    """
    Sort members geographically using nearest-neighbor traversal.

    Members whose city is found in the lookup are ordered so that
    adjacent entries in the result are as close together as possible.
    Members with no coordinates are appended at the end (timezone fallback).

    Args:
        members:      list of participant dicts
        get_city_fn:  callable(member) -> city string
        get_state_fn: callable(member) -> state/province string

    Returns:
        list of members in proximity order
    """
    located = []    # [member, lat, lng]
    unlocated = []

    for m in members:
        coords = get_city_coords(get_city_fn(m), get_state_fn(m))
        if coords:
            located.append([m, coords[0], coords[1]])
        else:
            unlocated.append(m)

    if not located:
        return unlocated

    ordered = []
    remaining = located[:]
    # Start from the northernmost point (highest latitude) for a consistent north→south sweep
    remaining.sort(key=lambda x: -x[1])
    current = remaining.pop(0)
    ordered.append(current[0])

    while remaining:
        cur_lat, cur_lng = current[1], current[2]
        nearest_idx = min(
            range(len(remaining)),
            key=lambda i: haversine_miles(cur_lat, cur_lng, remaining[i][1], remaining[i][2])
        )
        current = remaining.pop(nearest_idx)
        ordered.append(current[0])

    return ordered + unlocated
