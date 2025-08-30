#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuration constants
const char* WIFI_SSID = "Hamza";
const char* WIFI_PASSWORD = "12345678999";
const char* API_URL = "https://i-remember.onrender.com/api/i-remember";
const char* API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2ZXJpZmllZCI6dHJ1ZSwiZXhwIjo0MzQ4NTYyNTE1LCJkYXRhIjoiMjJjZTAwNTgtZTJmNi00OTc3LWEwMjAtMTU3ZjYyNjM4MTJjIn0.jFEjzc09XvQm8mUrqxaSbRZWa0cvDnxiWy3alYwrHf0";

const int BUZZER_PIN = 21;
const unsigned long CHECK_INTERVAL = 5000;
const unsigned long WIFI_TIMEOUT = 10000;
const int HTTP_TIMEOUT = 5000;
const int BUZZER_FREQ = 2000;
const int BUZZER_VOLUME = 50;

void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < WIFI_TIMEOUT) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed!");
  }
}

void setup() {
  Serial.begin(115200);
  ledcAttach(BUZZER_PIN, BUZZER_FREQ, 12);
  connectToWiFi();
}

void ensureWiFiConnection() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected, reconnecting...");
    connectToWiFi();
  }
}

void setupHTTPClient(HTTPClient& http) {
  http.begin(API_URL);
  http.addHeader("Authorization", API_KEY);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(HTTP_TIMEOUT);
}

void playBuzzer() {
  ledcChangeFrequency(BUZZER_PIN, BUZZER_FREQ, 12);
  ledcWrite(BUZZER_PIN, map(BUZZER_VOLUME, 0, 100, 50, 2048));
}

void stopBuzzer() {
  ledcWrite(BUZZER_PIN, 0);
}

void playNotification() {
  for (int i = 0; i < 2; i++) {
    playBuzzer();
    delay(80);
    stopBuzzer();
    if (i < 1) delay(50);
  }
}

bool checkNotification() {
  ensureWiFiConnection();
  if (WiFi.status() != WL_CONNECTED) return false;

  HTTPClient http;
  setupHTTPClient(http);

  int responseCode = http.GET();
  String response = http.getString();
  Serial.println("Response: " + response);
  
  bool hasNotification = false;

  if (responseCode == 200) {
    JsonDocument doc;
    if (deserializeJson(doc, response) == DeserializationError::Ok) {
      if (doc["detail"]["data"]["notify"] == 1) {
        Serial.println("Notification received!");
        updateNotifyStatus();
        hasNotification = true;
      }
    }
  } else if (responseCode > 0) {
    Serial.println("HTTP Error: " + String(responseCode));
  }
  
  http.end();
  return hasNotification;
}

void updateNotifyStatus() {
  HTTPClient http;
  setupHTTPClient(http);

  JsonDocument doc;
  doc["data"]["notify"] = 0;
  
  String payload;
  serializeJson(doc, payload);
  
  int responseCode = http.PUT(payload);
  if (responseCode != 200 && responseCode > 0) {
    Serial.println("Update failed: " + String(responseCode));
  }
  
  String response = http.getString();
  Serial.println("Response: " + response);
  
  http.end();
}

void loop() {
  static unsigned long lastCheck = 0;
  
  if (millis() - lastCheck >= CHECK_INTERVAL) {
    lastCheck = millis();
    
    if (checkNotification()) {
      playNotification();
    }
  }

  vTaskDelay(10);
}