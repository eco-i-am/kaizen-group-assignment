#!/usr/bin/env python3
import random
from datetime import datetime, timedelta

# Additional user IDs provided by the user
additional_user_ids = [
    1163, 1372, 1147, 1162, 1398, 1399, 1400, 1158, 1216, 1295, 1188, 1404, 1214, 1110, 1402, 1403, 1346, 1391, 369, 1334,
    1290, 1406, 1405, 1324, 1409, 1410, 1401, 298, 1294, 1396, 1341, 1413, 1179, 1275, 1259, 561, 1415, 1206, 1416, 1414,
    1279, 1420, 1337, 1422, 1417, 1362, 1427, 1423, 1101, 1429, 887, 1149, 1393, 1374, 1238, 1431, 1339, 1411, 1394, 1432,
    1428, 1435, 1434, 1430, 1436, 1438, 1424, 1323, 1439, 1344, 1444, 1395, 1447, 1447, 1308, 554, 798, 1418, 1314, 1258,
    1350, 1452, 1270, 928, 1262, 1120, 1456, 1450, 1458, 1459, 1343, 1157, 1173, 1397, 1451, 1460, 1463, 1094, 1464, 1455,
    1461, 1468, 1467, 1469, 909, 979, 1470, 1283, 1473, 1474, 1475, 1478, 1477, 1040, 1433, 1457, 1421, 1040, 1481, 1376,
    1482, 1484, 1483, 1485, 1471, 1390, 1392, 1472, 1486, 350, 1479, 1156, 886, 1488, 1489, 1407, 1167, 1109, 1366, 1476,
    1494, 1493, 1201, 1118, 1495, 1490, 1499, 1231, 1240, 1505, 1502, 1506, 1512, 1375, 1507, 1419, 828, 1513, 1170, 1515,
    1360, 1498, 1518, 1437, 1520, 1228, 1521, 1257, 1209, 1217, 1197, 1524, 751, 1526, 1527, 645, 1496, 1530, 1514, 1519,
    970, 1426, 1386, 1535, 1536, 1532, 1537, 1538, 1534, 1306, 1540, 1480, 1541, 1364, 602, 1546, 1547, 1446, 1190, 1543,
    1551, 1549, 1552, 1553, 1558, 1563, 1560, 1562, 1564, 1150, 1566, 1542, 1569, 1282, 385, 1271, 1572, 1579, 1580, 477,
    1555, 1338, 1338, 1584, 1577, 1561, 1586, 1587, 1351, 1491, 1134, 1510, 1590, 1582, 1592, 1593, 1557, 1594, 1443, 1168,
    1550, 1548, 296, 1589, 1596, 1598, 1597, 1545, 1585, 1098, 1601, 1602, 1154, 1602, 1603, 283, 1119, 1523, 1453, 1600,
    1153, 1606, 1607, 1608, 1576, 1504, 1554, 1611, 1533, 607, 1508, 1610, 1614, 1023, 1615, 433, 1571, 1616, 1595, 1559,
    1605, 1528, 1383, 1152, 1381, 1623, 1618, 1625, 1624, 1626, 160, 1621, 1627, 1632, 1631, 1612, 1633, 1630, 1503, 1636,
    1637, 1599, 1517, 716, 1638, 165, 1102, 627, 1466, 1639, 1604, 1640, 1500, 1641, 1642, 370, 1609, 1643, 711, 1588, 1487,
    1647, 1531, 1649, 1644, 210, 1654, 1653, 1650, 1655, 827, 476, 472, 498, 1648, 1656, 1574, 449, 1661, 517, 1662, 647,
    1615, 718, 1663, 318, 1645, 742, 251, 1014, 1667, 271, 425, 154, 1671, 1670, 1613, 1672, 1449, 1617, 447, 601, 915, 214,
    341, 1675, 234, 1681, 312, 1683, 1684, 1687, 727, 1678, 1690, 458, 1692, 475, 1658, 1664, 1511, 1570, 1318, 1620, 259,
    1693, 270, 1680, 693, 1686, 1041, 1695, 1525, 1691, 436, 1704, 1699, 316, 565, 1707, 435, 374, 990, 1652, 1709, 1711,
    1713, 1211, 1032, 1712, 336, 1700, 434, 614, 1676, 1646, 1556, 142, 1717, 1673, 1720, 1651, 908, 1635, 465, 1694, 1708,
    1722, 1132, 1303, 448, 1724, 533, 258, 1725, 368, 918, 730, 622, 423, 1730, 1312, 319, 524, 1619, 849, 1668, 196, 1454,
    1723, 1462, 1732, 1733, 480, 1718, 1726, 1739, 1738, 1743, 1501, 568, 1749, 1758, 1741, 658, 1761, 1408, 1760, 263, 1108,
    1757, 1193, 1017, 1353, 1674, 1764, 702, 529, 1744, 1767, 1769, 1660, 1755, 1768, 1425, 1659, 1746, 1679, 590, 134, 274,
    245, 1775, 1777, 1774, 1772, 1779, 1773, 1780, 1782, 1688, 907, 356, 1783, 914, 1784, 293, 1770, 1790, 227, 1795, 1706,
    1791, 1747, 1794, 482, 1778, 1522, 1803, 1805, 1703, 1702, 741, 1800, 1689, 1807, 1809, 619, 1698, 624, 1754, 1788, 383,
    1798, 1812, 1003, 1810, 1811, 215, 1813, 1816, 373, 1814, 321, 1820, 187, 666, 885, 1825, 1793, 514, 1827, 1802, 1701,
    1797, 1762, 182, 1377, 779, 1829, 1628, 1838, 1839, 1823, 1830, 1629, 1740, 1745, 483, 1575, 1846, 1843, 1851, 1847, 1852,
    1848, 1833, 682, 1844, 1855, 308, 547, 1682, 1856, 1799, 1696, 709, 1865, 1867, 1808, 1748, 695, 1868, 1872, 1716, 1877,
    265, 1863, 770, 1880, 1879, 1849, 1884, 1291, 1864, 141, 1529, 1885, 1889, 1893, 540, 1873, 1896, 1901, 1903, 1894, 1902,
    1910, 1006, 1705, 1908, 1911, 1781, 1913, 1058, 1909, 1866, 1845, 1918, 1915, 1819, 1922, 203, 1756, 1765, 1926, 343, 1714,
    1928, 685, 173, 1824, 1933, 1935, 1936, 1938, 139, 1939, 1941, 1942, 1937, 1944, 1943, 1763, 1766, 1951, 1952, 1881, 1953,
    1950, 1750, 1958, 1955, 1917, 1959, 1961, 197, 731, 731, 943, 1060, 780, 1968, 1963, 731, 1964, 1965, 1967, 1972, 1975,
    1721, 1974, 1979, 1982, 1753, 408, 1983, 814, 1581, 1912, 1986, 1882, 1985, 1568, 835, 1946, 1993, 1890, 1995, 1871, 1897,
    2004, 1583, 580, 2007, 681, 2006, 1751, 1252, 812, 803, 640, 824, 2022, 2017, 1904, 1980, 2021, 2018, 2024, 2019, 1497,
    2032, 357, 2023, 2037, 2015, 2001, 1949, 2040, 1994, 1957, 253, 1697, 1044, 2034, 2057, 2003, 2047, 1931, 2048, 2011, 2053,
    1888, 2043, 2052, 2035, 2044, 1886, 2045, 297, 2046, 1715, 2030, 2041, 1821, 1854, 1835, 1837, 1786, 240, 1859, 1862, 2008,
    1815, 1858, 794, 1442, 2033, 783, 1742, 419, 1742, 1831, 1737, 347, 1960, 2029, 1297, 1031, 1665, 1826, 1310, 1996, 2016,
    889, 1978, 2027, 1785, 628, 1945, 1776, 999, 1907, 1989, 1657, 1256, 1891, 2010, 1728, 1850, 1850, 552, 2067, 1947, 148,
    2056, 511, 1771, 1869, 1906, 2026, 157, 327, 1832, 776, 1977, 328, 945, 1710, 325, 1987, 445, 156, 1787, 1876, 1878, 1940,
    1448, 1999, 193, 1966, 2051, 1713, 2055, 1971, 1899, 1836, 1828, 2013, 492, 1719, 2042, 1759, 2063, 1874, 1806, 1970, 805,
    427, 158, 715, 526, 421, 667, 309, 303, 2066, 2061, 1806, 1516, 2058, 1159, 2050, 740, 1948, 1565, 295, 2031, 1509, 453,
    661, 600, 1801, 1990, 493, 1973, 1969, 613, 1818, 1225, 2069, 1927, 1412, 1914, 2014, 636, 1992, 235, 1099, 2071, 151,
    2028, 1105, 451, 1834, 1255, 964, 1991, 168, 1039, 813, 1930, 898, 2062, 1976, 1016, 1905, 405, 2072, 1981, 1734, 1122,
    1654, 2009, 1932, 2038, 2077, 1857, 2065, 1861, 1883, 1492, 2025, 1925, 282, 1997, 1195, 1895, 2079, 1984, 1752, 291, 1998,
    1929, 1924, 2020, 2080, 906, 688, 2081, 190, 2082, 896, 2073, 629, 2078, 1735, 189, 2083, 1875, 2075, 2092, 184, 1892,
    1727, 1465, 2094, 2088, 2086, 1840, 1796, 2096, 1934, 489, 2084, 304, 1182, 2098, 535, 1175, 1860, 2101, 1175, 2102, 550,
    1729, 2012, 2105, 2106, 971, 2104, 307, 816, 2108, 1956, 819, 1817, 2059, 2002, 2111, 2112, 577, 1898, 686, 934, 972, 1358,
    2113, 2114, 2115, 1919, 2116, 2117, 2054, 652, 2118, 810, 2121, 2109, 2124, 2123, 868, 868, 795, 2123, 973, 1921, 209,
    2064, 2125, 249, 687, 367, 1591, 2100, 361, 2110, 177, 2091, 1387, 2039, 2090, 519, 1002, 1299, 919, 635, 1374, 618, 646,
    217, 2049, 1870, 1792, 260, 650, 2089, 899, 2119, 772, 110, 67, 57, 462, 131, 1578, 2103, 1544, 706, 1685, 1789, 63, 56,
    82, 952, 774, 1842, 123, 673, 116, 49, 174, 66, 1841, 2093, 108, 58, 159, 1853, 38, 64, 288, 2070, 55, 132, 1293, 115,
    105, 112, 65, 494, 118, 128, 130, 1377, 1336, 144, 120, 149, 856, 1106, 555, 1042, 1923, 2095, 126, 323, 386, 117, 94,
    1916, 1634, 531, 1138, 205, 802, 1802, 942, 1804, 2130, 2107, 103, 2136, 1161, 2060, 244, 581, 69, 40, 84, 594, 2131, 121,
    2135, 1567, 1445, 104, 277, 2137, 2068, 2000, 815, 502, 2138, 2005, 2097, 2076, 2133, 247, 60, 389, 349, 459, 882, 863,
    2140, 275, 106, 556, 2139, 1005, 953, 1806, 122, 1067, 736, 1822, 651, 996, 2141, 314, 322, 2142, 219, 576, 256, 2143,
    876, 756, 1066, 878, 890, 59, 2144, 420, 129, 41, 114, 763, 1019, 124, 586, 2074, 966, 2132, 487, 2015, 1954, 1018, 1070,
    998, 1146, 1962, 2126, 107, 79, 485, 109, 1369, 77, 39, 2146, 78, 2147, 1920, 1054, 2099, 1053, 83, 831, 1050, 164, 2151,
    787, 348, 468, 2149, 2148, 866, 2150, 1052, 903, 1065, 719, 1669, 1666, 600, 2036, 2087, 2085, 724, 1331, 1331, 1072, 76,
    2155, 74, 220, 80, 525, 905, 2156, 469, 469, 382, 461, 111, 44, 101, 659, 2120, 1345, 1622, 281, 231, 2158, 199, 246, 883,
    404, 926, 710, 1988, 1887, 113, 417, 294, 471, 62, 521, 1573, 870, 2157, 371, 300, 857, 392, 1900, 2154, 541, 1059, 1068,
    1695, 1695, 42, 1731, 355, 2122, 2160, 406, 188, 1476, 1071, 1056, 2159, 2134
]

