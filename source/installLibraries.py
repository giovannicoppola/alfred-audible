#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from audi_fun import *
from config import WF_LIB_FOLDER, WF_FOLDER


if not os.path.exists(WF_LIB_FOLDER):
    os.makedirs(WF_LIB_FOLDER)
    os.system ("pip3 install -r requirements.txt --target=lib  > /dev/null")
    
resultErr= {"items": [{
        "title": "Libraries installed! Press Enter to setup your Audible device 📲",
        "subtitle": "will abort if already existing",
        "arg": "",
        "icon": {
            "path": ""
            }
            }]}
print (json.dumps(resultErr))


