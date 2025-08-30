#include "Arduino.h"

#define BUZZER_PIN 21
#define LEDC_CHANNEL 0
#define LEDC_TIMER_RESOLUTION 12  // 12-bit resolution
#define LEDC_BASE_FREQ 5000       // Base frequency for LEDC timer

void setup() {
    ledcAttach(BUZZER_PIN, LEDC_BASE_FREQ, LEDC_TIMER_RESOLUTION);
}

void playToneWithVolume(int frequency, int volume) {
    // Volume should be between 0-100
    if (volume < 0) volume = 0;
    if (volume > 100) volume = 100;
    int dutyCycle = map(volume, 0, 100, 0, 4095);  // 12-bit: 0-4095
    ledcWriteTone(BUZZER_PIN, frequency);
    ledcWrite(BUZZER_PIN, dutyCycle);
}

void stopTone() {
    ledcWrite(BUZZER_PIN, 0); // Set duty cycle to 0 to stop the tone
}

void loop() {
    // Play tone at 1000Hz with 10% volume
    playToneWithVolume(1000, 10);
    delay(500);
    
    stopTone();
    delay(1000);
}