import asyncio
import logging
import threading

import rpyc

import cortex

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

CLIENT_ID = "Your Client ID"
CLIENT_SECRET = "Your Client Secret"
PROFILE = "Your Emotiv training Profile"
EV3_HOST = "EV3 Ip address"


class CommandListener(cortex.Listener):
    def __init__(self, host):
        self.host = host
        self.conn = rpyc.classic.connect(host)
        self.ev3motor = self.conn.modules["ev3dev2.motor"]
        self.motor = self.ev3motor.LargeMotor(self.ev3motor.OUTPUT_A)
        self.state = ""

    @cortex.Listener.handler("com")
    def handle_command(self, data):
        print(data)
        cmd, power = data["com"]
        if cmd != self.state:
            if cmd == "lift":
                self.motor.on(power * 50)
            elif cmd == "neutral":
                self.motor.off()
        self.state = cmd

    @cortex.Listener.handler("close")
    def handle_close(self, data):
        print("close")
        self.motor.off()
        self.conn.close()


if __name__ == "__main__":
    async def main():
        headset = await api.get_headset()
        token, session = await api.prepare(headset=headset)
        if not await api.get_current_profile_id(token, headset):
            if PROFILE in (await api.query_profile(token)).values():
                await api.load_profile(token, headset, PROFILE)
            else:
                raise RuntimeError("The Profile is not exist")

        await api.subscribe(token, session, ["com"])
        await asyncio.sleep(300)  # Run 300 secs
        await api.unsubscribe(token, session, ["com"])
        api.exit()


    api = cortex.Wrapper(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, main=main)
    api.register_listener(CommandListener(EV3_HOST))
    threading.Thread(target=api.run).start()
