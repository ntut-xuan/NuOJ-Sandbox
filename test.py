import os

status = os.system('systemctl is-active --quiet nuoj-sandbox')
print(status)
exit(status)