import re
import os
import pandas as pd

def getProfilesFromConfig(path):

    pName = []

    cfgFile = open(path, 'r')
    Lines = cfgFile.readlines()

    for line in Lines:
        m = re.findall("\[.*\]", line)
        if len(m) > 0:
            pName.append(str(m[0]).replace('[', "").replace(']', ""))

    return pName