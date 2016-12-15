#!/usr/bin/python3
import comfoconnect

c = comfoconnect.BridgeDiscovery()
bridges = c.Discover()
if bridges:
    print("Found bridges:")
    for bridge in bridges:
        print(" * %s" % bridge)
else:
    print("No bridges were found.")
