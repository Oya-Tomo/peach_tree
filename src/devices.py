import subprocess
import re
import pprint
from pydantic import BaseModel


class Device(BaseModel):
    name: str
    bus: str


def get_usb_buses() -> list[Device]:
    try:
        output = subprocess.check_output(["v4l2-ctl", "--list-devices"]).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return []

    lines = output.split("\n")
    devices = []
    for line in lines:
        if "usb" in line:
            name = re.search(r"(.*\(usb-.*\))", line).group(1)
            bus = re.search(r"\((usb-.*)\):", line).group(1)
            devices.append(Device(name=name, bus=bus))
    return devices


if __name__ == "__main__":
    pprint.pprint(get_usb_buses())
