#include <WiFi.h>
#include <HTTPClient.h>

// WIFI
const char* ssid = "Elektro Master";
const char* password = "haruscerdas";

// FIREBASE
String firebaseURL = "https://hidroponik-4c359-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json";

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected");
}

void loop() {
  float ph = analogRead(34) * (14.0 / 4095.0);
  float ppm = analogRead(35) * (1000.0 / 4095.0);

  Serial.print("pH: ");
  Serial.print(ph);
  Serial.print(" | PPM: ");
  Serial.println(ppm);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin(firebaseURL);
    http.addHeader("Content-Type", "application/json");

    String json = "{\"ph\":" + String(ph, 2) + ",\"ppm\":" + String(ppm, 0) + "}";

    int response = http.PUT(json);

    Serial.print("Response: ");
    Serial.println(response);

    http.end();
  }

  delay(5000);
}