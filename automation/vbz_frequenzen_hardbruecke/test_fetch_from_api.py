# -*- coding: utf-8 -*-

import os
import sys
import csv
import traceback
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv, find_dotenv
# load_dotenv(find_dotenv())

user = os.getenv('VBZ_SSZ_USER_N')
pw = os.getenv('VBZ_SSZ_USER')
#user = os.getenv('VBZ_SSZ_USER')
#pw = os.getenv('VBZ_SSZ_PASSWORD')

print(user)
