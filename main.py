from Network import sendTo
from Verifier import checkIntegrity
import RoutingTable

from random import SystemRandom

def main():
    # Use bootstrap nodes and some random keys to discover inital DHT nodes
    BOOTSTRAP = [u"A", u"B", u"C"]
    FILE_KEY, RANDOM_KEY = 0xc2dd31, 0x1b45e2
    for b in BOOTSTRAP:
        RoutingTable.addNode(b)
    collectNodes(RoutingTable.nodes()[0:3], [FILE_KEY, RANDOM_KEY])
    print("We know %s peers and their responsibilities: %s" % (str(len(RoutingTable._peer_dict)), repr(RoutingTable.nodes())))

    # Look for known nodes closest to key
    print("Looking for peers who have key 0xc2dd31...")
    nodes = findCachedNodes(FILE_KEY)
    print("Closest nodes to key, closest first: " + ", ".join(nodes))

    # Ask for values, 10 nodes at a time
    lower_index = 0
    while lower_index < len(nodes):
        value = findValue(nodes[lower_index : lower_index + 10], FILE_KEY)
        if value:
            print("Found the value! " + repr(value))
            break
        else:
            print("No value can be found")
            lower_index += 10

    print("Done asking for values")


def collectNodes(node_list, file_keys):
    for node in node_list:
        key_index = 0
        for key in file_keys:
            routes = familiarize(node, key)

            print("Routes taken.")
            for r in routes:
                if r:
                    print(" -> ".join(r))

def familiarize(node, file_key):
    """Recursively walk through the DHT, directed by an initial node and key.
    Return a list of routes taken
    """
    return _familiarize(node, file_key, history = set(), ttl = 5)

def _familiarize(node, file_key, history, ttl):
    if ttl <= 0 or node in history:
        return [[]]
    history.add(node)

    print("Asking node " + repr(node))
    routes = []
    # if we don't know his responsibility
    if not RoutingTable.hasNode(node) or not RoutingTable.hasDutyData(node):
        _updateResponsibility(node)
        routes.append([node])

    # ask more nodes recursively
    resp = sendTo(node, cmd("find_key", file_key))
    if resp:
        worth_asking = resp.get("worth_asking")
        if worth_asking:
            for another_node in pickSome(worth_asking, ttl):
                chains = _familiarize(another_node, file_key, history, ttl - 1)

                for line in chains:
                    if line:
                        routes.append([node] + line)
            print("Done")

    return routes

def _updateResponsibility(node):
    resp = sendTo(node, cmd("responsibility"))
    if resp:
        responsible = resp.get("responsible")
        if responsible is not None:
            responsible = int(responsible, 16)
            RoutingTable.setDuty(node, responsible)
            return responsible

def lookupResponsibility(node):
    if RoutingTable.hasNode(node) and RoutingTable.hasDutyData(node):
        return RoutingTable.nodeDuty(node)
    else:
        return _updateResponsibility(node)

def pickSome(nodes, ttl = 5):
    """Return some nodes from the given node list, most useful first"""
    if ttl <= 0:
        return []
    return nodes[0:ttl]

def findCachedNodes(file_key):
    """Return a subset of cached nodes most likely to have the file key. Most likely first"""
    possible, responsible, closest = [], [], []

    for node in RoutingTable.nodes():
        if len(possible) + len(responsible) > 20 or len(closest) > 200:
            break

        if RoutingTable.hasFile(node, file_key):
            possible.append(node)
        elif RoutingTable.isResponsible(node, file_key):
            responsible.append([node, RoutingTable.distance(file_key, RoutingTable.nodeDuty(node))])
        elif RoutingTable.hasDutyData(node):
            closest.append([node, RoutingTable.distance(file_key, RoutingTable.nodeDuty(node))])

    _logNodes(possible, responsible, closest)

    possible += [item[0] for item in sorted(responsible, key = lambda t: t[1])]
    possible += [item[0] for item in sorted(closest, key = lambda t: t[1])[0:20]]
    return possible

def _logNodes(possible, responsible, closest):
    print("Found %s non-DHT possible value holders, %s responsible nodes and %s second closest nodes" \
        % (str(len(possible)), str(len(responsible)), str(len(closest))))
    print("Distances: %s %s" % (repr(responsible), repr(closest)))


def findValue(initial_nodes, file_key):
    """Recursively find value, first asking some initial nodes"""
    # Use a smaller TTL
    return _findValue(initial_nodes, file_key, set(), 3)

def _findValue(initial_nodes, file_key, history, ttl):
    if not initial_nodes or ttl <= 0:
        return None

    queue = []
    for node in initial_nodes:
        small_queue = []
        data = _findValueLevel(node, file_key, history, small_queue, ttl)
        if data is not None:
            return data

        if not small_queue:
            continue
        node_resp = lookupResponsibility(node)
        for n in small_queue:
            queue.append(n)
            n_resp = lookupResponsibility(n)
            if isCloser(n, n_resp, node_resp, file_key):
                RoutingTable.setDuty(n, n_resp)

    return _findValue(queue, file_key, history, ttl - 1)

def _findValueLevel(node, file_key, history, queue, ttl):
    if node in history:
        return None

    print("Asking node %s for value..." % repr(node))
    data, nodes = getFile(node, file_key)
    history.add(node)

    if data is not None:
        return data
    elif not nodes:
        return None
    else:
        for n in pickSome(nodes, ttl):
            queue.append(n)
        return None



def isCloser(n, new_resp, old_resp, file_key):
    if (old_resp is not None) and (new_resp is not None):
        if RoutingTable.distance(file_key, new_resp) <= RoutingTable.distance(file_key, old_resp):
            return True
    return False

def getFile(node, file_key):
    """Ask the node for value.
    Return value [0]: will always be a verified value. Will be None if value is invalid or node is down
    Return value [1]: other nodes worth asking, most useful first (list). [] if no node
    """
    data, nodes = _getGoodValue(node, file_key)
    direction = -1 if (data is None) else 1
    RoutingTable.changeReputation(node, direction * RoutingTable.BIG_CHANGE)
    return (data, nodes)

def _getGoodValue(node, file_key):
    resp = sendTo(node, cmd("find_value", file_key))
    if not resp or not isinstance(resp, dict):
        return (None, [])

    data = resp.get("data")
    nodes = resp.get("worth_asking")

    if not nodes or not isinstance(nodes, list):
        nodes = []
    if not checkIntegrity(data):
        data = None

    return (data, nodes)

def cmd(cmd_name, param = None):
    result = {"cmd": cmd_name}
    if param is not None:
        result["param"] = param
    return result

if __name__ == "__main__":
    main()
