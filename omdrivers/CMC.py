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
from enum import Enum
from omsdk.sdkdevice import iDeviceRegistry, iDeviceDriver, iDeviceDiscovery
from omsdk.sdkdevice import iDeviceTopologyInfo
from omsdk.sdkproto import PWSMAN
from omsdk.sdkcenum import EnumWrapper, TypeHelper
from omsdk.sdkprint import PrettyPrint
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3


# MessageID, Message
CMCCompEnum = EnumWrapper("CMCCompEnum", {
    "System" : "System",
    "ComputeModule" : "ComputeModule",
    "StorageModule" : "StorageModule",
    "IOModule" : "IOModule",
    "Fan" : "Fan",
    "CMC" : "CMC",
    "PowerSupply" : "PowerSupply",
    "Controller" : "Controller",
    "Enclosure" : "Enclosure",
    "EnclosureEMM" : "EnclosureEMM",
    "EnclosurePSU" : "EnclosurePSU",
    "PCIDevice" : "PCIDevice",
    "ControllerBattery" : "ControllerBattery" ,
    "VirtualDisk" : "VirtualDisk",
    "PhysicalDisk" : "PhysicalDisk",
    "KVM" : "KVM",
    "BladeSlot" : "BladeSlot",
    "License" : "License",
    "Slots_Summary" : "Slots_Summary"
    }).enum_type

CMCMiscEnum = EnumWrapper("CMCMiscEnum", {
    "PassThroughModule" : "PassThroughModule",
    "PSPackage" : "PSPackage",
    "PSSlot" : "PSSlot",
    "PCISlot" : "PCISlot",
    "FanPackage" : "FanPackage",
    "FanSlot" : "FanSlot"
    }).enum_type

CMCLogsEnum = EnumWrapper("CMCLogEnum", {
    "Logs" : "Logs",
    }).enum_type

CMCJobsEnum = EnumWrapper("CMCJobEnum", {
    "Jobs" : "Jobs",
    }).enum_type

CMCFirmEnum = EnumWrapper("CMCFirmEnum", {
    "Firmware" : "Firmware",
    }).enum_type

CMCComponentTree = {
    CMCCompEnum.System : [
        CMCCompEnum.IOModule,
        CMCCompEnum.Fan,
        CMCCompEnum.CMC,
        CMCCompEnum.PowerSupply,
        CMCCompEnum.PCIDevice,
        CMCCompEnum.ComputeModule,
        CMCCompEnum.Slots_Summary,
        "Storage"
    ],
    "Storage" : [
        CMCCompEnum.Controller
    ],
    CMCCompEnum.Controller : [
        CMCCompEnum.Enclosure,
        CMCCompEnum.ControllerBattery,
        CMCCompEnum.VirtualDisk,
        CMCCompEnum.PhysicalDisk
    ],
    CMCCompEnum.VirtualDisk : [
        CMCCompEnum.PhysicalDisk
    ],
    CMCCompEnum.Enclosure : [
        CMCCompEnum.EnclosureEMM,
        CMCCompEnum.EnclosurePSU,
        CMCCompEnum.PhysicalDisk
    ]
}

CMCWsManViews = {
    CMCCompEnum.System: "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ModularChassisView",
    CMCCompEnum.ComputeModule : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_BladeServerView",
    CMCCompEnum.StorageModule : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_StorageSledView",
    CMCCompEnum.Fan : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_Fan",
    CMCMiscEnum.FanPackage : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_FanPackage",
    CMCMiscEnum.FanSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_FanSlot",
    CMCCompEnum.PCIDevice : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_ChassisPCIDeviceView",
    CMCMiscEnum.PCISlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_ChassisPCISlot",
    CMCCompEnum.CMC : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_ChMgrPackage",
    CMCCompEnum.IOModule : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_IOMPackage",
    CMCMiscEnum.PassThroughModule : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PassThroughModule",
    CMCCompEnum.PowerSupply : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PowerSupply",
    CMCMiscEnum.PSPackage : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PSPackage",
    CMCMiscEnum.PSSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_PSSlot",
    CMCFirmEnum.Firmware : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_SoftwareIdentity",
    CMCJobsEnum.Jobs : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob",
    CMCLogsEnum.Logs : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_HWLogEntry",
    CMCCompEnum.Controller : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerView",
    CMCCompEnum.EnclosureEMM : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureEMMView",
    CMCCompEnum.EnclosurePSU : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosurePSUView",
    CMCCompEnum.Enclosure : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_EnclosureView",
    CMCCompEnum.ControllerBattery : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_ControllerBatteryView",
    CMCCompEnum.VirtualDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_VirtualDiskView",
    CMCCompEnum.PhysicalDisk : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_PhysicalDiskView",
    CMCCompEnum.KVM : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_KVM",
    CMCCompEnum.BladeSlot : "http://schemas.dell.com/wbem/wscim/1/cim-schema/2/Dell_BladeSlot",
    CMCCompEnum.License : "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_License"
}

