#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# Copyright © 2018 Dell Inc. or its subsidiaries. All rights reserved.
# Dell, EMC, and other trademarks are trademarks of Dell Inc. or its subsidiaries.
# Other trademarks may be trademarks of their respective owners.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Vaideeswaran Ganesan
#
from omsdk.sdkdevice import iDeviceDiscovery, iDeviceRegistry, iDeviceDriver
from omsdk.sdkcenum import EnumWrapper
from omsdk.sdkproto import PSNMP
import sys
import logging

logger = logging.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

try:
    from pysnmp.hlapi import *
    from pysnmp.smi import *
    from pysnmp.entity.rfc3413.oneliner import cmdgen
    from pysnmp.proto import rfc1902
    from pysnmp import debug
    PyPSNMP = True
except ImportError:
    PyPSNMP = False

class NoConfig:
    def __init__(self, obj):
        logger.debug("not implemented")

NSeriesCompEnum = EnumWrapper('NSeriesCompEnum', {
    "System" : "System",
    "dellNetFanTray" : "dellNetFanTray",
    "dellNetPowerSupply" : "dellNetPowerSupply",
    "dellNetProcessor" : "dellNetProcessor",
    "dellNetPort" : "dellNetPort",
    "dellNetFan" : "dellNetFan",
    "dellNetPowerSupplyTray" : "dellNetPowerSupplyTray",
}).enum_type

