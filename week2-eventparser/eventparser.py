#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from graphviz import Digraph
import os

if len(sys.argv) < 2:
    sys.stderr.write("Usage: %s <config-file>\n"%sys.argv[0])
    sys.exit(1)

config_fh = open(sys.argv[1], "r")

state_graph = Digraph("State Diagram")
state_graph.attr("graph", rankdir="LR")
state_graph.attr("graph", ranksep="5.0")
color = 0

# TODO Add state entry- and exit-functions.
interesting_section = False


class event_storage:
    def __init__(self):
        self.event = ""
        self.state = ""
        self.new_state = ""
        self.guard = ""
        self.action = ""
        self.action_params = ""
        self.extra_actions = []

current_event = event_storage()

while True:
    line = config_fh.readline()
    if not line:
        break

    if interesting_section:
        try:
            row_data = re.findall("\{([a-zA-Z0-9_ ,()]+)\}", line)[0]
            [event, state, new_state, guard, action, action_params] = [items.strip() for items in row_data.split(",")]
            if event != "0":
                if current_event.event != "":
                    label = current_event.event
                    if current_event.guard != "":
                        label += "\nGuard: %s"%current_event.guard
                    if current_event.action != "":
                        label += "\nAction: %s(%s)"%(current_event.action, current_event.action_params)
                    for extra_action in current_event.extra_actions:
                        label += "\n[ %s ]"%extra_action

                    color_params = {}
                    if color > 0:
                        color_params = {
                            "colorscheme" : "dark28",
                            "color" : "%d"%color,
                            "fontcolor" :"%d"%color

                        }
                    state_graph.edge(
                            current_event.state,
                            current_event.new_state,
                            label=label,
                            **color_params
                        )
                    color = (color+1)%8
                    current_event = event_storage()
                current_event.event = event
                current_event.state = state
                if new_state == "0":
                    new_state = state
                current_event.new_state = new_state
                if guard != "0":
                    current_event.guard = guard
                if action != "0":
                    current_event.action = action
                    current_event.action_params = action_params
            else:
                extra_action = ""
                if guard != "0":
                    extra_action = "%s => "%guard
                extra_action += "%s(%s)"%(action, action_params)
                current_event.extra_actions.append(extra_action)

        except IndexError:
            pass

    if all(word in line for word in ["define", "EVENTTABLE"]):
        interesting_section = True

    if interesting_section and line.strip().endswith("}"):
        interesting_section = False

config_fh.close()

state_graph.render("%s.sd"%os.path.basename(sys.argv[1]).split(".")[0], cleanup=True, view=False)
