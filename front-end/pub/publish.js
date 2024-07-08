let mqttClient;

window.addEventListener("load", (event) => {
  connectToBroker();

  const publishBtn = document.querySelector("#publishBtn");
  publishBtn.addEventListener("click", function () {
    publishConfig();
  });

  document.querySelector("#circleOnBtn").addEventListener("click", function () {
    publishCircle("circle_on");
  });
  document
    .querySelector("#circleOffBtn")
    .addEventListener("click", function () {
      publishCircle("circle_off");
    });

  document
    .querySelector("#circlePlusOnBtn")
    .addEventListener("click", function () {
      publishCircle("circle_plus_on");
    });

  document
    .querySelector("#circlePlusOffBtn")
    .addEventListener("click", function () {
      publishCircle("circle_plus_off");
    });

  const subscribeBtn = document.querySelector("#subscribe");
  subscribeBtn.addEventListener("click", function () {
    publishAndSubscribeToTopic();
  });

  const unsubscribeBtn = document.querySelector("#unsubscribe");
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
    try {
      const msg = JSON.parse(message.toString());
      const tableName = msg.table_name;
      const dataList = msg.data;

      const messageTextArea = document.querySelector("#message");
      messageTextArea.value += `Table Name: ${tableName}\n`;

      dataList.forEach((dataItem, index) => {
        messageTextArea.value += `Data ${index + 1}:\n`;
        for (const [key, value] of Object.entries(dataItem)) {
          messageTextArea.value += `  ${key}: ${value}\n`;
        }
      });
      messageTextArea.value += "\n";
    } catch (e) {
      console.error("Failed to parse message", e);
      const messageTextArea = document.querySelector("#message");
      messageTextArea.value += "Received invalid JSON message.\n";
    }

    console.log(
      "Received Message: " + message.toString() + "\nOn topic: " + topic
    );
  });
}

function publishConfig() {
  const config_d = {
    max_temp: parseFloat(document.querySelector("#max_temp").value),
    min_temp: parseFloat(document.querySelector("#min_temp").value),
    max_mois: parseFloat(document.querySelector("#max_mois").value),
    min_mois: parseFloat(document.querySelector("#min_mois").value),
    enough_light_time:
      parseFloat(document.querySelector("#enough_light_time").value) * 60,
    single_water_time: parseFloat(
      document.querySelector("#single_water_time").value
    ),
    single_light_time: parseFloat(
      document.querySelector("#single_light_time").value
    ),
    trigger_period: parseFloat(document.querySelector("#trigger_period").value),
  };

  const topic = "config";
  mqttClient.publish(topic, JSON.stringify(config_d), { qos: 0 });
  //clear the form
  document.querySelectorAll("input").forEach((input) => {
    input.value = "";
  });
}

function publishCircle(message) {
  const topic = "plugwise";
  console.log(`Sending Topic: ${topic}, Message: ${message}`);
  mqttClient.publish(topic, message, { qos: 0, retain: false });
}

function publishAndSubscribeToTopic() {
  const status = document.querySelector("#status");
  const pubTopic = "get_db";
  const subTopic = "db_data";
  const payload = document.querySelector("#payload").value.trim();

  // Subscribe to the topic first to ensure we don't miss any messages
  console.log(`Subscribing to Topic: ${subTopic}`);
  mqttClient.subscribe(subTopic, { qos: 0 }, (err) => {
    if (err) {
      console.error(`Failed to subscribe to ${subTopic}`, err);
      status.style.color = "red";
      status.value = "SUBSCRIBE FAILED";
    } else {
      status.style.color = "green";
      status.value = "SUBSCRIBED";

      // Now publish the payload
      console.log(`Publishing to Topic: ${pubTopic}`);
      mqttClient.publish(pubTopic, payload, { qos: 0 }, (err) => {
        if (err) {
          console.error(`Failed to publish to ${pubTopic}`, err);
          status.style.color = "red";
          status.value = "PUBLISH FAILED";
        } else {
          console.log(`Published to ${pubTopic}`);
        }
      });
    }
  });
}

function unsubscribeToTopic() {
  const status = document.querySelector("#status");
  const subTopic = "db_data";
  console.log(`Unsubscribing to Topic: ${subTopic}`);

  mqttClient.unsubscribe(subTopic, { qos: 0 });
  status.style.color = "red";
  status.value = "UNSUBSCRIBED";
}
