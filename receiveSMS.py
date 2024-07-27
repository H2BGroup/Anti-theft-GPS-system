#!/usr/bin/env python

import os
import parseSMS

numparts = int(os.environ["DECODED_PARTS"])

text = ""
# Are there any decoded parts?
if numparts == 0:
    text = os.environ["SMS_1_TEXT"]
# Get all text parts
else:
    for i in range(1, numparts + 1):
        varname = "DECODED_%d_TEXT" % i
        if varname in os.environ:
            text = text + os.environ[varname]

# Do something with the text
print("Number {} have sent text: {}".format(os.environ["SMS_1_NUMBER"], text))
parseSMS.parseSMS(os.environ["SMS_1_NUMBER"], text)
