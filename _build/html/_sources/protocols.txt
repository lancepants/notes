Protocols
=========
This is a general catch-all. Topic-specific protocols (eg: TCP) may exist under other pages.

DNS
---
port:53

DNS Resolution process
^^^^^^^^^^^^^^^^^^^^^^
# Host looks in its cache for www.wiki.org (if it has a dns cache)
# Host asks its configured nameserver(s) where www.wiki.org is
# nameserver checks its cache
# nameserver either asks a configured recursive nameserver, or has recursive lookup itself
# recursive nameserver has "hints" of the known address of root name servers, or is configured to have some
# recursive nameserver asks root nameserver for www.wiki.org, root nameserver passes back auth nameserver for .org
# recursive nameserver asks authoritative nameserver for .org for www.wiki.org, .org nameserver passes back auth nameserver for wiki.org
# recursive nameserver asks authoritative nameserver for wiki.org for www.wiki.org
# authoritative nameserver for wiki.org answers www.wiki.org = 147.0.2.3
# recursive nameserver passes back info to previous host or nameserver

General
^^^^^^^
Every domain has at least one authoritative DNS server (eg: ns1.wiki.org). These authoritative servers publish info about that domain and the name servers of any domains subordinate to it. These servers pass back their answers with the Authoritave Answer (AA) flag set.

These ns[1,2].wiki.org records are configured at the .org nameserver as well as the authoritative wiki.org server. In the example above, the recursive server is querying the .org server for www.wiki.org. In that response, the .org nameserver is telling it to contact ns1.wiki.org. The recursive nameserver doesn't know the IP of ns1.wiki.org and it's already querying about finding wiki.org. In this case, the .org nameserver must pass back a **"glue"** record containing the IP's of ns1&2. This is contained in the "additional" section of the DNS response.

An *authoritative-only* nameserver is configured to only return answers to queries about domain names that have been specifically configured by the admin. So, an authoritative server lets recursive nameservers know address info for the domains it has configured.

Query and Reply Structure
^^^^^^^^^^^^^^^^^^^^^^^^^
Each message consists of a header and four sections: question, answer, authority, and additional. Queries and replies have the same structure. The header section contains the fields: Identification, Flags, Number of questions, Number of answers, Number of authority resource records (RRs), and Number of additional RRs. The flags field has bits that are flipped to say whether it's a reply or a query, whether the response (only on replies) is authoritative, whether a recursive query is requested, and whether a dns server supports recursion (reply only).

A RR (Resource Record) is just a line in a DNS file
  NAME	TYPE(# in numberic form, eg:15 for MX)	CLASS(Almost always "IN" for internet)	TTL	RDLENGTH(length of RDATA field)	RDATA(ie: an ip address)


HTTP
----
TODO: EXPAND

Stateless?
^^^^^^^^^^
Most HTTP conversation does not drop the connection on every request, but rather multiple HTTP requests are pipelined in the same connection. In HTTP 1.0, client can indicate that it wants to send multiple requests in the same connection by using Connection: Keep-Alive header, in HTTP 1.1, keep alive is the default, and client and server only drops connection when explicitly requested and on timeout.

Upon hearing that HTTP is stateless, you might then assume that HTTP uses a new connection for every request. This is incorrect. HTTP is stateless because every request is independent of any other request whether they are transported through the same connection or a different connection. In other words **every request contains all information (even if just a token that represents the full context) that is needed to process that request.**

As a real life analogy, a stateless communication is like radio conversation between pilot and ground controllers, where you're expected to always state your callsign and usually the callsign of the message destination with every spurt of messages. On the other hand, a stateful protocol is like a telephone conversation, where you rely that the person on the other side to remember who you are.

