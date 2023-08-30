
# Bright Sky API Dokumentation

Die Bright Sky API ist eine öffentliche Wetter-API, die aktuelle und historische Wetterdaten bereitstellt. Diese Dokumentation erklärt, wie man den `current_weather` Endpunkt der API aufruft, um aktuelle Wetterdaten für einen bestimmten Ort abzurufen.

## Endpunkt: `current_weather`

**URL**: `https://api.brightsky.dev/current_weather`

**Methode**: GET

### Anforderungsparameter

Die API erfordert die Angabe von geographischen Koordinaten oder Stations-IDs, um den Ort festzulegen, für den Sie Wetterdaten abrufen möchten. 

- `lat`: Breitengrad in Dezimalgraden.
- `lon`: Längengrad in Dezimalgraden.
- `dwd_station_id`: DWD-Station-ID.
- `wmo_station_id`: WMO-Station-ID.
- `source_id`: Bright Sky-Quell-ID.

### Beispielaufforderung

Ein `curl` Aufruf zur Bright Sky API's `current_weather` Endpunkt mit den Koordinaten von Mindelheim könnte so aussehen:

```bash
curl "https://api.brightsky.dev/current_weather?lat=48.05&lon=10.48"
```

### Antwortinterpretation

Die API gibt eine JSON-Antwort zurück, die sowohl aktuelle Wetterdaten als auch Metainformationen zu deren Quellen enthält. 

Beispielantwort:

```json
{
  "weather": {
    "source_id": 9914,
    "timestamp": "2023-07-16T11:30:00+00:00",
    "cloud_cover": 100,
    "condition": "dry",
    "dew_point": 12.43,
    "temperature": 21.7,
    "icon": "cloudy"
  }
}
```

In diesem Beispiel gibt `source_id` die ID der Quelle der Wetterdaten an, `timestamp` ist der Zeitpunkt, zu dem die Daten erfasst wurden, `cloud_cover` ist die prozentuale Wolkenbedeckung, `condition` beschreibt den aktuellen Wetterzustand, `dew_point` ist der Taupunkt in Grad Celsius, `temperature` ist die aktuelle Temperatur in Grad Celsius und `icon` gibt einen Hinweis auf die allgemeinen Wetterbedingungen (z. B. "cloudy" für bewölkt).
