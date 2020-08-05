import logging
import threading
import time

import matplotlib.animation as animation
import matplotlib.pyplot as plt

import cortex

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

CLIENT_ID = "Your client id"
CLIENT_SECRET = "Your Client Secret"


class AF7Listener(cortex.Listener):
    cols = dict()

    def __init__(self):
        self.ref_time = time.time()
        self.x = [0 for x in range(200)]
        self.theta = [0 for x in range(200)]
        self.alpha = [0 for x in range(200)]
        self.betaL = [0 for x in range(200)]
        self.betaH = [0 for x in range(200)]
        self.gamma = [0 for x in range(200)]
        self.raw = [0 for x in range(200)]

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE, is_success=True)
    def handle_subscribe(self, data):
        for stream in data["success"]:
            self.cols[stream["streamName"]] = stream["cols"]
        print(self.cols)

    @cortex.Listener.handler(cortex.ID.SUBSCRIPTION.SUBSCRIBE, is_success=False)
    def handle_subscribe_error(self, data):
        print(data)

    @cortex.Listener.handler("pow")
    def handle_pow(self, data):
        print(data)
        self.__handle_pow(data["pow"], data["sid"], data["time"])

    def __handle_pow(self, data, sid, time):
        self.x.pop(0)
        self.alpha.pop(0)
        self.betaL.pop(0)
        self.betaH.pop(0)
        self.gamma.pop(0)
        self.theta.pop(0)
        # self.raw.pop(0)

        self.x.append(time - self.ref_time)
        self.theta.append(data[0])
        self.alpha.append(data[1])
        self.betaL.append(data[2])
        self.betaH.append(data[3])
        self.gamma.append(data[4])
        # self.raw.append(np.fft.irfft([data[0], data[1], data[2], data[3], data[4]], n=1))


if __name__ == "__main__":
    h = AF7Listener()

    fig, ax = plt.subplots()
    legend = plt.legend()


    def animate(i):
        ax.clear()
        ax.set_title("AF7")
        ax.plot(h.x, h.theta, "m", label="theta")
        ax.plot(h.x, h.alpha, "r", label="alpha")
        ax.plot(h.x, h.betaL, "c", label="betaL")
        ax.plot(h.x, h.betaH, "b", label="betaH")
        ax.plot(h.x, h.gamma, "y", label="gamma")
        # ax.plot(h.x, h.raw, "k", label="eeg")
        ax.legend()


    async def main():
        token, session = await api.prepare()
        await api.subscribe(token, session, ["pow"])


    api = cortex.Wrapper(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, main=main)
    api.register_listener(h)
    threading.Thread(target=api.run).start()
    ani = animation.FuncAnimation(fig, animate, interval=500)
    plt.show()
