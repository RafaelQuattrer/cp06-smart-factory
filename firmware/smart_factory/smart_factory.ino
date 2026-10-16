#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHTesp.h>
#include <math.h>
#include "config.h"
#include "edge_logic.h"

DHTesp dht;
struct Reading { float temperature; float humidity; bool alert; };
QueueHandle_t readings;

// Rede em uma tarefa separada: um connect() lento nunca bloqueia DHT/LEDs.
void networkTask(void *parameter) {
  WiFiClient wifi;
  PubSubClient mqtt(wifi);
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setBufferSize(512);
  mqtt.setSocketTimeout(2);
  mqtt.setKeepAlive(30);
  String clientId = "cp06-esp32-" + String((uint32_t)(ESP.getEfuseMac() >> 32), HEX)
                    + String((uint32_t)ESP.getEfuseMac(), HEX)
                    + "-" + String(esp_random(), HEX);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  unsigned long wifiAttempt = millis();
  unsigned long mqttAttempt = millis() - 5000;
  for (;;) {
    unsigned long now = millis();
    if (WiFi.status() != WL_CONNECTED) {
      if (now - wifiAttempt >= 10000) {
        wifiAttempt = now;
        WiFi.disconnect();
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
        Serial.println("[REDE] Tentando WiFi; LEDs continuam locais.");
      }
    } else if (!mqtt.connected()) {
      if (now - mqttAttempt >= 5000) {
        mqttAttempt = now;
        if (mqtt.connect(clientId.c_str())) {
          Serial.printf("[MQTT] Conectado. Topico: %s\n", MQTT_TOPIC);
        } else {
          Serial.printf("[MQTT] Falha %d. Nova tentativa em 5 s.\n", mqtt.state());
        }
      }
    } else {
      mqtt.loop();
      Reading reading;
      if (xQueueReceive(readings, &reading, 0) == pdTRUE) {
        char payload[128];
        // Precisão suficiente para não arredondar 35.01 para 35.0 com ALERTA.
        snprintf(payload, sizeof(payload),
                 "{\"temperatura\":%.2f,\"umidade\":%.2f,\"estado\":\"%s\"}",
                 reading.temperature, reading.humidity, reading.alert ? "ALERTA" : "NORMAL");
        bool sent = mqtt.publish(MQTT_TOPIC, payload, false); // QoS 0, sem retain
        Serial.printf("[MQTT %s] %s\n", sent ? "ENVIADO" : "FALHOU", payload);
      }
    }
    vTaskDelay(pdMS_TO_TICKS(20));
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  dht.setup(DHT_PIN, DHTesp::DHT22);
  readings = xQueueCreate(1, sizeof(Reading));
  if (readings == nullptr || xTaskCreate(networkTask, "mqtt-network", 6144, nullptr, 1, nullptr) != pdPASS) {
    Serial.println("[ERRO] Rede indisponivel. Controle local segue ativo.");
  }
  Serial.println("CP06 Smart Factory | leitura e decisao locais a cada 5 s");
}

void loop() {
  static unsigned long lastRead = millis(); // aguarda estabilização do DHT22
  unsigned long now = millis();
  if (now - lastRead >= SAMPLE_INTERVAL_MS) {
    lastRead = now;
    TempAndHumidity value = dht.getTempAndHumidity();
    if (!isfinite(value.temperature) || !isfinite(value.humidity)
        || value.temperature < -40 || value.temperature > 80
        || value.humidity < 0 || value.humidity > 100) {
      Serial.println("[DHT22] Leitura invalida; nao publicada. LEDs preservam ultimo estado.");
    } else {
      bool alert = isAlert(value.temperature);
      digitalWrite(RED_LED_PIN, alert ? HIGH : LOW);
      digitalWrite(GREEN_LED_PIN, alert ? LOW : HIGH);
      Serial.printf("[EDGE] %.2f C | %.2f %% | %s\n", value.temperature, value.humidity,
                    alert ? "ALERTA" : "NORMAL");
      Reading reading = {value.temperature, value.humidity, alert};
      if (readings != nullptr) xQueueOverwrite(readings, &reading);
    }
  }
  delay(10);
}
