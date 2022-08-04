from netifaces import interfaces, ifaddresses, AF_INET

def get_local_ips():
    """ Assumes the host has an external IP"""   
    result = []
    for ifaceName in interfaces():    
        addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
        addr = addresses[0]
        if addr != 'No IP addr' and addr != '127.0.0.1':
            result.append(addr)
    return result