# Data options for variety
gender_identities = ['Male', 'Female', 'LGBTQ+']
kaizen_client_types = ['first_time', 'returning_s7', 'returning_other']
sex_options = ['Male', 'Female']
lifting_experiences = ['complete_beginner', 'beginner', 'intermediate', 'advanced']
group_gender_preferences = ['same_gender', 'no_preference']
current_goals = ['lean_down', 'get_bigger', 'not_sure']
follow_up_levels = ['level_1', 'level_2', 'level_3']
team_names = [
    'Phoenix Squad', 'Thunder Warriors', 'Elite Force', 'Power Pack', 'Fitness Fusion',
    'Strength Syndicate', 'Wellness Warriors', 'Dynamic Duo', 'Peak Performers', 'Core Crushers',
    'Cardio Kings', 'Muscle Masters', 'Agility Aces', 'Speed Stars', 'Recovery Rangers',
    'Nutrition Ninjas', 'Balance Builders', 'Flexibility First', 'Endurance Elite', 'Health Heroes'
]
coach_names = [
    'Coach Maria Santos', 'Coach Jennifer Wilson', 'Coach David Thompson', 'Coach Lim Wei Ming',
    'Coach Carlos Silva', 'Coach Sarah Johnson', 'Coach Michael Chen', 'Coach Lisa Rodriguez',
    'Coach Robert Kim', 'Coach Amanda Lee', 'Coach James Garcia', 'Coach Michelle Wong',
    'Coach Daniel Park', 'Coach Juan Dela Cruz', 'Coach Pedro Reyes', 'Coach Emily Davis',
    'Coach Alex Johnson', 'Coach Chris Martinez', 'Coach Rachel Green', 'Coach Tom Anderson'
]

