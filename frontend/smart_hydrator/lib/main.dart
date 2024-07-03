import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:smart_hydrator/state/hydrator_state_mqtt.dart';

void main() {
  runApp(const ProviderScope(child: MyApp()));
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Hydrator System',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends ConsumerWidget {
  const MyHomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.read(mqttServiceProvider); // 这行代码会触发 MQTT 服务的初始化和连接

    final hydratorState = ref.watch(hydratorProvider);

    return Scaffold(
      appBar: AppBar(title: Text('Smart Hydrator System')),
      body: Column(
        children: [
          Text('Temperature: ${hydratorState.sensorData.temperature} °C'),
          Text('Humidity: ${hydratorState.sensorData.humidity} %'),
          Text('Light: ${hydratorState.sensorData.light} LUX'),
          Text('UV Index: ${hydratorState.sensorData.uvIndex}'),
          Text('Weather Forecast: ${hydratorState.weatherData.forecast}'),
          Text(
              'Weather Temperature: ${hydratorState.weatherData.temperature} °C'),
        ],
      ),
    );
  }
}
