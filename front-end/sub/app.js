let mqttClient;

window.addEventListener("load", (event) => {
  connectToBroker();

  const subscribeBtn = document.querySelector("#subscribeBtn");
  subscribeBtn.addEventListener("click", function () {
    subscribeToTopic();
  });

  const unsubscribeBtn = document.querySelector("#unsubscribeBtn");
  unsubscribeBtn.addEventListener("click", function () {
    unsubscribeToTopic();
  });
});

function connectToBroker() {
  const clientId = "client" + Math.random().toString(36).substring(7);

  // Change this to point to your MQTT broker
  const host = "ws://192.168.0.100:8080";

  const options = {
    keepalive: 60,
    clientId: clientId,
    protocolId: "MQTT",
    protocolVersion: 4,
    clean: true,
    reconnectPeriod: 1000,
    connectTimeout: 30 * 1000,
  };

  mqttClient = mqtt.connect(host, options);

  mqttClient.on("error", (err) => {
    console.log("Error: ", err);
    mqttClient.end();
  });

  mqttClient.on("reconnect", () => {
    console.log("Reconnecting...");
  });

  mqttClient.on("connect", () => {
    console.log("Client connected:" + clientId);
  });

  // Received
  mqttClient.on("message", (topic, message, packet) => {
    console.log(
      "Received Message: " + message.toString() + "\nOn topic: " + topic
    );
    const data = JSON.parse(message.toString());
    updateCharts(data);
    updateDisplay(data);
  });
}

function subscribeToTopic() {
  const status = document.querySelector("#status");
  const topic = "sensor_data"; // Adjust this to your topic
  console.log(`Subscribing to Topic: ${topic}`);

  mqttClient.subscribe(topic, { qos: 0 });
  status.style.color = "green";
  status.textContent = "SUBSCRIBED";
}

function unsubscribeToTopic() {
  const status = document.querySelector("#status");
  const topic = "sensor_data"; // Adjust this to your topic
  console.log(`Unsubscribing to Topic: ${topic}`);

  mqttClient.unsubscribe(topic, { qos: 0 });
  status.style.color = "red";
  status.textContent = "UNSUBSCRIBED";
}

const temperatureChartCtx = document
  .getElementById("temperatureChart")
  .getContext("2d");
const illuminanceChartCtx = document
  .getElementById("illuminanceChart")
  .getContext("2d");
const humidityChartCtx = document
  .getElementById("humidityChart")
  .getContext("2d");
const uvChartCtx = document.getElementById("uvChart").getContext("2d");

const temperatureChart = new Chart(temperatureChartCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Air Temperature",
        borderColor: "rgba(255, 99, 132, 1)",
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
  },
});

const illuminanceChart = new Chart(illuminanceChartCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Illuminance",
        borderColor: "rgba(54, 162, 235, 1)",
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
  },
});

const humidityChart = new Chart(humidityChartCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Humidity",
        borderColor: "rgba(75, 192, 192, 1)",
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
  },
});

const uvChart = new Chart(uvChartCtx, {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Ultraviolet",
        borderColor: "rgba(153, 102, 255, 1)",
        backgroundColor: "rgba(153, 102, 255, 0.2)",
        data: [],
      },
    ],
  },
  options: {
    responsive: true,
  },
});

function updateCharts(data) {
  const currentTime = new Date().toLocaleTimeString();

  // Update Temperature Chart
  addDataToChart(temperatureChart, currentTime, data["Air Temperature"]);

  // Update Illuminance Chart
  addDataToChart(illuminanceChart, currentTime, data["Illuminance"]);

  // Update Humidity Chart
  addDataToChart(humidityChart, currentTime, data["Humidity"]);

  // Update UV Chart
  addDataToChart(uvChart, currentTime, data["Ultraviolet"]);
}

function addDataToChart(chart, label, data) {
  chart.data.labels.push(label);
  chart.data.datasets.forEach((dataset) => {
    dataset.data.push(data);
  });
  chart.update();
}

function updateDisplay(data) {
  document.getElementById(
    "airTempValue"
  ).textContent = `${data["Air Temperature"]} °C`;
  document.getElementById(
    "illuminanceValue"
  ).textContent = `${data["Illuminance"]} lux`;
  document.getElementById(
    "humidityValue"
  ).textContent = `${data["Humidity"]} %`;
  document.getElementById("uvValue").textContent = `${data["Ultraviolet"]} UV`;
}
