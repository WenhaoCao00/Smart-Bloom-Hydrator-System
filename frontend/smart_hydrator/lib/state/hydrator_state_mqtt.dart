import 'dart:async';
import 'dart:convert';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';
import 'dart:developer' as developer;

// 状态类定义
class SensorData {
  final double temperature;
  final double humidity;
  final double light;
  final double uvIndex;

  SensorData({
    required this.temperature,
    required this.humidity,
    required this.light,
    required this.uvIndex,
  });

  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      temperature: json['temperature'],
      humidity: json['humidity'],
      light: json['light'],
      uvIndex: json['uvIndex'],
    );
  }
}

class WeatherData {
  final String forecast;
  final double temperature;

  WeatherData({
    required this.forecast,
    required this.temperature,
  });

  factory WeatherData.fromJson(Map<String, dynamic> json) {
    return WeatherData(
      forecast: json['forecast'],
      temperature: json['temperature'],
    );
  }
}

class HydratorState {
  final SensorData sensorData;
  final WeatherData weatherData;

  HydratorState({
    required this.sensorData,
    required this.weatherData,
  });
}

// StateNotifier 定义
class HydratorNotifier extends StateNotifier<HydratorState> {
  HydratorNotifier()
      : super(
          HydratorState(
            sensorData: SensorData(
                temperature: 0.0, humidity: 0.0, light: 0.0, uvIndex: 0.0),
            weatherData: WeatherData(forecast: '', temperature: 0.0),
          ),
        );

  void updateSensorData(SensorData newSensorData) {
    state = HydratorState(
      sensorData: newSensorData,
      weatherData: state.weatherData,
    );
  }

  void updateWeatherData(WeatherData newWeatherData) {
    state = HydratorState(
      sensorData: state.sensorData,
      weatherData: newWeatherData,
    );
  }
}

final hydratorProvider =
    StateNotifierProvider<HydratorNotifier, HydratorState>((ref) {
  return HydratorNotifier();
});

// MQTT 服务
class MQTTService {
  final Ref ref;
  final client = MqttServerClient('192.168.0.103', '');

  MQTTService(this.ref) {
    _setupClient();
  }

  void _setupClient() {
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
  }

  Future<void> connect() async {
    try {
      await client.connect();
    } catch (e) {
      print('Exception: $e');
      client.disconnect();
      return;
    }

    if (client.connectionStatus!.state == MqttConnectionState.connected) {
      developer.log('MQTT client connected');
      _subscribeToTopics();
    } else {
      developer.log(
          'ERROR: MQTT client connection failed - disconnecting, state is ${client.connectionStatus!.state}');
      client.disconnect();
    }
  }

  void disconnect() {
    client.disconnect();
  }

  void _subscribeToTopics() {
    const topic = 'test_sensor_data';
    client.subscribe(topic, MqttQos.atLeastOnce);
    final builder = MqttClientPayloadBuilder();
    builder.addString('Hello from flutter');
    client.publishMessage(topic, MqttQos.exactlyOnce, builder.payload!);

    client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> c) {
      final MqttPublishMessage message = c[0].payload as MqttPublishMessage;
      final payload =
          MqttPublishPayload.bytesToStringAsString(message.payload.message);
      developer.log('Received message:$payload from topic: ${c[0].topic}>');
      _handleMessage(c[0].topic, payload);
    });
  }

  void _handleMessage(String topic, String payload) {
    final data = jsonDecode(payload);

    if (topic == 'test_sensor_data') {
      // final sensorData = SensorData.fromJson(data);
      // ref.read(hydratorProvider.notifier).updateSensorData(sensorData);
      developer.log('Received sensor data: $data');
    }
  }

  void onConnected() {
    developer.log('Connected');
  }

  void onDisconnected() {
    developer.log('Disconnected');
  }

  void onSubscribed(String? topic) {
    developer.log('Subscribed topic: $topic');
  }

  void onSubscribeFail(String? topic) {
    developer.log('Failed to subscribe $topic');
  }

  void onUnsubscribed(String? topic) {
    developer.log('Unsubscribed topic: $topic');
  }

  void pong() {
    developer.log('Ping response client callback invoked');
  }
}

final mqttServiceProvider = Provider((ref) {
  final service = MQTTService(ref);
  service.connect(); // 连接到 MQTT 服务器
  ref.onDispose(() {
    service.disconnect(); // 在 Provider 销毁时断开连接
  });
  return service;
});
