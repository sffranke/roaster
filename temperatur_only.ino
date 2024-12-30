#include "MAX6675.h"

const int dataPin   = 7;
const int clockPin  = 6;
const int selectPin = 5;

MAX6675 thermoCouple(selectPin, dataPin, clockPin);

float lastTemperature = -999.0;   // speichert die letzte plausible Temperatur
bool  firstReading    = true;     // Flag, um beim allerersten Lesen keinen Filter anzuwenden

void setup()
{
  Serial.begin(115200);
  SPI.begin();
  thermoCouple.begin();
}

void loop()
{
  // status != STATUS_OK --> Fehler beim Auslesen
  // z.B. thermCouple.read() liefert das Status-Flag
  int status = thermoCouple.read();
  // Serial.println(status);
  if (status != STATUS_OK)
  {
    Serial.println("ERROR (Thermocouple status)!");
    delay(1000);
    return;  
  }

  // Aktuelle Temperatur
  float currentTemperature = thermoCouple.getTemperature();

  // Hier kannst du zusätzliche Plausibilitätschecks einbauen, z.B.:
  //   - Thermoelement kann z.B. nicht < 0°C sein (wenn du keine Minustemperatur hast)
  //   - oder du gibst einen bestimmten max. Temperaturwert an.
  //   - oder du prüfst auf "Sprünge" größer als X °C zwischen zwei Messungen.

  // Beispiel: Sprung größer als 20°C in 0,5s => wahrscheinlich wackelnder Kontakt
  if (!firstReading)
  {
    float diff = fabs(currentTemperature - lastTemperature);
    if (diff > 20.0 || currentTemperature < 0.0 || currentTemperature > 250.0)
    {
      // Unplausibler Wert => ignorieren
      Serial.println("Warnung: Unplausibler Messwert. Wert verworfen.");
    }
    else
    {
      // Wert plausibel => ausgeben und merken
      lastTemperature = currentTemperature;
      Serial.println(currentTemperature, 2);
    }
  }
  else
  {
    // Beim ersten Lesen direkt übernehmen
    lastTemperature = currentTemperature;
    firstReading = false;
    Serial.println(currentTemperature, 1);
  }

  delay(1000);
}
