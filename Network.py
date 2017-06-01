import io
import json

_resp_dict = {}

def init():
    global _resp_dict

    json_str = io.open("big_network.json", "r").read()
    _resp_dict = json.loads(json_str)

def _sendTo(node, data):
    node_script = _resp_dict.get(node)
    if not node_script:
        return False

    node_answer = node_script.get(data["cmd"])
    if not node_answer:
        return False

    param = data.get("param")
    answer = None
    if param is None:
        answer = node_answer
    elif isinstance(param, int):
        answer = node_answer.get(hex(param))
    else:
        answer = node_answer.get(param)

    if isinstance(answer, (bytes, unicode)) and answer.startswith("0x"):
        return int(answer, 16)
    else:
        return answer

def sendTo(node, data):
    result = _sendTo(node, data)
    # print("Node %s says %s" % (repr(node), repr(result)))
    return result

init()
