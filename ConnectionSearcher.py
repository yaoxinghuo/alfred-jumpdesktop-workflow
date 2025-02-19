#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import json
import os
import plistlib
import sys

from workflow import ICON_WARNING, MATCH_SUBSTRING, Workflow3


def read_connections():
    # Read preferences file
    preferences_path = os.path.join(
        os.environ["HOME"],
        "Library",
        "Containers",
        "com.p5sys.jump.mac.viewer",
        "Data",
        "Library",
        "Preferences",
        "com.p5sys.jump.mac.viewer.plist",
    )
    # if preference path not exists, try this location:
    if not os.path.isfile(preferences_path):
        preferences_path = os.path.join(
            os.environ["HOME"],
            "Library",
            "Preferences",
            "com.p5sys.jump.mac.viewer.web.plist",
        )

    # try setapp jump desktop
    if not os.path.isfile(preferences_path):
        preferences_path = os.path.join(
            os.environ["HOME"],
            "Library",
            "Preferences",
            "com.p5sys.jumpdesktop-setapp.plist",
        )

    connections = []
    with open(preferences_path, "rb") as fp:
        plist = plistlib.load(fp)
        # Extract profile data from plist
        connection_path = plist.get("path where JSON .jump files are stored")

        if connection_path is None:
            connection_path = "~/Documents/JumpDesktop/Viewer/Servers"

        connection_path = os.path.normpath(os.path.expanduser(connection_path))

        jumps = glob.glob(connection_path + "/Computer - *.jump")
        connections = []
        for jump in jumps:
            f = open(jump)
            json_content = f.read()
            f.close()
            dict_content = json.loads(json_content)
            icon = None
            if dict_content["Icon"]:
                icon = (
                    "/Applications/Jump Desktop.app/Contents/Resources/%s.png"
                    % dict_content["Icon"]
                )
            username = ""
            if "Username" in dict_content:
                username = dict_content["Username"]
            command = "jump://?protocol=%s&host=%s&username=%s" % (
                protocol_switch(dict_content["ProtocolTypeCode"]),
                dict_content["TcpHostName"],
                username,
            )

            connections.append(
                {
                    "name": dict_content["DisplayName"],
                    "command": command,
                    "path": jump,
                    "icon": icon,
                    "tags": dict_content["Tags"],
                }
            )

    return connections


def protocol_switch(x):
    return {
        0: "rdp",
        1: "vnc",
        2: "fluid",
    }.get(x, 0)


def filter_key_for_connection(connection):
    return connection["name"] + " " + str(connection["tags"])


def sort_key_for_connection(connection):
    return connection["name"]


def main(wf: Workflow3):
    connections = wf.cached_data("connections", read_connections, max_age=30)

    # Query argument Ensure `query` is initialised
    query = None
    if len(wf.args):
        query = wf.args[0]

    connections = wf.filter(
        query, connections, filter_key_for_connection, match_on=MATCH_SUBSTRING
    )

    if not connections:
        wf.add_item("No connection matches", icon=ICON_WARNING)

    connections.sort(key=sort_key_for_connection)
    for connection in connections:
        wf.add_item(
            title=connection["name"],
            subtitle=((str(connection["tags"]) + " ") if connection["tags"] else "")
            + connection["command"],
            arg=connection["path"],
            valid=True,
            icon=connection["icon"],
        )

    wf.send_feedback()
    return


if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
