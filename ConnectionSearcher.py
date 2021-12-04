#! /usr/bin/python
# -*- coding: utf-8 -*-

from lib import biplist
import os
import json
import sys
import glob
from workflow import Workflow, ICON_WARNING, MATCH_SUBSTRING

reload(sys)
sys.setdefaultencoding('utf8')


def read_connections():
    # Read preferences file
    preferencesPath = os.path.join(os.environ["HOME"], "Library", "Containers", "com.p5sys.jump.mac.viewer", "Data", "Library", "Preferences", "com.p5sys.jump.mac.viewer.plist")
    # if preference path not exists, try this location:
    if not os.path.isfile(preferencesPath):
        preferencesPath = os.path.join(os.environ["HOME"], "Library", "Preferences", "com.p5sys.jump.mac.viewer.web.plist")
    plist = biplist.readPlist(preferencesPath)
    # Extract profile data from plist
    connectionPath = plist.get('path where JSON .jump files are stored')
    if connectionPath.startswith('~'):
        connectionPath = os.environ["HOME"] + connectionPath[1:]
    jumps = glob.glob(connectionPath + "/Computer - *.jump")
    connections = []
    for jump in jumps:
        f = open(jump)
        json_content = f.read()
        f.close()
        dict_content = json.loads(json_content)
        icon = None
        if dict_content['Icon']:
            icon = "/Applications/Jump Desktop.app/Contents/Resources/%s.png" % dict_content['Icon']
        command = 'jump://?protocol=%s&host=%s&username=%s' % \
                  (protocol_switch(dict_content['ProtocolTypeCode']), dict_content['TcpHostName'], dict_content['Username'])

        connections.append({
            'name': dict_content['DisplayName'],
            'command': command,
            'path': jump,
            'icon': icon,
            'tags': dict_content['Tags']
        })

    return connections


def protocol_switch(x):
    return {
        0: 'rdp',
        1: 'vnc',
        2: 'fluid',
    }.get(x, 0)


def filter_key_for_connection(connection):
    return connection['name'] + ' ' + str(connection['tags'])


def sort_key_for_connection(connection):
    return connection['name']


def main(wf):
    connections = wf.cached_data('connections', read_connections, max_age=30)

    # Query argument Ensure `query` is initialised
    query = None
    if len(wf.args):
        query = wf.args[0]

    connections = wf.filter(query, connections, filter_key_for_connection, match_on=MATCH_SUBSTRING)

    if not connections:
        wf.add_item('No connection matches', icon=ICON_WARNING)

    connections.sort(key=sort_key_for_connection)
    for connection in connections:
        wf.add_item(title=connection['name'],
                    subtitle=((str(connection['tags']) + ' ') if connection['tags'] else '') + connection['command'],
                    arg=connection['path'],
                    valid=True,
                    icon=connection['icon'])

    wf.send_feedback()
    return


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))
    
