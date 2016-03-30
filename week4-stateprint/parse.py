#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
from seqdiag import parser, builder, drawer

if len(sys.argv) < 3:
    sys.stderr.write("Usage: %s <c-file> <log-file>\n"%sys.argv[0])
    sys.exit(1)

c_fh = open(sys.argv[1], "r")
log_fh = open(sys.argv[2], "r")

all_names = { "states" : [], "events" : [] }

interesting_section = False
append_func = None
while True:
    line = c_fh.readline()
    if not line:
        break

    if interesting_section and "#endif" in line:
        interesting_section = False

    if interesting_section:
        data = re.findall("\([a-zA-Z0-9_, ]+\)", line)
        if len(data) > 0:
            append_func(data[0][1:-1].split(",")[0])

    if not interesting_section and "define" in line and "EVENT_LIST" in line:
        interesting_section = True
        append_func = all_names["events"].append

    if not interesting_section and "define" in line and "STATE_LIST" in line:
        interesting_section = True
        append_func = all_names["states"].append




class Event:
    def __init__(self, event=None, enter_state=None):
        self.event = event
        self.enter_state = enter_state
        self.exit_state = None
        self.result = None
        self.delayed = []
        self.log = []
        self.__repr__ = self.__str__

    def __str__(self):
        return "%d -> %d -> %d"%(self.enter_state, self.event, self.exit_state)

class StateResults:
    EV_RESULT_NO_MATCH = 0
    EV_RESULT_EXECUTED = 1
    EV_RESULT_DELAYED = 2
    EV_RESULT_GUARD_FAILED = 3
    names = ["No Match", "Executed", "Delayed", "Guard Failed" ]
    colors = ["red", "black", "blue", "red"]


sequence = []
pending_events = []
current_event = None
current_state = None
current_log = []


def event_incoming(line):
    global current_event
    global current_state
    global pending_events
    numbers = re.findall(r"\d+", line)

    if current_event == None:
        current_event = Event()
        current_event.event = int(numbers[0])
        if current_state == None:
            current_state = int(numbers[1])-1
        current_event.enter_state = current_state
    else:
        current_event.delayed.append(int(numbers[0]))
        pending_events.append(Event(int(numbers[0])))
#print "Incoming Event: [e: %s][s: %s]"%(event_name, state_name)

def event_result(line):
    global current_event
    global sequence
    global current_log
    global current_state
    numbers = re.findall(r"\d+", line)
    if int(numbers[1]) == StateResults.EV_RESULT_EXECUTED and int(numbers[0]) != current_event.event:
        sys.stderr.write("Error! Result didn't match current event: %s\n"%line)
        sys.exit(1)

    if int(numbers[1]) != StateResults.EV_RESULT_DELAYED:
        if current_event.exit_state == None:
            current_event.exit_state = current_state
        current_event.log = current_log
        current_log = []
        current_event.result = int(numbers[1])
        sequence.append(current_event)
        current_event = None

#    print "Event result: [e: %s]: %s"%(event_name, additional_text)

def state_transition(line):
    global current_event
    global current_state
    numbers = re.findall(r"\d+", line)
    current_event.exit_state = int(numbers[0])
    current_state = int(numbers[0])-1

#    print "State Transition: New state: %s"%state_name


func_table = {
    "i:" : event_incoming,
    "r:" : event_result,
    "t:" : state_transition
}

while True:
    line = log_fh.readline()
    if not line:
        break

    line = line.strip()

    try:
        func_table[line[:2]](line)
    except KeyError:
        current_log.append(line)

    if current_event == None and len(pending_events) > 0:
        current_event = pending_events[0]
        pending_events = pending_events[1:]
        current_event.enter_state = current_state

transition_spec = ""
used_states = []
for event in sequence:
    enter_state_name = all_names["states"][event.enter_state]
    used_states.append(enter_state_name)
    exit_state_name = all_names["states"][event.exit_state]
    event_name = all_names["events"][event.event]
    delayed_events = ""
    for delayed in event.delayed:
        delayed_events += "%s -> %s [label='Delayed:\\n%s', color=blue, failed];\n"%(
                enter_state_name,
                enter_state_name,
                all_names["events"][delayed]
                )
    log_text = "\\n".join(event.log)
    transition = "%s -> %s [label='%s:\\n%s', color=%s, leftnote='%s'] { %s };"%(
                enter_state_name,
                exit_state_name,
                StateResults.names[event.result],
                event_name,
                StateResults.colors[event.result],
                log_text,
                delayed_events
            )
    transition_spec += "    %s\n"%transition

used_states_text = ""
for state in set(used_states):
    used_states_text += "%s [width = 200];\n"%state

diag_spec = u"""
seqdiag {
    %s
    %s
}
"""%(used_states_text, transition_spec)

tree = parser.parse_string(diag_spec)
diagram = builder.ScreenNodeBuilder.build(tree)
draw = drawer.DiagramDraw('SVG', diagram, filename="diagram.svg")
draw.draw()
draw.save()
