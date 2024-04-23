"""Fan data."""
from hct.thermal_dataclasses import *

datasheet_3010 = 'https://www.mouser.de/datasheet/2/1491/OD3010-3239706.pdf'
datasheet_4010 = 'https://www.mouser.de/datasheet/2/1491/OD4010-3239432.pdf'
datasheet_4015 = 'https://www.mouser.de/datasheet/2/1491/OD4015-3239663.pdf'
datasheet_4020 = 'https://www.mouser.de/datasheet/2/1491/OD4020-3239708.pdf'
datasheet_4028 = 'https://www.mouser.de/datasheet/2/1491/OD4028-3239467.pdf'
datasheet_4028xc = 'https://www.mouser.de/datasheet/2/1491/OD4028_XC-3239458.pdf'
datasheet_5010 = 'https://www.mouser.de/datasheet/2/1491/OD5010-3239362.pdf'
datasheet_5015 = 'https://www.mouser.de/datasheet/2/1491/OD5015-3239544.pdf'
datasheet_6010 = 'https://www.mouser.de/datasheet/2/1491/OD6010-3239469.pdf'
datasheet_6015 = 'https://www.mouser.de/datasheet/2/1491/OD6015-3239460.pdf'
datasheet_6025 = 'https://www.mouser.de/datasheet/2/1491/OD6025-3239710.pdf'
datasheet_6038xc = 'https://www.mouser.de/datasheet/2/1491/OD6038_XC-3239303.pdf'

weight_3010 = 0.00907
weight_4010 = 0.0227
weight_4015 = 0.272
weight_4020 = 0.0317
weight_4028 = 0.0454
weight_5010 = 0.0317
weight_5015 = 0.0363
weight_6010 = 0.0227
weight_6015 = 0.0272
weight_6025 = 0.0635
weight_6038xc = 0.127

