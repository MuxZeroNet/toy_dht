# Toy DHT

As you expect, this is a simple DHT written for educational purposes. It is single-threaded, not thread-safe, not crazily fast. It runs on an emulated network.

## Network Emulation

I do not have 500 computers. The Internet it runs on is emulated based on a JSON file. You can run `generate_network.py` to create another emulated Internet.

## DHT Details

This program does not implement any "standard" DHT protocol. It is written for you to understand how DHT works.

For simplicity, the key length is only 3 bytes. Practical DHT has a longer key length to cut down routing costs.

To see the DHT network working, run `main.py` in your terminal.

## Implemented

- Discovering initial DHT peers and their responsibilities
- Remembering peer addresses and metadata
- Finding peers closest to a key
- Finding the value bound to a key with a level-order traversal algorithm

## Not Implemented (yet)

- Changing routing preference according to peer reputation
- The "storage" of values
- Responding to others
