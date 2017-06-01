import json
from random import SystemRandom

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890"
KEY = 0xc2dd31
BOOTSTRAP = ["A", "B", "C", "D"]

node_names = set()

def main():
    print(json.dumps(makeJson()))

def nodeName():
    return SystemRandom().choice(list(node_names))

def makeNames(n):
    for node in BOOTSTRAP:
        node_names.add(node)

    for i in range(n):
        name = SystemRandom().choice(LETTERS) + SystemRandom().choice(LETTERS)
        node_names.add(name)

def makeJson():
    n = 500
    makeNames(n)
    node_values = [makeNodeAnswer() for i in range(n)]

    result = {}
    name_index = 0
    name_list = list(node_names)
    for val in node_values:
        if name_index >= len(name_list):
            break
        result[name_list[name_index]] = val
        name_index += 1

    return result

def makeNodeAnswer():
    node = Node()
    answer = {
        "ping": node.askPing(),
        "find_key": node.askFindKey(KEY),
        "find_value": node.askFindValue(KEY),
        "responsibility": node.askResponsibility()
    }

    return answer


class Node:

    def __init__(self):
        self.dead = SystemRandom().randint(0, 100) < 25
        self.responsibility = SystemRandom().randint(0, 0xffffff)
        self.has_keys = set([SystemRandom().randint(0, 0xffffff) for i in range(SystemRandom().randint(0, 10))])
        self.known_nodes = set([nodeName() for i in range(SystemRandom().randint(0, 10))])
        self.data = "GOOD_DATA" if (SystemRandom().randint(0, 100) < 50) else "BAD_DATA"

        r = SystemRandom().randint(0, 100)

        if r < 10:
            self.responsibility = KEY
            self.has_keys.add(KEY)
        elif r < 25:
            shift = r % 16 + 1
            self.responsibility = (KEY >> shift) << shift
        elif r < 50:
            self.has_keys.add(self.responsibility)

    def askPing(self):
        if not self.dead:
            return "pong"

    def askFindKey(self, key):
        if self.dead:
            return None

        return {
            hex(key): {
                "has_key": key in self.has_keys,
                "worth_asking": list(self.known_nodes)
            }
        }

    def askFindValue(self, key):
        if self.dead:
            return None

        if not(key in self.has_keys):
            return {
                hex(key): {
                    "error": "I don't have this key.",
                    "worth_asking": list(self.known_nodes)
                }
            }
        else:
            return {
                hex(key): {
                    "data": self.data,
                    "worth_asking": list(self.known_nodes)
                }
            }

    def askResponsibility(self):
        if self.dead:
            return None

        return {
            "responsible": hex(self.responsibility),
            "has_keys": [hex(v) for v in self.has_keys]
        }



if __name__ == "__main__":
    main()
