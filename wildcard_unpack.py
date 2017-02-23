import socket, struct, ipaddress

masks = [
        0x00000000,
        0x80000000,
        0xC0000000,
        0xE0000000,
        0xF0000000,
        0xF8000000,
        0xFC000000,
        0xFE000000,
        0xFF000000,
        0xFF800000,
        0xFFC00000,
        0xFFE00000,
        0xFFF00000,
        0xFFF80000,
        0xFFFC0000,
        0xFFFE0000,
        0xFFFF0000,
        0xFFFF8000,
        0xFFFFC000,
        0xFFFFE000,
        0xFFFFF000,
        0xFFFFF800,
        0xFFFFFC00,
        0xFFFFFE00,
        0xFFFFFF00,
        0xFFFFFF80,
        0xFFFFFFC0,
        0xFFFFFFE0,
        0xFFFFFFF0,
        0xFFFFFFF8,
        0xFFFFFFFC,
        0xFFFFFFFE,
        0xFFFFFFFF
]

def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

def is_bit_on(number, bit):
    return (number & (1 << (32 - bit))) != 0

def contiguous_bits(mask):
    """
    Return an array of range tuples (start, end) of groups of on bits in
    the discontiguous mask
    """
    ranges = []
    start = None
    end = None
    for bit in range(1,33):
        if is_bit_on(mask, bit):
            if start:
                end = bit
            else:
                start = bit
                end = bit
        elif end:
            ranges.append((start, end))
            start = None
            end = None
    if end:
        ranges.append((start, end))
    return ranges

def unroller(ranges, prefixes):
    """
    Takes an array of prefixes and array of ranges, operates on the
    first range and recurses until returning the full array of unrolled
    prefixes
    """
    if not ranges:
        return prefixes
    unrolled = []
    rng = ranges.pop(0)
    start = rng[0]
    end = rng[1]
    bits = end - start + 1
    for prefix in prefixes:
        for field in range(0, 2**bits):
            mask = masks[start - 1] | (masks[32] >> end)
            unrolled.append((prefix & mask) | (field << (32 - end)))
    return unroller(ranges, unrolled)
    
def unroll(addr, mask):
    """
    Return an array of ipaddress objects with prefix and normal netmasks 
    unrolled from the wildcard mask
    """

    addr_as_long = ip2long(addr)
    mask_as_long = ip2long(mask)

    # If the final bitstring ends in 32, we will return subnets instead
    # of addresses, so set it aside for later
    rng = None
    ranges = contiguous_bits(mask_as_long)
    if ranges[-1][1] == 32:
        rng = ranges.pop()
    unrolled = unroller(ranges, [addr_as_long])

    processed = []
    for address in unrolled:
        if rng:
            start = rng[0]
            end = rng[1]
            network = address & masks[start]
            processed.append(ipaddress.IPv4Network((network, start)))
        else:
            processed.append(ipaddress.IPv4Network(address))

    return processed

addr = "10.12.14.16"

# 0x00FF0081
mask = "0.255.0.129"
print "Unrolling %s/%s" % (addr, mask)
output = unroll(addr, mask)
print "Results in %d networks: %s" % (len(output), output)

# 0xF0000002
mask = "240.0.0.2"
print "Unrolling %s/%s" % (addr, mask)
output = unroll(addr, mask)
print "Results in %d networks: %s" % (len(output), output)

# 0x00F00003
mask = "0.240.0.3"
print "Unrolling %s/%s" % (addr, mask)
output = unroll(addr, mask)
print "Results in %d networks: %s" % (len(output), output)

# [{'10.0.1.64': '255.0.7.224'}

addr = "10.0.1.64"
mask = "255.0.7.224"
print "Unrolling %s/%s" % (addr, mask)
output = unroll(addr, mask)
print "Results in %d networks, which is a lot" % len(output)
