import asyncio
import os.path
from datetime import datetime
from pprint import pprint

import h5py
import numpy as np

import cortex

CLIENT_ID = "Your Client ID"
CLIENT_SECRET = "Your Secret"
LICENSE = "Your License"


class EEGListener(cortex.Listener):
    def __init__(self):
        self.current_tick = 0
        self.data = list()

    @cortex.Listener.handler("eeg")
    def handle_eeg(self, data):
        self.current_tick += 1
        self.data.append([self.current_tick] + data["eeg"][2:7])

        pprint(data["eeg"])

    @cortex.Listener.handler("close")
    def handle_close(self, data):
        time_format = datetime.now().strftime("%Y-%m-%d(%H%M%S)")
        file_dir = "eeg"
        filename = f"{file_dir}/raw_eeg_{time_format}.h5"

        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)

        with h5py.File(filename, "w") as h5f:
            h5f.create_dataset("dataset_1", data=np.array(self.data))
            h5f.close()

        pprint(data)

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE)
    def handle_subscribe(self, data):
        pprint(data)

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.UNSUBSCRIBE)
    def handle_unsubscribe(self, data):
        pprint(data)


if __name__ == "__main__":
    async def main():
        headset = await api.get_headset()
        token, session = await api.prepare(headset=headset, _license=LICENSE)

        # 데이터 취득 시작
        await api.subscribe(token, session, ["eeg"])
        # 30초 대기
        await asyncio.sleep(30)
        # 데이터 취득 종료
        await api.unsubscribe(token, session, ["eeg"])
        api.exit()


    listener = EEGListener()

    api = cortex.Wrapper(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, main=main)
    api.register_listener(listener)

    api.run()
