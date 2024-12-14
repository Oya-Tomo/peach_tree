document.addEventListener("DOMContentLoaded", async (event) => {
  await updateDeviceList();
});

async function updateDeviceList() {
  var list = document.getElementById("devices");

  var hostname = window.location.hostname;

  var data = await fetch("/devices", {
    method: "GET",
  })
    .then((response) => response.json())
    .then((json) => json);

  list.innerHTML = "";
  data.forEach((device) => {
    var deviceElement = document.createElement("li");
    var deviceState = `
    <div>
        <div class="name">${device.name}</div>
        <span class="status">
            status:
            <span>${device.status}</span>
        </span>
        ${
          device.status == "running"
            ? `
                <span class="port">
                    port:
                    <a href="http://${hostname}:${device.port}/html/test.html" target="_blank" rel="noopener noreferrer">${device.port}</a>
                </span>
                `
            : `
                <span class="port">
                    port:
                    <span>${device.port}</span>
                </span>
                `
        }

    </div>`;

    var deviceAction =
      device.status == "stopped"
        ? `
        <div>
            <button class="start" onclick="startDevice('${device.bus}')">Start</button>
        </div>
        `
        : `
        <div>
            <button class="stop" onclick="stopDevice('${device.bus}')">Stop</button>
        </div>`;

    deviceElement.innerHTML = deviceState + deviceAction;
    list.appendChild(deviceElement);
  });
}

async function startDevice(bus) {
  await fetch("/launch", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bus: bus }),
  }).then(() => {
    updateDeviceList();
  });
}

async function stopDevice(bus) {
  await fetch("/stop", {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bus: bus }),
  }).then(() => {
    updateDeviceList();
  });
}
