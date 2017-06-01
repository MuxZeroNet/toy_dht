_peer_dict = {}

SMALL_CHANGE = 0.01
BIG_CHANGE = 0.1

STORAGE_DISTANCE = 0xFF
ROUTING_DISTANCE = 0x7FFF

def addNode(node):
    global _peer_dict

    if node not in _peer_dict:
        _peer_dict[node] = {}

    return _peer_dict[node]

def discardNode(node):
    global _peer_dict

    if node in _peer_dict:
        del _peer_dict[node]

def nodes():
    # Use an iterator. (Python 2)
    return sorted(_peer_dict.iterkeys(), key = reputation, reverse = True)

def unorderedNodes():
    # Use an iterator. (Python 2)
    return _peer_dict.iterkeys()

def hasNode(node):
    return node in _peer_dict

def changeReputation(node, diff):
    peer_state = addNode(node)
    peer_state["reputation"] = peer_state.get("reputation", 0) + diff

def reputation(node):
    if node not in _peer_dict:
        return 0
    return _peer_dict[node].get("reputation", 0)


def hasFile(node, file_key):
    if node not in _peer_dict:
        raise ValueError("No such node")
    return file_key in _peer_dict[node].get("retrieved", set())

def isResponsible(node, file_key):
    if node not in _peer_dict:
        raise ValueError("No such node")
    responsibility = nodeDuty(node)
    return responsibility is not None and distance(responsibility, file_key) <= STORAGE_DISTANCE

def nodeDuty(node):
    if node not in _peer_dict:
        raise ValueError("No such node")
    return (_peer_dict.get(node) or {}).get("responsible")

def hasDutyData(node):
    return nodeDuty(node) is not None

def isNeighbor(node, my_duty):
    if node not in _peer_dict:
        raise ValueError("No such node")
    his_duty = nodeDuty(node)
    return his_duty is not None and distance(his_duty, my_duty) <= ROUTING_DISTANCE

def distance(key_a, key_b):
    return key_a ^ key_b


def recordRetrieval(node, file_key):
    peer_state = addNode(node)
    if not peer_state.has_key("retrieved"):
        peer_state["retrieved"] = set()

    peer_state["retrieved"].add(file_key)

def forgetRetrieval(node, file_key):
    global _peer_dict

    if node not in _peer_dict:
        return
    peer_state = _peer_dict[node]
    peer_state.get("retrieved", set()).discard(file_key)


def setDuty(node, duty):
    peer_state = addNode(node)
    if not peer_state.has_key("responsible"):
        peer_state["responsible"] = None

    peer_state["responsible"] = duty

def forgetDuty(node):
    global _peer_dict

    if node not in _peer_dict:
        return
    peer_state = _peer_dict[node]
    peer_state["responsible"] = None
