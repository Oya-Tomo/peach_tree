from subprocess import Popen, PIPE
from os.path import expanduser

home = expanduser("~")


def momo(
    bus: str,
    port: int,
):
    process = Popen(
        f'./momo --no-audio-device --video-device "{bus}" test --port {port}',
        cwd=f"{home}/Downloads/momo",
        user="oyatomo",
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
