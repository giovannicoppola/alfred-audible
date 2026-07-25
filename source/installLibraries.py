#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Creates a virtualenv in the workflow data folder and installs a pinned
# audible-cli into it. The venv lives outside the (possibly synced) workflow
# folder and survives workflow updates.

import json
import os
import re
import subprocess

from config import VENV_FOLDER, VENV_PYTHON

# audible-cli 0.3.3 requires python >=3.10,<3.14
SUPPORTED = re.compile(r"Python 3\.1[0-3]\.")
CANDIDATES = ["python3.13", "python3.12", "python3.11", "python3.10", "python3"]
SEARCH_DIRS = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]


def alfredItem(title, subtitle, valid=False):
    print(json.dumps({"items": [{
        "title": title,
        "subtitle": subtitle,
        "arg": "",
        "valid": valid,
        "icon": {"path": ""}
    }]}))


def findPython():
    for name in CANDIDATES:
        for d in SEARCH_DIRS:
            exe = os.path.join(d, name)
            if not os.path.exists(exe):
                continue
            try:
                ver = subprocess.run([exe, "--version"], capture_output=True,
                                     text=True, timeout=15).stdout
            except Exception:
                continue
            if SUPPORTED.match(ver.strip()):
                return exe
    return None


def venvWorks():
    if not os.path.exists(VENV_PYTHON):
        return False
    check = subprocess.run([VENV_PYTHON, "-m", "audible_cli", "--version"],
                           capture_output=True)
    return check.returncode == 0


def main():
    if venvWorks():
        alfredItem("Libraries already installed ✅ Press Enter to setup your Audible device 📲",
                   "will abort if a device is already registered", valid=True)
        return

    myPython = findPython()
    if not myPython:
        alfredItem("🚨 No compatible Python found (need 3.10–3.13)",
                   "install one with: brew install python@3.13, then run audible:setup again")
        return

    try:
        subprocess.run([myPython, "-m", "venv", "--clear", VENV_FOLDER],
                       check=True, capture_output=True, text=True)
        reqFile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "requirements.txt")
        subprocess.run([VENV_PYTHON, "-m", "pip", "install", "--quiet",
                        "-r", reqFile],
                       check=True, capture_output=True, text=True, timeout=600)
    except subprocess.CalledProcessError as err:
        errTail = (err.stderr or "").strip().splitlines()[-1:]
        alfredItem("🚨 library install failed",
                   errTail[0] if errTail else "unknown error")
        return

    alfredItem("Libraries installed! Press Enter to setup your Audible device 📲",
               "will abort if a device is already registered", valid=True)


if __name__ == "__main__":
    main()
