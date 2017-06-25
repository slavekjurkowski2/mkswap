#!/usr/bin/python
#
# A ansible module to create a linux swap partition
#
# example:
# - name: create swap
#   mkswap:
#     dev: /dev/sdb1
#
# 2017-06-25 Florian Schmidt <floschmi at gmail dot com>
# License: GNU GPLv3
#

from ansible.module_utils.basic import AnsibleModule
import subprocess

def checkDevice(dev):
	try:
		output = subprocess.check_output(["blkid", dev])
	except subprocess.CalledProcessError:
		return "free"

	if 'TYPE="swap"' in output:
		return "alreadySwap"
	elif "TYPE" in output:
		return "occupied"
	
	return "unknownError"

def mkswap(dev):
	rc = subprocess.call(["mkswap", dev])

	if(rc == 0):
		return "success"
	return "failed"

def checkFstab(dev):
	fstab = open("/etc/fstab", "r")
	for line in fstab:
		if dev in line:
			fstab.close()
			return "found"
	fstab.close()
	return "notFound"

def writeFstab(dev):
	fstab = open("/etc/fstab", "a")
	fstab.write(dev + " swap swap defaults 0 0\n")
	fstab.close()

def main():
	module = AnsibleModule(
		argument_spec = dict(
			dev      = dict(required=True),
		)
	)

	noChange = True
	dev = module.params['dev']

	# device check / mkswap on device
	deviceCheck = checkDevice(dev)
	if(deviceCheck == "occupied"):
		module.exit_json(failed=True, msg="There is already a filesystem on the device.")
	elif(deviceCheck == "unknownError"):
		module.exit_json(failed=True, msg="unknown error.")
	elif(deviceCheck == "free"):
		mkswap_rc = mkswap(dev)
		if(mkswap_rc == "success"):
			noChange = False
		else:
			module.exit_json(failed=True, msg="error while creating swap, does the device exist?")


	# swapon
	subprocess.call(["swapon",dev]) 

	# fstab
	rc = checkFstab(dev)
	if(rc == "notFound"):
		writeFstab(dev)
		noChange = False

	# return 
	if noChange:
		module.exit_json(changed=False)
	else:
		module.exit_json(changed=True)

if __name__ == '__main__':
    main()
