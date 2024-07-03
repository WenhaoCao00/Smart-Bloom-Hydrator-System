import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

void main() async {
  final client = MqttServerClient('localhost', '');
  client.port = 1883;
  client.logging(on: true);

  // 设置连接所需参数
  client.keepAlivePeriod = 60;
  client.onConnected = onConnected;
  client.onDisconnected = onDisconnected;
  client.onSubscribed = onSubscribed;
  client.onSubscribeFail = onSubscribeFail;
  client.onUnsubscribed = onUnsubscribed;
  client.pongCallback = pong;

  final connMessage = MqttConnectMessage()
      .withClientIdentifier('dart_client')
      .startClean()
      .withWillQos(MqttQos.atLeastOnce);
  client.connectionMessage = connMessage;

  try {
    await client.connect();
  } catch (e) {
    print('Exception: $e');
    client.disconnect();
  }

  if (client.connectionStatus!.state == MqttConnectionState.connected) {
    print('MQTT client connected');
  } else {
    print(
        'ERROR: MQTT client connection failed - disconnecting, state is ${client.connectionStatus!.state}');
    client.disconnect();
    return;
  }

  // 订阅主题
  const topic = 'test_sensor_data';
  client.subscribe(topic, MqttQos.atLeastOnce);

  // 发布消息
  const pubTopic = 'test_sensor_data';
  final builder = MqttClientPayloadBuilder();
  builder.addString('Hello from Dart');
  client.publishMessage(pubTopic, MqttQos.exactlyOnce, builder.payload!);

  // 等待消息到达
  client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> c) {
    final MqttPublishMessage message = c[0].payload as MqttPublishMessage;
    final payload =
        MqttPublishPayload.bytesToStringAsString(message.payload.message);

    print('Received message:$payload from topic: ${c[0].topic}>');
  });

  // // 保持连接一段时间，以便接收消息
  // await MqttUtilities.asyncSleep(1000);

  // // 断开连接
  // client.disconnect();
}

void onConnected() {
  print('Connected');
}

void onDisconnected() {
  print('Disconnected');
}

void onSubscribed(String? topic) {
  print('Subscribed topic: $topic');
}

void onSubscribeFail(String? topic) {
  print('Failed to subscribe $topic');
}

void onUnsubscribed(String? topic) {
  print('Unsubscribed topic: $topic');
}

void pong() {
  print('Ping response client callback invoked');
}
