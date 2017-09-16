from argparse import ArgumentParser
from omsdk.sdkfile import LocalFile
from omsdk.sdkcenum import TypeHelper
from omsdk.catalog.sdkupdatemgr import UpdateManager
from omdrivers.helpers.iDRAC.UpdateHelper import UpdateHelper
from omsdk.sdkinfra import sdkinfra
from omsdk.sdkcreds import UserCredentials
from omsdk.sdkprint import PrettyPrint
import sys

def CompareInventory(arglist):
    parser = ArgumentParser(description='Compare Inventory')
    #parser.add_argument('-u', '--user', 
    #    action="store", dest="user", type=str, nargs='?',
    #    default='root', help="Username to use for iDRAC")
    #parser.add_argument('-p', '--password', 
    #    action="store", dest="password", type=str,
    #    default='calvin', help="Password to use for iDRAC")
    #parser.add_argument('-i', '--ipaddress',
    #    action="store", dest="idrac_ip", nargs='+',
    #    help="ipaddress of iDRAC")
    parser.add_argument('-f', '--folder', 
        action="store", dest="folder", type=str,
        help="folder from where inventory is serialized")
    parser.add_argument('-C', '--catalog', 
        action="store", dest="catalog", type=str, nargs='?',
        default='Catalog', help="Catalog to load")

    options = parser.parse_args(arglist)

    #if options.password is None:
    #    print("password must be provided")
    #    return -1
    #if options.user is None:
    #    print("user must be provided")
    #    return -1
    #if options.idrac_ip is None or len(options.idrac_ip) <= 0:
    #    print("iDRAC ip addresses must be provided")
    #    return -1
    if options.folder is None:
        print("Folder must be provided")
        return -1
    if options.catalog is None:
        options.catalog = 'Catalog'


    updshare = LocalFile(local = options.folder, isFolder=True)
    if not updshare.IsValid:
        print("Folder is not writable!")
        return -2

    print("Configuring Update Share...")
    UpdateManager.configure(updshare)
    print("Retrieving Firmware Inventory...")
    rjson = UpdateHelper.get_firmware_inventory()
    dev_fw = {}
    if rjson['Status'] == 'Success':
        dev_fw= rjson['retval']

    updmgr = UpdateManager.get_instance()
    (ignore, cache_cat) = updmgr.getCatalogScoper(options.catalog)
    devcompare = {}
    for dev in dev_fw:
        swidentity = dev_fw[dev]
        retval = cache_cat.compare(swidentity['Model_Hex'], swidentity)
        devcompare[dev] = []
        for firm in swidentity['Firmware']:
            fwcompare = {}
            if 'Catalog.vendorVersion' not in firm:
                fwcompare['FQDD'] = firm['FQDD']
                fwcompare['ElementName'] = firm['ElementName']
                fwcompare['UpdatePackage'] = 'Absent'
                fwcompare['UpdateNeeded'] = False
                fwcompare['UpdateType'] = ''
            elif 'VersionString' not in firm:
                fwcompare['FQDD'] = firm['FQDD']
                fwcompare['ElementName'] = firm['ElementName']
                fwcompare['Catalog.vendorVersion']=firm['Catalog.vendorVersion']
                fwcompare['UpdatePackage'] = 'Present'
                fwcompare['UpdateNeeded'] = True
                fwcompare['UpdateType'] = 'New'
            elif firm['VersionString'] == firm['Catalog.vendorVersion']:
                fwcompare['FQDD'] = firm['FQDD']
                fwcompare['ElementName'] = firm['ElementName']
                fwcompare['Catalog.vendorVersion']=firm['Catalog.vendorVersion']
                fwcompare['VersionString']=firm['VersionString']
                fwcompare['UpdatePackage'] = 'Present'
                fwcompare['UpdateNeeded'] = False
                fwcompare['UpdateType'] = 'None'
            elif firm['VersionString'] > firm['Catalog.vendorVersion']:
                fwcompare['FQDD'] = firm['FQDD']
                fwcompare['ElementName'] = firm['ElementName']
                fwcompare['Catalog.vendorVersion']=firm['Catalog.vendorVersion']
                fwcompare['VersionString']=firm['VersionString']
                fwcompare['UpdatePackage'] = 'Present'
                fwcompare['UpdateNeeded'] = True
                fwcompare['UpdateType'] = 'Downgrade'
            else:
                fwcompare['FQDD'] = firm['FQDD']
                fwcompare['ElementName'] = firm['ElementName']
                fwcompare['Catalog.vendorVersion']=firm['Catalog.vendorVersion']
                fwcompare['VersionString']=firm['VersionString']
                fwcompare['UpdatePackage'] = 'Present'
                fwcompare['UpdateNeeded'] = True
                fwcompare['UpdateType'] = 'Upgrade'
            devcompare[dev].append(fwcompare)
    print(PrettyPrint.prettify_json(devcompare))

if __name__ == "__main__":
    CompareInventory(sys.argv[1:])
