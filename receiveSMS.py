#!/usr/bin/env python
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of python-gammu <https://wammu.eu/python-gammu/>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from parseSMS import parseSMS
from sendSMS import sendSMS
import gammu

def receiveSMS():

    state_machine = gammu.StateMachine()
    state_machine.ReadConfig()
    state_machine.Init()

    status = state_machine.GetSMSStatus()

    remain = status["SIMUsed"] + status["PhoneUsed"] + status["TemplatesUsed"]

    sms = []
    start = True

    print("connected to phone, getting messages")
    try:
        while remain > 0:
            if start:
                cursms = state_machine.GetNextSMS(Start=True, Folder=0)
                start = False
            else:
                cursms = state_machine.GetNextSMS(Location=cursms[0]["Location"], Folder=0)
            remain = remain - len(cursms)
            sms.append(cursms)
            state_machine.DeleteSMS(Folder=0, Location=cursms[0]["Location"])
    except gammu.ERR_EMPTY:
        # This error is raised when we've reached last entry
        # It can happen when reported status does not match real counts
        print("Failed to read all messages!")

    state_machine.Terminate()
    state_machine = None

    data = gammu.LinkSMS(sms)

    print("finished receiving messages")
    responses = []

    for x in data:
        v = gammu.DecodeSMS(x)

        m = x[0]
        print()
        print("{:<15}: {}".format("Number", m["Number"]))
        print("{:<15}: {}".format("Date", str(m["DateTime"])))
        print("{:<15}: {}".format("State", m["State"]))
        print("{:<15}: {}".format("Folder", m["Folder"]))
        print("{:<15}: {}".format("Validity", m["SMSC"]["Validity"]))
        loc = []
        for m in x:
            loc.append(str(m["Location"]))
        print("{:<15}: {}".format("Location(s)", ", ".join(loc)))
        if v is None:
            print("\n{}".format(m["Text"]))
            res = parseSMS(m["Number"], m["Text"])
            if res != None:
                responses.append(res)
        else:
            print("Long sms or not supported")
            # for e in v["Entries"]:
            #     print()
            #     print("{:<15}: {}".format("Type", e["ID"]))
            #     if e["Bitmap"] is not None:
            #         for bmp in e["Bitmap"]:
            #             print("Bitmap:")
            #             for row in bmp["XPM"][3:]:
            #                 print(row)
            #         print()
            #     if e["Buffer"] is not None:
            #         print("Text:")
            #         print(e["Buffer"])
            #         print()
    if len(responses) > 0:
        print("responding to messages")
        state_machine = gammu.StateMachine()
        state_machine.ReadConfig()
        state_machine.Init()

        for res in responses:
            sendSMS(state_machine, res[0], res[1])
        
        state_machine.Terminate()
        state_machine = None