fan_database = {

    # Orion 3010
    "orion_od3010h": FanData("orion", "od3010h", width_height=30e-3, length=10e-3, weight=weight_3010, datasheet=datasheet_3010),
    "orion_od3010m": FanData("orion", "od3010m", width_height=30e-3, length=10e-3, weight=weight_3010, datasheet=datasheet_3010),
    "orion_od3010l": FanData("orion", "od3010l", width_height=30e-3, length=10e-3, weight=weight_3010, datasheet=datasheet_3010),

    # Orion 4010
    "orion_od4010h": FanData("orion", "od4010h", width_height=40e-3, length=10e-3, weight=weight_4010, datasheet=datasheet_4010),
    "orion_od4010hh": FanData("orion", "od4010hh", width_height=40e-3, length=10e-3, weight=weight_4010, datasheet=datasheet_4010),
    "orion_od4010l": FanData("orion", "od4010l", width_height=40e-3, length=10e-3, weight=weight_4010, datasheet=datasheet_4010),
    "orion_od4010m": FanData("orion", "od4010m", width_height=40e-3, length=10e-3, weight=weight_4010, datasheet=datasheet_4010),

    # Orion 4015
    "orion_od4015h": FanData("orion", "od4015h", width_height=40e-3, length=15e-3, weight=weight_4015, datasheet=datasheet_4015),
    "orion_od4015l": FanData("orion", "od4015l", width_height=40e-3, length=15e-3, weight=weight_4015, datasheet=datasheet_4015),
    "orion_od4015m": FanData("orion", "od4015m", width_height=40e-3, length=15e-3, weight=weight_4015, datasheet=datasheet_4015),

    # Orion 4020
    "orion_od4020h": FanData("orion", "od4020h", width_height=40e-3, length=20e-3, weight=weight_4020, datasheet=datasheet_4020),
    "orion_od4020l": FanData("orion", "od4020l", width_height=40e-3, length=20e-3, weight=weight_4020, datasheet=datasheet_4020),
    "orion_od4020m": FanData("orion", "od4020m", width_height=40e-3, length=20e-3, weight=weight_4020, datasheet=datasheet_4020),

    # Orion 4028
    "orion_od4028h": FanData("orion", "od4028h", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028),
    "orion_od4028h3": FanData("orion", "od4028h3", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028),
    "orion_od4028hh": FanData("orion", "od4028hh", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028),
    "orion_od4028l": FanData("orion", "od4028l", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028),
    "orion_od4028m": FanData("orion", "od4028m", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028),
    "orion_od4028xc": FanData("orion", "od4028xc", width_height=40e-3, length=28e-3, weight=weight_4028, datasheet=datasheet_4028xc),

    # Orion 5010
    "orion_od5010hh": FanData("orion", "od5010hh", width_height=50e-3, length=10e-3, weight=weight_5010, datasheet=datasheet_5010),
    "orion_od5010h": FanData("orion", "od5010h", width_height=50e-3, length=10e-3, weight=weight_5010, datasheet=datasheet_5010),
    "orion_od5010m": FanData("orion", "od5010m", width_height=50e-3, length=10e-3, weight=weight_5010, datasheet=datasheet_5010),
    "orion_od5010l": FanData("orion", "od5010l", width_height=50e-3, length=10e-3, weight=weight_5010, datasheet=datasheet_5010),

    # Orion 5015
    "orion_od5015hh": FanData("orion", "od5015hh", width_height=50e-3, length=15e-3, weight=weight_5015, datasheet=datasheet_5015),
    "orion_od5015h": FanData("orion", "od5015h", width_height=50e-3, length=15e-3, weight=weight_5015, datasheet=datasheet_5015),
    "orion_od5015m": FanData("orion", "od5015m", width_height=50e-3, length=15e-3, weight=weight_5015, datasheet=datasheet_5015),


    # Orion 6010
    "orion_od6010h": FanData("orion", "od6010h", width_height=60e-3, length=10e-3, weight=weight_6010, datasheet=datasheet_6010),
    "orion_od6010m": FanData("orion", "od6010m", width_height=60e-3, length=10e-3, weight=weight_6010, datasheet=datasheet_6010),
    "orion_od6010l": FanData("orion", "od6010l", width_height=60e-3, length=10e-3, weight=weight_6010, datasheet=datasheet_6010),


    # Orion 6015
    "orion_od6015hh": FanData("orion", "od6015hh", width_height=60e-3, length=15e-3, weight=weight_6015, datasheet=datasheet_6015),
    "orion_od6015h": FanData("orion", "od6015h", width_height=60e-3, length=15e-3, weight=weight_6015, datasheet=datasheet_6015),
    "orion_od6015m": FanData("orion", "od6015m", width_height=60e-3, length=15e-3, weight=weight_6015, datasheet=datasheet_6015),
    "orion_od6015l": FanData("orion", "od6015l", width_height=60e-3, length=15e-3, weight=weight_6015, datasheet=datasheet_6015),

    # Orion 6025
    "orion_od6025hh": FanData("orion", "od6025hh", width_height=60e-3, length=25e-3, weight=weight_6025, datasheet=datasheet_6025),
    "orion_od6025h": FanData("orion", "od6025h", width_height=60e-3, length=25e-3, weight=weight_6025, datasheet=datasheet_6025),
    "orion_od6025m": FanData("orion", "od6025m", width_height=60e-3, length=25e-3, weight=weight_6025, datasheet=datasheet_6025),
    "orion_od6025l": FanData("orion", "od6025l", width_height=60e-3, length=25e-3, weight=weight_6025, datasheet=datasheet_6025),

    # Orion 6038
    "orion_od6038xchh": FanData("orion", "od6038xchh", width_height=60e-3, length=38e-3, weight=weight_6038xc, datasheet=datasheet_6038xc),
    "orion_od6038xch": FanData("orion", "od6038xch", width_height=60e-3, length=38e-3, weight=weight_6038xc, datasheet=datasheet_6038xc),
    "orion_od6038xcl": FanData("orion", "od6038xcl", width_height=60e-3, length=38e-3, weight=weight_6038xc, datasheet=datasheet_6038xc),
}
