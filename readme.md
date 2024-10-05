Ideas


As per usual, this project got complicated real quick

I need to decide is this just a jsonrpc toolkit or a full blown framework.


As of now my goal would be to support client and server jsonrpc
as well as supporting both wsgi and asgi interfaces.

I am not sure if this is too much for a single repo, but I hope it isn't

For the client side, I might only need to support the creation of a jsonrpc request
    payload and converting an error response into an exception. The client can choose
    the actual http (or websocket) library for actually sending the request over the network.


The server side is more complicated obviously.
I thought it was a good idea to use the well known Werkzeug library for WSGI and using
    Starlette for ASGI since those are the leaders in their respective domain.

I like the idea of creating modular components for basic server side taks such as
method dispatching and exception handling.