# Philippine cities and provinces for variety
philippine_locations = [
    ('Philippines', None, 'Metro Manila', 'Quezon City'),
    ('Philippines', None, 'Metro Manila', 'Manila'),
    ('Philippines', None, 'Metro Manila', 'Makati'),
    ('Philippines', None, 'Metro Manila', 'Taguig'),
    ('Philippines', None, 'Metro Manila', 'Pasig'),
    ('Philippines', None, 'Metro Manila', 'Caloocan'),
    ('Philippines', None, 'Metro Manila', 'Malabon'),
    ('Philippines', None, 'Metro Manila', 'Navotas'),
    ('Philippines', None, 'Metro Manila', 'Valenzuela'),
    ('Philippines', None, 'Metro Manila', 'Parañaque'),
    ('Philippines', None, 'Metro Manila', 'Las Piñas'),
    ('Philippines', None, 'Metro Manila', 'Muntinlupa'),
    ('Philippines', None, 'Cebu', 'Cebu City'),
    ('Philippines', None, 'Cebu', 'Mandaue City'),
    ('Philippines', None, 'Cebu', 'Talisay City'),
    ('Philippines', None, 'Batangas', 'Batangas City'),
    ('Philippines', None, 'Batangas', 'Lipa City'),
    ('Philippines', None, 'Batangas', 'Tanauan City'),
    ('Philippines', None, 'Pampanga', 'Angeles City'),
    ('Philippines', None, 'Pampanga', 'San Fernando City'),
    ('Philippines', None, 'Iloilo', 'Iloilo City'),
    ('Philippines', None, 'Iloilo', 'Passi City'),
    ('Philippines', None, 'Negros Occidental', 'Bacolod City'),
    ('Philippines', None, 'Negros Occidental', 'Silay City'),
    ('Philippines', None, 'Zamboanga del Sur', 'Zamboanga City'),
    ('Philippines', None, 'Zamboanga del Sur', 'Dipolog City'),
    ('Philippines', None, 'Bohol', 'Tagbilaran City'),
    ('Philippines', None, 'Bohol', 'Jagna'),
    ('Philippines', None, 'Leyte', 'Tacloban City'),
    ('Philippines', None, 'Leyte', 'Ormoc City'),
    ('Philippines', None, 'Palawan', 'Puerto Princesa City'),
    ('Philippines', None, 'Palawan', 'El Nido'),
    ('Philippines', None, 'Davao del Sur', 'Digos City'),
    ('Philippines', None, 'Baguio', 'Baguio City'),
    ('Philippines', None, 'Cagayan de Oro', 'Cagayan de Oro City'),
    ('Philippines', None, 'General Santos', 'General Santos City'),
    ('Philippines', None, 'Iligan', 'Iligan City'),
    ('Philippines', None, 'Butuan', 'Butuan City'),
    ('Philippines', None, 'Dumaguete', 'Dumaguete City'),
    ('Philippines', None, 'Legazpi', 'Legazpi City'),
    ('Philippines', None, 'Calamba', 'Calamba City'),
    ('Philippines', None, 'Lucena', 'Lucena City'),
    ('Philippines', None, 'Naga', 'Naga City'),
    ('Philippines', None, 'San Carlos', 'San Carlos City'),
    ('Philippines', None, 'Roxas', 'Roxas City'),
    ('Philippines', None, 'San Jose del Monte', 'San Jose del Monte City'),
    ('Philippines', None, 'Antipolo', 'Antipolo City'),
    ('Philippines', None, 'Sorsogon', 'Sorsogon City'),
    ('Philippines', None, 'Masbate', 'Masbate City')
]

