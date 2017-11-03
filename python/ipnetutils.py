#pip install netifaces
#
# use the function get_default_ip()
# returns None if none found, IP as string for the first (and default) configuration IP.
# 

import netifaces

def get_from_mask(addr, mask):

	addr_s = addr.split('.')
	mask_s = mask.split('.')
	ret = []
	
	for i in range(len(addr_s)):
		a = int(addr_s[i])
		b = int(mask_s[i])
		if a & b:
			ret.append(str(a & b))
		
	return ".".join(ret)
		
def get_default_ip():
	default = netifaces.gateways()['default'][netifaces.AF_INET]

	for i in netifaces.interfaces():
		addr = netifaces.ifaddresses(i)[netifaces.AF_INET]
		for a in addr:
			netmask = a['netmask']
			addr = a['addr']
			mask_addr = get_from_mask(addr, netmask)
			mask_default = get_from_mask(default[0], netmask)
			if mask_addr == mask_default:
				return(addr)
				
	return None	
		


if __name__ == "__main__":
	
	print get_default_ip()
	
			

