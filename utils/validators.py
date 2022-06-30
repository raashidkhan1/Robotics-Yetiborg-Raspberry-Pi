import ipaddress

def is_valid_ip(ip):
    """ Vaidate input ip address by parsing it as ip_address object """
    try:
        ip = ipaddress.ip_address(ip)
        return True
    except ValueError:
        print("IP address {} is not valid".format(ip))
    return False