if PyPSNMP:
    NSeriesPSNMPViews = {
     NSeriesCompEnum.System : { 
         'SysObjectID' : ObjectIdentity('SNMPv2-MIB', 'sysObjectID'),
         'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.4"),
         'PrimaryStatus' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.1"),
         'Model' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.1"),
         'Description' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.2"),
         'FirmwareVersion' : ObjectIdentity(".1.3.6.1.4.1.674.10895.3000.1.2.100.4"),
         'Location' : ObjectIdentity("1.3.6.1.2.1.1.6"),
         'NetwUMACAddress' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.1.9"),
         'NetwUStatus':  ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.8"),
         'NetwUSerialNo':  ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.2"),
         'NetwUPartNo':  ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.3.4.1.17"),
         'PPID' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.7"),
         'ExpressServiceCode' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.8.1.9"),
         'ManagementIP' :  ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.6"),
         'Hostname' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.100.7"),
         'SwitchUptime': ObjectIdentity("1.3.6.1.2.1.1.3"),
     },
     NSeriesCompEnum.dellNetPort : { 
       'Description' : ObjectIdentity('IF-MIB', 'ifDescr'),
       'Type' : ObjectIdentity('IF-MIB', 'ifType'),
       'Address' : ObjectIdentity('IF-MIB', 'ifPhysAddress'),
       'Class' : ObjectIdentity('ENTITY-MIB', 'entPhysicalClass'),
       'Status' : ObjectIdentity('1.3.6.1.2.1.2.2.1.7'),
       'ifIndex' : ObjectIdentity('1.3.6.1.2.1.2.2.1.1'),
       'ifInOctets' : ObjectIdentity('1.3.6.1.2.1.2.2.1.10'),
       'ifOutOctets' : ObjectIdentity('1.3.6.1.2.1.2.2.1.16'),
       'ifInDiscards' : ObjectIdentity('1.3.6.1.2.1.2.2.1.13'),
       'ifOutDiscards' : ObjectIdentity('1.3.6.1.2.1.2.2.1.19'),
       'ifInErrors' : ObjectIdentity('1.3.6.1.2.1.2.2.1.14'),
       'ifOutErrors' : ObjectIdentity('1.3.6.1.2.1.2.2.1.20'),
       'ifInUnknownProtos' : ObjectIdentity('1.3.6.1.2.1.2.2.1.15'),
       'ifSpeed' : ObjectIdentity('1.3.6.1.2.1.2.2.1.5'),
       'dellNetSysIfName' : ObjectIdentity('1.3.6.1.2.1.31.1.1.1.1'),
     },
     NSeriesCompEnum.dellNetFanTray : {
       'dellNetFanDeviceIndex' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.6.1.1"),
       'PiecePartID' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.5"), 
       'Type' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.6.1.2"),
       'ExpressServiceCode' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.8"),
       'PPIDRevision' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.6"), 
       'ServiceTag' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.7.1.7"), 
       'OperStatus' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.6.1.3"),
       'Speed' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.6.1.4"),
     },
     NSeriesCompEnum.dellNetFan: {
       'envMonFanStatusIndex': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.1"),
       'envMonFanStatusDescr': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.2"),
       'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.3"),
       'envMonFanSpeed': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.1.1.4"),
     },
     NSeriesCompEnum.dellNetPowerSupply : {
       'envMonSupplyStatusIndex' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.1"),
       'OperStatus' : ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.3"),
       'envMonSupplyStatusDescr': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.2"),
       'envMonSupplySource': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.4"),
       'envMonSupplyCurrentPower': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.5"),
       'envMonSupplyAveragePower': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.6"),
       'envMonSupplyAvgStartTime': ObjectIdentity("1.3.6.1.4.1.674.10895.3000.1.2.110.7.2.1.7"),
     },
     NSeriesCompEnum.dellNetPowerSupplyTray: {
       'dellNetPowerDeviceIndex': ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.7.1.1"),
       'OperStatus': ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.7.1.3"),
       'Type': ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.43.1.7.1.2"),
     },
     NSeriesCompEnum.dellNetProcessor : {
       'DeviceType' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.1"), 
       'Module' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.4"), 
       'Index' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.3"),
       'UpTime' : ObjectIdentity("1.3.6.1.4.1.6027.3.26.1.4.3.1.5"), 
       'MemSize' : ObjectIdentity("1.3.6.1.4.1.674.10895.5000.2.6132.1.1.1.1.4.2")
     },
    }
    NSeriesSNMPViews_FieldSpec = {
        NSeriesCompEnum.System : {
            "PrimaryStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "3" : "Healthy",
                    "4" : "Warning",
                    "5" : "Critical"
                }
            },
            "Model" : {
                'Lookup'  :  'True',
                'Values' : {
			"1" : "e1200", 
			"2" : "e600", 
			"3" : "e300", 
			"4" : "e150", 
			"5" : "e610", 
			"6" : "c150", 
			"7" : "c300", 
			"8" : "e1200i", 
			"9" : "s2410cp", 
			"10" : "s2410p", 
			"11" : "s50", 
			"12" : "s50e", 
			"13" : "s50v", 
			"14" : "s50nac", 
			"15" : "s50ndc", 
			"16" : "s25pdc", 
			"17" : "s25pac", 
			"18" : "s25v", 
			"19" : "s25n", 
			"20" : "s60", 
			"21" : "s55", 
			"22" : "s4810", 
			"23" : "s6410", 
			"24" : "z9000", 
			"25" : "m-MXL", 
			"26" : "m-IOA", 
			"27" : "s4820", 
			"28" : "s6000", 
			"29" : "s5000", 
			"30" : "s-FN410S-IOA", 
			"31" : "s-FN410T-IOA", 
			"32" : "s-FN2210S-IOA", 
			"33" : "z9500", 
			"34" : "c9010", 
			"35" : "c1048p", 
			"36" : "s4048on", 
			"37" : "s4810on", 
			"38" : "s6000on", 
			"39" : "s3048on", 
			"40" : "z9100", 
			"41" : "s6100", 
			"42" : "s3148p", 
			"43" : "s3124p", 
			"44" : "s3124f", 
			"45" : "s3124", 
			"46" : "s3148", 
			"47" : "s4048ton", 
			"48" : "s6010", 
			"49" : "n2048p", 
			"50" : "n2024p", 
			"51" : "n2024", 
			"52" : "n2048", 
			"53" : "n3048p", 
			"54" : "n3024p", 
			"55" : "n3024f", 
			"56" : "n3024", 
			"57" : "n3048"
                }
            },
            "NetwUMACAddress" : {
                'Macedit' : 'True'
                }
        },
        NSeriesCompEnum.dellNetPowerSupply : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Warning",
                    "3" : "Critical",
                    "4" : "Unknown",
                    "5" : "Absent",
                    "6" : "Critical"
                }
            },
            "envMonSupplySource" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "AC",
                    "3" : "DC",
                    "4" : "External PowerSupply",
                    "5" : "Internal Redundant",
                }
            }
        },
        NSeriesCompEnum.dellNetFanTray : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1": "Warning",
                    "2": "Healthy",
                    "3": "Critical",
                    "4": "Healthy",
                    "5": "Warning",
                    "6": "Critical",
                    "7": "Unknown"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
			"1" : "Chassis", 
			"2" : "Stack", 
			"3" : "RPM", 
			"4" : "Supervisor", 
			"5" : "Linecard", 
			"6" : "Port-extender" 
                }
            }
        },
        NSeriesCompEnum.dellNetPort : {
            "Status" : {
                'Lookup'  :  'True',
                'Values' : {
                    "up" : "Up",
                    "down" : "Down",
                    "testing" : "Testing"
                }
            }
        },
        NSeriesCompEnum.dellNetPowerSupplyTray : {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1": "Warning",
                    "2": "Healthy",
                    "3": "Critical",
                    "4": "Healthy",
                    "5": "Warning",
                    "6": "Critical",
                    "7": "Unknown"
                }
            },
            "Type" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Unknown",
                    "2" : "AC",
                    "3" : "DC"
                }
            }
        },
        NSeriesCompEnum.dellNetFan: {
            "OperStatus" : {
                'Lookup'  :  'True',
                'Values' : {
                    "1" : "Healthy",
                    "2" : "Warning",
                    "3" : "Critical",
                    "4" : "Unknown",
                    "5" : "Absent",
                    "6" : "Critical"
                }
            }
        },
        NSeriesCompEnum.dellNetProcessor : {
            "MemSize" : { 'Type' : 'Bytes' , 'InUnits' : 'MB', 'OutUnits' : 'GB' },
            "Module" : {
                'Lookup'  :  'True',
                'Values' : {
			"1" : "ControlProcessor", 
			"2" : "RoutingProcessor1", 
			"3" : "RoutingProcessor2", 
			"4" : "LinecardProcessor", 
			"5" : "RpmProcessor", 
			"6" : "RoutingProcessor" 
                }
            }
        }
    }

    # SNMPv2-SMI::enterprises\\.674\\.10895\\.3045 is added for N-Series switch

    NSeriesPSNMPClassifier = {
        NSeriesCompEnum.System : {
            'SysObjectID' : 'SNMPv2-SMI::enterprises\\.674\\.10895\\.3045'
        }
    }
