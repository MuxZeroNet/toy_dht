# Toy DHT

For serious DHT implementation, see my [`Pastry`][pastry_repo] repo. It is a
Pythonic but incomplete implementation of the [Pastry DHT][pastry_dht].

To learn more about DHT in general, check out these videos by Anne-Marie
Kermarrec.

_Routing in Distributed Hash Tables._
https://www.youtube.com/watch?v=WqQRQz_XYg4

_Dynamics in Distributed Hash Tables._
https://www.youtube.com/watch?v=p8iugvHeGcg

The original code in this `toy_dht` repository has been removed. To see the
code, feel free to `git reset --hard <commit_hash>`. Please note that the
original code can be misleading, though it produces fancy outputs.

If you are here for a silly analogy, here it is:

### DHT routing in a nutshell

For some reason, I wanted to chat with Barack Obama, but I did not know his
phone number, so I asked a friend.

My friend had no idea what Obama’s phone number was, so he kindly asked me to
call my rep.

I called my rep. He did not have Obama’s phone number, so he gave me the phone
number of his colleague in Washington D.C.

I called his colleague. He knew Obama’s phone number.

Finally, I got Obama's phone number.


[pastry_repo]: https://github.com/MuxZeroNet/pastry
[pastry_dht]: https://en.wikipedia.org/wiki/Pastry_(DHT)