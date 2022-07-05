import os
import sys

status = os.system('sudo systemctl is-active --quiet nuoj-sandbox')
print(status)
sys.exit(status)