CMCWsManCmds = { }
CMCWsManCompMap = { }

CMCUnionCompSpec = {
   "Slots_Summary":{
        "_components": [
            "ComputeModule",
            "StorageModule"
        ],
        "_components_enum": [
            CMCCompEnum.ComputeModule,
            CMCCompEnum.StorageModule
        ],
        "_remove_duplicates" : False
   }
}

CMCMergeJoinCompSpec = {
   "Fan" : {
        "_components" : [
            ["Fan", "ClassId", "FanSlot", "ClassId"],
            ["Fan", "ClassId", "FanPackage", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.Fan,
            CMCMiscEnum.FanPackage,
            CMCMiscEnum.FanSlot
        ],
        "_overwrite" : False
   },
   "PowerSupply" : {
        "_components" : [
            ["PowerSupply", "ClassId", "PSPackage", "ClassId"],
            ["PowerSupply", "ClassId", "PSSlot", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.PowerSupply,
            CMCMiscEnum.PSPackage,
            CMCMiscEnum.PSSlot
        ],
        "_overwrite" : False
   },
   "IOModule" : {
        "_components" : [
            ["IOModule", "ClassId", "PassThroughModule", "ClassId"]
        ],
        "_components_enum": [
            CMCCompEnum.IOModule,
            CMCMiscEnum.PassThroughModule
        ],
        "_overwrite" : True
   },
   "PCIDevice" : {
        "_components" : [
            ["PCIDevice", "SlotFQDD", "PCISlot", "FQDD"]
        ],
        "_components_enum": [
            CMCCompEnum.PCIDevice,
            CMCMiscEnum.PCISlot
        ],
        "_overwrite" : False
   }
}
CMCWsManViews_FieldSpec = {
    CMCCompEnum.PowerSupply : {
        "HealthState":  {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        },
        "TotalOutputPower": {'UnitScale': '-3', 'UnitAppend': 'Watts'},
    },
    CMCCompEnum.Fan : {
        "HealthState":  {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        }
    },
    CMCMiscEnum.FanSlot : {
        "Number": {'Rename' : 'SlotNumber'}
    },
    CMCCompEnum.KVM : {
        "HealthState":  {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "5" : "Healthy",
                "10" : "Warning", "15" : "Warning",
                "20": "Critical", "25" : "Critical", "30" : "Critical"
            }
        }
    },
    CMCMiscEnum.PSPackage : {
        "Tag":  { 'Rename' : 'PSPackage_Tag' }
    },
    CMCMiscEnum.PSSlot : {
        "Tag":  { 'Rename' : 'PSSlot_Tag' },
        "Number" : {'Rename' : 'Slot'}
    },
    CMCCompEnum.PhysicalDisk : {
        "SizeInBytes" : { 'Rename' : 'Capacity', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "FreeSizeInBytes" : { 'Rename' : 'FreeSpace', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "UsedSizeInBytes" : { 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "MediaType":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Hard Disk Drive",
                "1" : "Solid State Drive"
            }
        },
        "BusProtocol":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "SCSI", "2" : "PATA", "3" : "FIBRE", "4" : "USB", "5" : "SATA", "6" : "SAS"
            }
        },
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "SecurityState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Not Capable", "1" : "Secured", "2" : "Locked", "3" : "Foreign", "4" : "Encryption Capable", "5" : "Unknown"
            }
        },
        "PredictiveFailureState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Healthy", "1" : "Warning"
            }
        }
    },
    CMCCompEnum.VirtualDisk : {
        "SizeInBytes" : { 'Rename' : 'Capacity', 'Type' : 'Bytes' , 'InUnits' : 'B' , 'OutUnits' : 'GB'},
        "RAIDTypes":  {
            'Lookup' : 'True',
            'Values' : {
                "1" : "No RAID",
                "2" : "RAID0",
                "4" : "RAID1",
                "64" : "RAID5",
                "128" : "RAID6",
                "2048" : "RAID10",
                "8192" : "RAID50",
                "16384" : "RAID60"
            }
        },
        "MediaType":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown",
                "1" : "Magnetic Drive",
                "2" : "Solid State Drive"
            }
        },
        "BusProtocol":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "SCSI", "2" : "PATA", "3" : "FIBRE", "4" : "USB", "5" : "SATA", "6" : "SAS"
            }
        },
        "StripeSize":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Default", "1" : "512B", "2" : "1KB", "4" : "2KB", "8" : "4KB", "16" : "8KB",
                "32" : "16KB", "64" : "32KB", "128" : "64KB", "256" : "128KB", "512" : "256KB",
                "1024" : "512KB", "2048" : "1MB", "4096" : "2MB", "8192" : "4MB", "16384" : "8MB", "32768" : "16MB"
            }
        },
        "ReadCachePolicy":  {
            'Lookup' : 'True',
            'Values' : {
                 "0" : "Unknown", "16" : "No Read Ahead", "32" : "Read Ahead", "64" : "Adaptive Read Ahead"
            }
        },
        "WriteCachePolicy":  {
            'Lookup' : 'True',
            'Values' : {
                "0" : "Unknown", "1" : "Write Through", "2" : "Write Back", "4" : "Write Back Force"
            }
        }
    },
    CMCCompEnum.License : {
        "LicenseType":  {
            'Lookup' : 'True',
            'Values' : {
                "1" : "Perpertual", "2" : "Leased", "3" : "Evaluation", "4" : "Site"
            }
        }
    },
    CMCCompEnum.PCIDevice : {
        "PowerStateStatus":  {
            'Lookup' : 'True',
            'Values' : {
                "2" : "On", "3" : "Off"
            }
        },
        "DataBusWidth":  {
            'Lookup' : 'True',
            'Values' : {
                "0001" : "Other", 
                "0002" : "Unknown",
                "0003" : "8 bit",
                "0004" : "16 bit",
                "0005" : "32 bit",
                "0006" : "64 bit",
                "0007" : "128 bit",
                "0008" : "1x or x1",
                "0009" : "2x or x2",
                "000A" : "4x or x4",
                "000B" : "8x or x8",
                "000C" : "12x or x12",
                "000D" : "16x or x16",
                "000E" : "32x or x32"
            }
        }
    },
    CMCCompEnum.Controller : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "PatrolReadState" : {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Stopped", "2" : "Running"
            }
        },
        "SecurityStatus" : {
            'Lookup': 'True',
            'Values': {
                #MOF-Diff
                "0" : "Unknown", "1" : "Encryption Capable", "2" : "Security Key Assigned"
            }
        },
        'SlicedVDCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "Not Supported", "1" : "Supported"
            }
        },
        'CachecadeCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "Not Supported", "1" : "Supported"
            }
        },
        'EncryptionMode' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "None", "1" : "Local Key Management",
                    "2" : "Dell Key Management", "3" : "Pending Dell Key Management"
            }
        },
        'EncryptionCapability' : {
            'Lookup': 'True',
            'Values' : {
                    "0" : "None", "1" : "Local Key Management Capable",
                    "2" : "Dell Key Management Capable", "3" : "Pending Dell Key Management Capable"
            }
        },
        'DeviceCardSlotLength' : {
            'Lookup': 'True',
            'Values' : {
                    "3" : "Short", "4" : "Long"
            }
        },
        "CacheSizeInMB" : { 'Type' : 'Bytes' , 'InUnits' : 'MB' , 'OutUnits' : 'MB'}
    },
    CMCCompEnum.Enclosure : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical", "0x8000" :"Warning", "0xFFFF" : "Warning"
            }
        },
        "WiredOrder" :  { 'Rename' : 'BayID' }
    },
    CMCMiscEnum.PassThroughModule :{
        "LinkTechnologies": {
            'Lookup': 'True',
            'Values': {
                "0" :   "Unknown",
                "1" : "Other",
                "2" :  "Ethernet",
                "3" :  "IB",
                "4" :  "FC",
                "5" :  "FDDI",
                "6" :  "ATM",
                "7" :  "Token Ring",
                "8" :  "Frame Relay",
                "9" :  "Infrared",
                "10" :  "BlueTooth",
                "11" :  "Wireless LAN"
            }
        }
    },
    CMCCompEnum.IOModule : {
        "PrimaryStatus": {
            'Lookup': 'True',
            'Values': {
                "0" : "Unknown", "1" : "Healthy", "2" : "Warning", "3" : "Critical"
            }
        }
    },
    CMCCompEnum.ComputeModule: {
        "PowerState": {
            'Lookup': 'True',
            'Values': {
                "1": "Other", "2": "Power On", "6": "Power Off"
            }
        }
    }
}

