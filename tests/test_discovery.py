from wsdiscovery import WSDiscovery
from onvif import ONVIFCamera, ONVIFError
import urllib.parse

"""
pip install --upgrade onvif_zeep

"""

try_auth = [
    ('admin', 'admin'),
    ('test', 'test'),
]

wsd = WSDiscovery()
wsd.start()

seen_services = []

services = wsd.searchServices()
for service in services:
    print(service.getEPR() + ":" + service.getXAddrs()[0])
    if service.getXAddrs()[0] in seen_services:
        continue
        
    seen_services.append(service.getXAddrs()[0])
    parsed = urllib.parse.urlparse(service.getXAddrs()[0])
    parts =  parsed.netloc.split(':')
    ip = parts[0]
    if len(parts) > 1:
        port = parts[1]
    else:
        port = 80
        
    for authinfo in try_auth:
        try:
            print("Trying ONVIFCamera({ip}, {port}, {user}, {passwd})".format(
                ip=ip, port=port, user=authinfo[0], passwd=authinfo[1]))
            mycam = ONVIFCamera(ip, port, authinfo[0], authinfo[1])
        except ONVIFError as e:
            print("Got error {}".format(e))
            continue
    
        print("=> Scopes:")
        scopes = service.getScopes()
        for scope in scopes:
            print("  {}({})".format(type(scope),repr(scope)))

        print("=> Streams:")
        media_service = mycam.create_media_service()
        profiles = media_service.GetProfiles()
        for profile in profiles:
            try:
                params = media_service.create_type('GetStreamUri')
                params.ProfileToken = profile.token
                params.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}
                resp = media_service.GetStreamUri(params)
                print("~~~~~~~~~> resp: ", resp)
                print("  {}".format(resp.Uri))
            except ONVIFError as e:
                print("Got error {} from GetStreamUri({})".format(e, params))
                continue

        break
            
wsd.stop()
