from omsdk.sdkcenum import EnumWrapper
import logging

logger = logging.getLogger(__name__)

BootScanSelectionTypes = EnumWrapper("BootScanSelectionTypes", {
    "Disabled" : "Disabled",
    "FabricDiscovered" : "FabricDiscovered",
    "FirstLUN" : "FirstLUN",
    "FirstLUN0" : "FirstLUN0",
    "FirstNOTLUN0" : "FirstNOTLUN0",
    "SpecifiedLUN" : "SpecifiedLUN",
}).enum_type

FCTapeTypes = EnumWrapper("FCTapeTypes", {
    "Disabled" : "Disabled",
    "Enabled" : "Enabled",
}).enum_type

FramePayloadSizeTypes = EnumWrapper("FramePayloadSizeTypes", {
    "Auto" : "Auto",
    "T_1024" : "1024",
    "T_2048" : "2048",
    "T_2112" : "2112",
    "T_512" : "512",
}).enum_type

HardZoneTypes = EnumWrapper("HardZoneTypes", {
    "Disabled" : "Disabled",
    "Enabled" : "Enabled",
}).enum_type

PortSpeedTypes = EnumWrapper("PortSpeedTypes", {
    "Auto" : "Auto",
    "T_16G" : "16G",
    "T_1G" : "1G",
    "T_2G" : "2G",
    "T_32G" : "32G",
    "T_4G" : "4G",
    "T_8G" : "8G",
}).enum_type