CMCSubsystemHealthSpec = {
    CMCCompEnum.CMC : { "Component" : CMCCompEnum.System, "Field" : 'PrimaryStatus' },
    CMCCompEnum.IOModule : { "Component" : CMCCompEnum.System, "Field" : 'IOMRollupStatus' },
    CMCCompEnum.ComputeModule : { "Component" : CMCCompEnum.System, "Field" : 'BladeRollupStatus' },
    'Storage' : { "Component" : CMCCompEnum.System, "Field" : 'ChassisStorageRollupStatus' },
    CMCCompEnum.PowerSupply : { "Component" : CMCCompEnum.System, "Field" : 'PSRollupStatus' },
    CMCCompEnum.KVM : { "Component" : CMCCompEnum.System, "Field" : 'KVMRollupStatus' },
    CMCCompEnum.Fan : { "Component" : CMCCompEnum.System, "Field" : 'FanRollupStatus' },
    CMCCompEnum.StorageModule : { "Component" : CMCCompEnum.System, "Field" : 'StorageSledRollupStatus' }
    #ChassisTempRollupStatus
}

class CMC(iDeviceDiscovery):
    def __init__(self, srcdir):
        if PY2:
            super(CMC, self).__init__(iDeviceRegistry("CMC", srcdir, CMCCompEnum))
        else:
            super().__init__(iDeviceRegistry("CMC", srcdir, CMCCompEnum))
        self.protofactory.add(PWSMAN(
            selectors = {"__cimnamespace" : "root/dell/cmc" },
            views = CMCWsManViews,
            view_fieldspec = CMCWsManViews_FieldSpec,
            cmds = CMCWsManCmds,
            compmap = CMCWsManCompMap
        ))
        self.protofactory.addClassifier([CMCCompEnum.System])
        self.protofactory.addCTree(CMCComponentTree)
        self.protofactory.addSubsystemSpec(CMCSubsystemHealthSpec)

    def my_entitytype(self, pinfra, ipaddr, creds, protofactory):
        return CMCEntity(self.ref, protofactory, ipaddr, creds)

