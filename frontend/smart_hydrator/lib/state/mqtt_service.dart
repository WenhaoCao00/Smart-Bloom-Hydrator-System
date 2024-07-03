import 'dart:async';
import 'dart:convert';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
//import 'hydrator_state.dart';
import 'hydrator_state_mqtt.dart';
import 'dart:io';

final client = MqttServerClient('localhost', ''); //add address

class MQTTService {
  final WidgetRef ref;
  MQTTService(this.ref) {
    _setupClient();
  }

  void _setupClient() {
    client.logging(on: false);
    client.setProtocolV311();
    client.keepAlivePeriod = 20;
    client.connectTimeoutPeriod = 2000;
    client.port = 1883;
    client.securityContext = SecurityContext.defaultContext;
    client.onDisconnected = onDisconnected;
    client.onConnected = onConnected;
    client.onSubscribed = onSubscribed;
    client.pongCallback = pong;
  }

  Future<void> connect() async {
    final connMess = MqttConnectMessage()
        .withClientIdentifier('Mqtt_MyClientUniqueId')
        .withWillTopic('willtopic')
        .withWillMessage('My Will message')
        .startClean()
        .withWillQos(MqttQos.atLeastOnce);

    print('Connecting to MQTT broker...');
    client.connectionMessage = connMess;

    try {
      await client.connect();
    } on Exception catch (e) {
      print('Client exception - $e');
      client.disconnect();
    }

    if (client.connectionStatus!.state == MqttConnectionState.connected) {
      print('MQTT client connected');
      _subscribeToTopics();
    } else {
      print(
          'ERROR: MQTT client connection failed - disconnecting, status is ${client.connectionStatus}');
      client.disconnect();
    }
  }

  void disconnect() {
    client.disconnect();
  }

  void _subscribeToTopics() {
    print('Subscribing to topics...');
    client.subscribe('sensor_data', MqttQos.atMostOnce);
    client.subscribe('weather_data', MqttQos.atMostOnce);

    client.updates!.listen((List<MqttReceivedMessage<MqttMessage?>>? c) {
      final recMess = c![0].payload as MqttPublishMessage;
      final pt =
          MqttPublishPayload.bytesToStringAsString(recMess.payload.message);
      print(
          'Change notification:: topic is <${c[0].topic}>, payload is <-- $pt -->');
      _handleMessage(c[0].topic, pt);
    });

    client.published!.listen((MqttPublishMessage message) {
      print(
          'Published notification:: topic is ${message.variableHeader!.topicName}, with Qos ${message.header!.qos}');
    });
  }

  void _handleMessage(String topic, String payload) {
    final data = jsonDecode(payload);

    if (topic == 'sensor/data') {
      final sensorData = SensorData.fromJson(data);
      ref.read(hydratorProvider.notifier).updateSensorData(sensorData);
    } else if (topic == 'weather/data') {
      final weatherData = WeatherData.fromJson(data);
      ref.read(hydratorProvider.notifier).updateWeatherData(weatherData);
    }
  }

  void onSubscribed(String topic) {
    print('EXAMPLE::Subscription confirmed for topic $topic');
  }

  void onDisconnected() {
    print('OnDisconnected client callback - Client disconnection');
    if (client.connectionStatus!.disconnectionOrigin ==
        MqttDisconnectionOrigin.solicited) {
      print('OnDisconnected callback is solicited, this is correct');
    }
  }

  void onConnected() {
    print('OnConnected client callback - Client connection was successful');
  }

  void pong() {
    print('Ping response client callback invoked');
  }
}
