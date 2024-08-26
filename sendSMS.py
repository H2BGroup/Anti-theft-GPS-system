import gammu

def sendSMS(state_machine, receiver, content):
    
    smsinfo = {
        "Class": -1,
        "Unicode": False,
        "Entries": [
            {
                "ID": "ConcatenatedTextLong",
                "Buffer": content,
            }
        ],
    }

    encoded = gammu.EncodeSMS(smsinfo)

    for message in encoded:
        message["SMSC"] = {"Location": 1}
        message["Number"] = receiver

        state_machine.SendSMS(message)