class CMCEntity(iDeviceDriver):
    def __init__(self, ref, protofactory, ipaddr, creds):
        if PY2:
            super(CMCEntity, self).__init__(ref, protofactory, ipaddr, creds)
        else:
            super().__init__(ref, protofactory, ipaddr, creds)
        self.comp_merge_join_spec = CMCMergeJoinCompSpec
        self.comp_union_spec = CMCUnionCompSpec

    def my_fix_obj_index(self, clsName, key, js):
        retval = None
        if clsName == "System":
            if 'ServiceTag' not in js or js['ServiceTag'] is None:
                js['ServiceTag'] = self.ipaddr
            retval = js['ServiceTag']
        if retval is None:
            retval = self.ipaddr + "cmc_null"
        return retval

    def _isin(self, parentClsName, parent, childClsName, child):
        if TypeHelper.resolve(parentClsName) == "Controller" and \
           TypeHelper.resolve(childClsName) == "PhysicalDisk" and \
           ("Disk.Direct" not in self._get_obj_index(childClsName, child)):
           return False
        if TypeHelper.resolve(parentClsName) == "VirtualDisk" and \
           TypeHelper.resolve(childClsName) == "PhysicalDisk":
            if 'PhysicalDiskIDs' in parent:
                parentdiskListStr = parent['PhysicalDiskIDs'].strip("[]")
                diskids = parentdiskListStr.split(',')
                for d in diskids:
                    fd = d.strip().strip("'")
                    # print("FD is ",fd, " VD ",self._get_obj_index(childClsName,child))
                    if fd == self._get_obj_index(childClsName,child):
                        return True
            else:
                return False
        return self._get_obj_index(parentClsName, parent) in \
               self._get_obj_index(childClsName, child)

    def get_idrac_ips(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return self._get_field_device_for_all(self.ComponentEnum.ComputeModule, "IPv4Address")

    def _get_topology_info(self):
        self.get_partial_entityjson(self.ComponentEnum.ComputeModule)
        return CMCTopologyInfo(self.get_json_device())

    def _get_topology_influencers(self):
        return { 'System' : [ 'Model' ],
                 'ComputeModule' : [ 'ServiceTag' ] }

    def _should_i_include(self, component, entry):
        if component == "ComputeModule":
            # print("IN SHOULD I Include")
            bladeslot = self.entityjson["ComputeModule"]
            st_dict = {}
            slt_ndict = {}
            breakflag = False
            for slot in bladeslot:
                if 'FormFactor' in slot or 'ExtensionSlot' in slot:
                    breakflag = True
                    break #This is avoid repetition of logic for each Blade
                slt_ndict.setdefault(slot['ServiceTag'], []).append(slot['SlotNumber'])
                if slot['ServiceTag'] in st_dict:
                    st_dict[slot['ServiceTag']] = st_dict[slot['ServiceTag']] + 1
                else:
                    st_dict[slot['ServiceTag']] = 1
                if (not slot['SubSlot']) or (slot['SubSlot'] == "NA"):
                    slot['FormFactor'] = 'Half length Blade'
                else:
                    slot['FormFactor'] = 'Quarter length Blade'
                if slot['MasterSlotNumber'] != slot['SlotNumber']:
                    slot['ExtensionSlot'] = slot['SlotNumber']
                    slot['FormFactor'] = 'Full length Blade'
            for slot in bladeslot:
                if breakflag:
                    break
                if st_dict[slot['ServiceTag']] > 1:
                    slot['FormFactor'] = 'Full length Blade'
                    # if not 'ExtensionSlot' in slot:
                        # slot['SlotNumber'] = slot['SlotNumber'] + "/" + str(int(slot['SlotNumber'])+slotArch)
                    slot['SlotNumber'] = "/".join(sorted(slt_ndict[slot['ServiceTag']],key=int))
                if 'FormFactor' in slot:
                    if 'Quarter' in slot['FormFactor']:
                        slot['SlotNumber'] = slot['SlotNumber'] + slot['SubSlot']

        if component == "Slots_Summary":
            cmcmodel = self.entityjson['System'][0]["Model"]
            # print("SLOTS of ",cmcmodel)
            if 'FX2' in cmcmodel:
                slotArch = 1
                freeslots = set(range(1,5))
            if 'VRTX' in cmcmodel:
                slotArch = 2
                freeslots = set(range(1, 5))
            if 'M1000e' in cmcmodel:
                slotArch = 8
                freeslots = set(range(1,17))

            # print(freeslots)
            occupiedSlots = set()
            extensionSlots = set()
            bladeslot = self.entityjson["Slots_Summary"]
            for slot in bladeslot:
                if 'StorageMode' in slot:#this is a Sled
                    sledslot = int(slot['FQDD'][-2:])
                    # print("Sledslot ",sledslot)
                    freeslots.remove(sledslot)
                    occupiedSlots.add(sledslot)
                else:#this is a blade
                    if 'FormFactor' in slot:
                        if 'Full' in slot['FormFactor']:
                            if 'ExtensionSlot' in slot:
                                freeslots.remove(int(slot['ExtensionSlot']))
                                extensionSlots.add(int(slot['ExtensionSlot']))
                            else:
                                freeslots.remove(int(slot['MasterSlotNumber']))
                                occupiedSlots.add(int(slot['MasterSlotNumber']))
                        if 'Half' in slot['FormFactor']:
                            freeslots.remove(int(slot['MasterSlotNumber']))
                            occupiedSlots.add(int(slot['MasterSlotNumber']))

            quarterSlotdict = {'a' : 'b','b' : 'a','c' : 'd','d' : 'c'}
            extSlotIndicator = {'a' : False,'b' : False,'c' : True,'d' : True}
            for slot in bladeslot:
                if 'FormFactor' in slot:
                    if 'Quarter' in slot['FormFactor']:
                        slotModifier = 0
                        if extSlotIndicator[slot['SubSlot']]:
                            slotModifier = slotArch
                        extSlot = int(slot['MasterSlotNumber']) + slotModifier
                        if extSlot in freeslots:
                            freeslots.remove(extSlot)
                        qSlot = slot['MasterSlotNumber'] + slot['SubSlot']
                        if qSlot in freeslots:
                            freeslots.remove(qSlot)
                        occupiedSlots.add(qSlot)
                        otherslot = slot['MasterSlotNumber'] + quarterSlotdict[slot['SubSlot']]
                        if otherslot not in occupiedSlots:
                            freeslots.add(otherslot)

            Slot_Summary = {}
            # Slot_Summary['Key'] = 'Slot_Summary'
            if freeslots:
                Slot_Summary['FreeSlots'] = ",".join(str(x) for x in freeslots)
            else:
                Slot_Summary['FreeSlots'] = "Chassis is fully occupied"
            if occupiedSlots:
                Slot_Summary['OccupiedSlots'] = ",".join(str(x) for x in occupiedSlots)
            else:
                Slot_Summary['OccupiedSlots'] = "Chassis is empty"
            if extensionSlots:
                Slot_Summary['ExtensionSlots'] = ",".join(str(x) for x in extensionSlots)
            else:
                if occupiedSlots:
                    Slot_Summary['ExtensionSlots'] = "Chassis has only Half-length blades"
                else:
                    Slot_Summary['ExtensionSlots'] = "Chassis is empty"

            for slot in bladeslot:
                slot.update(Slot_Summary)

        if component == "StorageModule":
            if "StorageModule" in self.entityjson:
                storageslot = self.entityjson["StorageModule"]
                for slot in storageslot:
                    slot['SlotNumber'] = int(slot['FQDD'][-2:])
                    
        return True

    def _should_i_modify_component(self, finalretjson, component):
        # print("IN MODIFY COMP ",component)
        if component == 'ComputeModule':
            if "ComputeModule" in finalretjson:
                bladeslot = finalretjson['ComputeModule']
                newbladeList = []
                for slot in bladeslot:
                    if 'ExtensionSlot' in slot:
                        if slot['ExtensionSlot'] == "Not Available":
                            if 'Full' in slot['FormFactor']:
                                extslot = slot['SlotNumber'].split('/')
                                slot['ExtensionSlot'] = extslot[1]
                            newbladeList.append(slot)
                if newbladeList:
                    del finalretjson["ComputeModule"]
                    finalretjson['ComputeModule'] = newbladeList

        if component == "Slots_Summary":
            if "Slots_Summary" in finalretjson:
                bladeslot = finalretjson["Slots_Summary"]
                slot_summary = {}
                slotTypes = ['FreeSlots', 'OccupiedSlots', 'ExtensionSlots']
                for slot in bladeslot:
                    if not slot_summary:
                        slot_summary['Key'] = 'SlotSummary'
                        for slotType in slotTypes:
                            if slotType in slot:
                                slot_summary[slotType] = slot[slotType]
                        slot_summary['InstanceID'] = 'SlotSummary'
                    else:
                        break

                del finalretjson["Slots_Summary"]
                finalretjson['Slots_Summary'] = []
                finalretjson['Slots_Summary'].append(slot_summary)

class CMCTopologyInfo(iDeviceTopologyInfo):
    def __init__(self, json):
        if PY2:
            super(iDeviceTopologyInfo, self).__init__('CMC', json)
        else:
            super().__init__('CMC', json)

    def my_static_groups(self, tbuild):
        tbuild.add_group('Dell', static=True)
        tbuild.add_group('Dell Chassis', 'Dell', static=True)

    def my_groups(self, tbuild):
        if 'Model' in self.system:
            fmgrp = self.system['Model']
            tbuild.add_group(fmgrp, 'Dell Chassis')
            self._add_myself(tbuild, fmgrp)

    def my_assoc(self, tbuild):
        if 'ComputeModule' not in self.json:
            return
        self._remove_assoc(tbuild, [self.mytype, self.system['Key']])
        for slot in self.json['ComputeModule']:
            self._add_assoc(tbuild,
                            [self.mytype, self.system['Key']],
                            ['ComputeModule', slot['Key']],
                            ['Server', slot['ServiceTag']])
