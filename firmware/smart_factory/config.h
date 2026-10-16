#pragma once
constexpr char WIFI_SSID[] = "Wokwi-GUEST";
constexpr char WIFI_PASSWORD[] = "";
constexpr char MQTT_HOST[] = "broker.hivemq.com";
constexpr uint16_t MQTT_PORT = 1883;
// Mesmo tópico em compose.yaml, .env.example e README.md.
constexpr char MQTT_TOPIC[] = "edge/2ano/turma-pendente/equipe-pendente/cp06-4f8ab7c291e64396/dados";
constexpr uint8_t DHT_PIN = 15;
constexpr uint8_t GREEN_LED_PIN = 18;
constexpr uint8_t RED_LED_PIN = 19;
constexpr unsigned long SAMPLE_INTERVAL_MS = 5000;