# International locations
international_locations = [
    ('United States', 'California', None, 'Los Angeles'),
    ('United States', 'New York', None, 'New York City'),
    ('United States', 'Texas', None, 'Houston'),
    ('United States', 'Florida', None, 'Miami'),
    ('Canada', 'Ontario', None, 'Toronto'),
    ('Canada', 'British Columbia', None, 'Vancouver'),
    ('Australia', 'Victoria', None, 'Melbourne'),
    ('Australia', 'New South Wales', None, 'Sydney'),
    ('United Kingdom', 'England', None, 'London'),
    ('United Kingdom', 'Scotland', None, 'Edinburgh'),
    ('Germany', 'Bavaria', None, 'Munich'),
    ('Germany', 'Berlin', None, 'Berlin'),
    ('France', 'Île-de-France', None, 'Paris'),
    ('France', 'Provence-Alpes-Côte d\'Azur', None, 'Marseille'),
    ('Italy', 'Lombardy', None, 'Milan'),
    ('Italy', 'Lazio', None, 'Rome'),
    ('Spain', 'Madrid', None, 'Madrid'),
    ('Spain', 'Catalonia', None, 'Barcelona'),
    ('Netherlands', 'North Holland', None, 'Amsterdam'),
    ('Netherlands', 'South Holland', None, 'Rotterdam'),
    ('Sweden', 'Stockholm', None, 'Stockholm'),
    ('Sweden', 'Västra Götaland', None, 'Gothenburg'),
    ('Norway', 'Oslo', None, 'Oslo'),
    ('Norway', 'Vestland', None, 'Bergen'),
    ('Denmark', 'Copenhagen', None, 'Copenhagen'),
    ('Denmark', 'Central Jutland', None, 'Aarhus'),
    ('Finland', 'Helsinki', None, 'Helsinki'),
    ('Finland', 'Pirkanmaa', None, 'Tampere'),
    ('Switzerland', 'Zurich', None, 'Zurich'),
    ('Switzerland', 'Geneva', None, 'Geneva'),
    ('Austria', 'Vienna', None, 'Vienna'),
    ('Austria', 'Salzburg', None, 'Salzburg'),
    ('Belgium', 'Flanders', None, 'Antwerp'),
    ('Belgium', 'Brussels', None, 'Brussels'),
    ('Ireland', 'Dublin', None, 'Dublin'),
    ('Ireland', 'Cork', None, 'Cork'),
    ('Portugal', 'Lisbon', None, 'Lisbon'),
    ('Portugal', 'Porto', None, 'Porto'),
    ('Greece', 'Attica', None, 'Athens'),
    ('Greece', 'Central Macedonia', None, 'Thessaloniki'),
    ('Poland', 'Masovia', None, 'Warsaw'),
    ('Poland', 'Lesser Poland', None, 'Kraków'),
    ('Czech Republic', 'Prague', None, 'Prague'),
    ('Czech Republic', 'South Moravian', None, 'Brno'),
    ('Hungary', 'Budapest', None, 'Budapest'),
    ('Hungary', 'Pest', None, 'Debrecen'),
    ('Romania', 'Bucharest', None, 'Bucharest'),
    ('Romania', 'Cluj', None, 'Cluj-Napoca'),
    ('Croatia', 'Zagreb', None, 'Zagreb'),
    ('Croatia', 'Split-Dalmatia', None, 'Split'),
    ('Slovenia', 'Ljubljana', None, 'Ljubljana'),
    ('Slovenia', 'Maribor', None, 'Maribor'),
    ('Slovakia', 'Bratislava', None, 'Bratislava'),
    ('Slovakia', 'Košice', None, 'Košice'),
    ('Estonia', 'Harju', None, 'Tallinn'),
    ('Estonia', 'Tartu', None, 'Tartu'),
    ('Latvia', 'Riga', None, 'Riga'),
    ('Latvia', 'Daugavpils', None, 'Daugavpils'),
    ('Lithuania', 'Vilnius', None, 'Vilnius'),
    ('Lithuania', 'Kaunas', None, 'Kaunas'),
    ('Malta', 'Valletta', None, 'Valletta'),
    ('Malta', 'Sliema', None, 'Sliema'),
    ('Cyprus', 'Nicosia', None, 'Nicosia'),
    ('Cyprus', 'Limassol', None, 'Limassol'),
    ('Iceland', 'Reykjavík', None, 'Reykjavík'),
    ('Iceland', 'Akureyri', None, 'Akureyri'),
    ('Luxembourg', 'Luxembourg City', None, 'Luxembourg City'),
    ('Luxembourg', 'Esch-sur-Alzette', None, 'Esch-sur-Alzette'),
    ('Monaco', 'Monaco City', None, 'Monaco City'),
    ('Liechtenstein', 'Vaduz', None, 'Vaduz'),
    ('Andorra', 'Andorra la Vella', None, 'Andorra la Vella'),
    ('San Marino', 'San Marino City', None, 'San Marino City'),
    ('Vatican City', 'Vatican City', None, 'Vatican City'),
    ('Mexico', 'Mexico City', None, 'Mexico City'),
    ('Mexico', 'Jalisco', None, 'Guadalajara'),
    ('Argentina', 'Buenos Aires', None, 'Buenos Aires'),
    ('Argentina', 'Córdoba', None, 'Córdoba'),
    ('Brazil', 'São Paulo', None, 'São Paulo'),
    ('Brazil', 'Rio de Janeiro', None, 'Rio de Janeiro'),
    ('Chile', 'Santiago', None, 'Santiago'),
    ('Chile', 'Valparaíso', None, 'Valparaíso'),
    ('Colombia', 'Bogotá', None, 'Bogotá'),
    ('Colombia', 'Antioquia', None, 'Medellín'),
    ('Peru', 'Lima', None, 'Lima'),
    ('Peru', 'Arequipa', None, 'Arequipa'),
    ('Venezuela', 'Caracas', None, 'Caracas'),
    ('Venezuela', 'Maracaibo', None, 'Maracaibo'),
    ('Ecuador', 'Pichincha', None, 'Quito'),
    ('Ecuador', 'Guayas', None, 'Guayaquil'),
    ('Bolivia', 'La Paz', None, 'La Paz'),
    ('Bolivia', 'Santa Cruz', None, 'Santa Cruz'),
    ('Paraguay', 'Central', None, 'Asunción'),
    ('Paraguay', 'Alto Paraná', None, 'Ciudad del Este'),
    ('Uruguay', 'Montevideo', None, 'Montevideo'),
    ('Uruguay', 'Canelones', None, 'Canelones'),
    ('Japan', 'Tokyo', None, 'Tokyo'),
    ('Japan', 'Osaka', None, 'Osaka'),
    ('South Korea', 'Seoul', None, 'Seoul'),
    ('South Korea', 'Busan', None, 'Busan'),
    ('China', 'Beijing', None, 'Beijing'),
    ('China', 'Shanghai', None, 'Shanghai'),
    ('India', 'Maharashtra', None, 'Mumbai'),
    ('India', 'Delhi', None, 'New Delhi'),
    ('Thailand', 'Bangkok', None, 'Bangkok'),
    ('Thailand', 'Chiang Mai', None, 'Chiang Mai'),
    ('Vietnam', 'Ho Chi Minh City', None, 'Ho Chi Minh City'),
    ('Vietnam', 'Hanoi', None, 'Hanoi'),
    ('Malaysia', 'Kuala Lumpur', None, 'Kuala Lumpur'),
    ('Malaysia', 'Penang', None, 'George Town'),
    ('Singapore', None, None, 'Singapore'),
    ('Indonesia', 'Jakarta', None, 'Jakarta'),
    ('Indonesia', 'Surabaya', None, 'Surabaya'),
    ('Philippines', None, 'Metro Manila', 'Quezon City'),
    ('Philippines', None, 'Metro Manila', 'Manila')
]

