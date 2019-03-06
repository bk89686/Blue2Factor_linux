#!/usr/bin/env python

import sys
import json
import urllib
import urllib2


SERVER_ID="CHANGE_ME!"
endpoint = "https://secure.blue2factor.com/b2f-prox"
FAILURE = 1
SUCCESS = 0
def main(args=None):
    exitCode = FAILURE
    args = sys.argv
    if args is not None and len(args) > 2:
        if getProximityFromServer(args[1], args[2]):
            exitCode = SUCCESS
    else:
        sys.stdout.write("\n\n")
        sys.stdout.write("Make sure that the proper code has been added to ssh_config\n")
        sys.stdout.write("on your machine and to sshd_config on the server you're\n")
        sys.stdout.write("connecting to\n\n")
        sys.stdout.write("For assistence, contact your network administrator or visit\n")
        sys.stdout.write("www.blue2factor.com/ssh_setup\n")
        #just in case we need to override a failure
        if getProximityFromServer("", ""):
            exitCode = SUCCESS
    #sys.stdout.write("\n\nB2f exiting with code: " + str(exitCode) + "\n\n")
    sys.exit(exitCode)

def getProximityFromServer(token, devId):
    success = False
    success, reason = getUrlOutcome(endpoint, token, devId)
    if not success:
        if reason != None and reason != "":
            sys.stdout.write("Blue2Factor failed with reason: \"" + reason + "\"\n")
        else:
            sys.stdout.write("Blue2Factor authentication failed.");
    elif reason != "":
        sys.stdout.write(str(reason) + "\n")
    return success

def getUrlOutcome(url, token, devId):
    success = False
    reason = ""
    #sys.stdout.write("retrieving: " + url + "\n")
    params = {'tok' : token, 'coId' : SERVER_ID, 'b2fbe' : 'svr', 'dId' : devId}
    try:
        data = urllib.urlencode(params)
        opener = urllib2.build_opener()
        f = opener.open(url, data=data)
        jsonStr = f.read()
        jsonDict = json.loads(jsonStr)
        if jsonDict is not None:
            result = jsonDict["result"];
            if result is not None:
                success = int(result["outcome"]) == 1
                reason = result["reason"]
    except urllib2.HTTPError as e:
        reason = str(e)
        sys.stdout.write(str(e) + "\n\n")
    except Exception as ex:
        reason = str(ex)
        sys.stdout.write(str(ex) + "\n\n")
    return success, reason

if __name__ == '__main__':
    main()