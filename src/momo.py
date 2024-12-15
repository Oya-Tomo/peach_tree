from subprocess import Popen, PIPE
import os
from os.path import expanduser


MOMO_PATH = os.environ["MOMO_PATH"]


def momo(
    bus: str,
    port: int,
):
    process = Popen(
        f'exec ./momo --no-audio-device --video-device "{bus}" test --port {port}',
        cwd=f"{MOMO_PATH}",
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
    )
    return process


if __name__ == "__main__":
    process = None
    try:
        process = momo(
            bus="usb-0000:00:14.0-5",
            port=8000,
        )
        process.wait()
    except KeyboardInterrupt as e:
        process.kill()
