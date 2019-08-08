#!/usr/bin/env python

'''
    Created on Feb 28, 2019
    @author: cjm10
    '''

import sys
import os
import json
import urllib
try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote
import urllib2
from __builtin__ import False

endpoint = "https://secure.blue2factor.com/b2f-prox"
setupEndpoint = "https://secure.blue2factor.com/b2f-server-setup"
configFile = "b2f.config"
FAILURE = 1
SUCCESS = 0
TESTING = False

def main():
    exitCode = FAILURE
    args = sys.argv
    if args is not None and len(args) > 2:
        if getProximityFromServer(args[1], args[2]):
            exitCode = SUCCESS
    else:
        if len(args) == 2:
            prefix = args[1][:4]
            uuid = getServerUuidFromArg(args[1])
            print("uuid: " + uuid + ", pref: " + prefix)
            if prefix == "inst":
                if setup(uuid):
                    exitCode = SUCCESS
            elif prefix == "vali":
                if confirm(uuid):
                    exitCode = SUCCESS
            elif prefix == "dele":
                if delete(uuid):
                    exitCode = SUCCESS
        else:
            sys.stdout.write("not enough arguments: " + str(len(args)) + "\n\n")
            sys.stdout.write("Make sure that the proper code has been added to ssh_config\n")
            sys.stdout.write("on your machine and to sshd_config on the server you're\n")
            sys.stdout.write("connecting to\n\n")
            sys.stdout.write("For assistence, contact your network administrator or visit\n")
            sys.stdout.write("www.blue2factor.com/ssh_setup\n")
            #just in case we need to override a failure
            if getProximityFromServer("", ""):
                exitCode = SUCCESS
    sys.exit(exitCode)

def getServerUuidFromArg(arg):
    return arg[4:]

def writePublicKeyToFile(publicKey):
    keyFile = getBaseDir() + "/b2factor/keys/b2f.pem"
    f = open(keyFile, "w+")
    f.write("-----BEGIN PUBLIC KEY-----\n")
    f.write(publicKey)
    f.write("\n-----END PUBLIC KEY-----")
    f.close()

def delete(serverUuid):
    success, _ = getDeleteUrl(setupEndpoint, serverUuid)
    return success

def confirm(serverUuid):
    success, _ = getConfirmUrl(setupEndpoint, serverUuid)
    return success

def setup(serverUuid):
    success = False
    if (len(serverUuid)==36):
        success, pubKey = getSetupUrl(setupEndpoint, serverUuid)
        if success:
            writePublicKeyToFile(pubKey)
        else:
            sys.stdout.write("We could not verify that you entered the code into the Blue2Factor Admin Console.")
            if (pubKey is not None and pubKey != ""):
                sys.stdout.write("Error: " + pubKey)
    else:
        sys.stdout.write("Installation was unsuccessful - bad argument")
    return success

def getProximityFromServer(token, devId):
    success = False
    if len(token) > 19:
        success, reason = getUrlOutcome(endpoint, token, devId)
        if not success:
            sys.stdout.write("Blue2Factor failed with reason: \"" + reason + "\"\n")
        elif reason != "":
            sys.stdout.write(str(reason) + "\n")
    else:
        sys.stdout.write("invalid arg: " + token + "\n")
    return success

def getConfigVal(keyText):
    value = ""
    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    f = open(os.path.join(__location__, 'b2f.config'));
#    filePath = os.path.join(sys.path[0], 'b2f.config'
#    sys.stdout.write("opening " + str(os.path.join(__location__, 'b2f.config')) + "\n")
#    f = open(filePath, "r")
    for line in f:
        if "=" in line:
            lineSplit = line.split('=')
            if lineSplit[0] == keyText:
                value = lineSplit[1].rstrip()
#                sys.stdout.write("found: " + value)
                break
    f.close()
    return value

def getBaseDir():
    if TESTING:
        return "/Users/cjm10"
    return getConfigVal('BASE_INSTALL_DIR')

def getServerId():
    return getConfigVal('SERVER_ID')

def getDeleteUrl(url, serverId):
    params = {'uuid' : serverId, 'purp' : 'dele'}
    success, reason = fetchUrl(url, params)
    return success, reason

def getConfirmUrl(url, serverId):
    params = {'uuid' : serverId, 'purp' : 'vali'}
    success, reason = fetchUrl(url, params)
    return success, reason

def getSetupUrl(url, serverId):
    params = {'uuid' : serverId, 'purp' : 'inst'}
    success, reason = fetchUrl(url, params)
    return success, reason

def getUrlOutcome(url, token, devId):
    success = False
    serverId = getServerId();
    if serverId != None and serverId != "YOUR_SERVER_ID" and serverId != "":
        params = {'tok' : token, 'coId' : serverId, 'b2fbe' : 'svr', 'dId' : devId}
        success, reason = fetchUrl(url, params)
    else:
        reason = ("Configuration file error: check " + os.path.dirname(os.path.abspath(__file__)) + "/b2f.config " +
                  "to make sure it's set up correctly")
    return success, reason

def fetchUrl(url, params):
    success = False
    reason = ""
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

