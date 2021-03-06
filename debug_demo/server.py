#!/usr/bin/env python3

import datetime
import logging
import asyncio
import aiocoap.resource as resource
import aiocoap

class BlockResource(resource.Resource):
    def __init__(self):
        super(BlockResource, self).__init__()
        self.content = ("Constrained Application Protocol (CoAP) is a software protocol "\
            "intended to be used in very simple electronics devices, "\
            "allowing them to communicate interactively over the Internet. "\
            "It is particularly targeted for small, low-power sensors, switches, valves "
            "and similar components that need to be controlled or supervised remotely, "\
            "through standard Internet networks. CoAP is an application layer protocol "\
            "that is intended for use in resource-constrained internet devices, "\
            "such as WSN nodes. CoAP is designed to easily translate to HTTP "\
            "for simplified integration with the web, "\
            "while also meeting specialized requirements such as multicast support, "\
            "very low overhead, and simplicity.[Multicast, low overhead, "\
            "and simplicity are extremely important for Internet of Things (IoT) "\
            "and Machine-to-Machine (M2M) devices, "\
            "which tend to be deeply embedded and have much less memory "\
            "and power supply than traditional internet devices have. "\
            "Therefore, efficiency is very important. "\
            "CoAP can run on most devices that support UDP or a UDP analogue.\n").encode("ascii")

    @asyncio.coroutine
    def render_get(self, request):
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=self.content)
        return response

    @asyncio.coroutine
    def render_put(self, request):
        print('PUT payload: %s' % request.payload)
        self.content = request.payload
        payload = ("accepted the new payload. You may inspect it here in "\
                "Python's repr format:\n\n%r" % self.content).encode('utf8')
        response = aiocoap.Message(code=aiocoap.CHANGED, payload=self.content)
        return response

class SeparateLargeResource(resource.Resource):
    def __init__(self):
        super(SeparateLargeResource, self).__init__()

    @asyncio.coroutine
    def render_get(self, request):
        yield from asyncio.sleep(3)

        payload = "CoAP is an open Internet standard for the Web of Things."\
                " It's based on the Web's core pipe: HTTP, "\
                "but has many differences to allow it to be used "\
                "by very resource-constrained devices "\
                "and local radio networks.".encode('ascii')
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

class TimeResource(resource.ObservableResource):
    def __init__(self):
        super(TimeResource, self).__init__()

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(5, self.notify)

    def update_observation_count(self, count):
        if count:
            # not that it's actually implemented like that here -- unconditional updating works just as well
            print("Keeping the clock nearby to trigger observations")
        else:
            print("Stowing away the clock until someone asks again")

    @asyncio.coroutine
    def render_get(self, request):
        payload = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode('ascii')
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

# logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    root = resource.Site()
    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('time',), TimeResource())
    root.add_resource(('other', 'block'), BlockResource())
    root.add_resource(('other', 'separate'), SeparateLargeResource())
    asyncio.async(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main()