def generate_random_date():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date.strftime('%Y-%m-%d %H:%M:%S')

def generate_record(user_id):
    gender_identity = random.choice(gender_identities)
    kaizen_client_type = random.choice(kaizen_client_types)
    sex = random.choice(sex_options)
    residing_in_philippines = random.choice([0, 1])
    lifting_experience = random.choice(lifting_experiences)
    group_gender_preference = random.choice(group_gender_preferences)
    current_goal = random.choice(current_goals)
    follow_up_level = random.choice(follow_up_levels)
    has_accountability_buddies = random.choice([0, 1])
    
    # Generate location
    if residing_in_philippines:
        country, state, province, city = random.choice(philippine_locations)
    else:
        country, state, province, city = random.choice(international_locations)
    
    # Generate team name and buddies if has_accountability_buddies is 1
    temporary_team_name = None
    accountability_buddies = None
    previous_coach_name = None
    retain_previous_coach = random.choice([0, 1])
    
    if has_accountability_buddies:
        temporary_team_name = random.choice(team_names)
        accountability_buddies = '["buddy1@email.com","buddy2@email.com"]'
    
    if retain_previous_coach:
        previous_coach_name = random.choice(coach_names)
    
    go_solo = random.choice([0, 1])
    
    created_at = generate_random_date()
    updated_at = created_at
    
    return f"({user_id}, 4, '{gender_identity}', '{kaizen_client_type}', '{created_at}', '{updated_at}', '{sex}', {residing_in_philippines}, '{lifting_experience}', '{group_gender_preference}', '{current_goal}', '{follow_up_level}', {has_accountability_buddies}, {repr(temporary_team_name) if temporary_team_name else 'NULL'}, {repr(accountability_buddies) if accountability_buddies else 'NULL'}, '{country}', {repr(state) if state else 'NULL'}, {repr(province) if province else 'NULL'}, '{city}', {go_solo}, {retain_previous_coach}, {repr(previous_coach_name) if previous_coach_name else 'NULL'})"

# Generate the additional records
additional_records = []
for user_id in additional_user_ids:
    record = generate_record(user_id)
    additional_records.append(record)

# Read existing file
with open('phpmyadmin_test_data.sql', 'r') as f:
    content = f.read()

# Remove the last semicolon and add the new records
content = content.rstrip().rstrip(';')
content += ',\n' + ',\n'.join(additional_records) + ';'

# Write back to file
with open('phpmyadmin_test_data.sql', 'w') as f:
    f.write(content)

print(f"Successfully added {len(additional_user_ids)} new records!")
print(f"Total records in file: {len(additional_user_ids) + 99}") 