else:
    NSeriesPSNMPViews = {}
    NSeriesPSNMPClassifier = {}

NSeriesComponentTree = {
    "Full" : [ 
        NSeriesCompEnum.System,
        NSeriesCompEnum.dellNetFanTray,
        NSeriesCompEnum.dellNetPowerSupply,
        NSeriesCompEnum.dellNetProcessor,
        NSeriesCompEnum.dellNetPort,
        NSeriesCompEnum.dellNetFan,
        NSeriesCompEnum.dellNetPowerSupplyTray
    ],
}

NSeriesClassifier = [ NSeriesCompEnum.System ]

NSeriesSubsystemHealthSpec = {
    NSeriesCompEnum.System : { "Component" : NSeriesCompEnum.System, "Field" : 'PrimaryStatus' },
}

class NSeries(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(NSeries, self).__init__(iDeviceRegistry("NSeries", srcdir, NSeriesCompEnum))
        else:
            super().__init__(iDeviceRegistry("NSeries", srcdir, NSeriesCompEnum))
        if PyPSNMP:
            self.protofactory.add(PSNMP(
                views = NSeriesPSNMPViews,
                classifier = NSeriesPSNMPClassifier,
                view_fieldspec = NSeriesSNMPViews_FieldSpec))
        self.protofactory.addCTree(NSeriesComponentTree)
        self.protofactory.addClassifier(NSeriesClassifier)
        self.protofactory.addSubsystemSpec(NSeriesSubsystemHealthSpec)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return NSeriesEntity(self.ref, protofactory, ipaddr, creds)

class NSeriesEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(NSeriesEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)


    def _isin(self, parentClsName, parent, childClsName, child):
        if 'MyPos' in parent:
            return parent['MyPos'] == child['ContainedIn']
        else:
            return self._get_obj_index(parentClsName, parent) in \
                   self._get_obj_index(childClsName, child)
    def _should_i_include(self, component, entry):
        if component in ["dellNetPort"]:
            if entry["Status"] == 'Testing':
                return False
        return True
