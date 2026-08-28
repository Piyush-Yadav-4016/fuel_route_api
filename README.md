# Fuel Route API

A Django REST API and browser map for planning fuel-efficient routes between two US locations.

## Run locally

```powershell
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Open the map at http://127.0.0.1:8000/.

## Route API

`GET /api/route/` returns usage information in JSON.

Send route coordinates with a JSON `POST` request to `/api/route/`:

```json
{
  "start": { "lat": 37.7749, "lon": -122.4194 },
  "finish": { "lat": 34.0522, "lon": -118.2437 }
}
```

The response includes route distance, duration, geometry, recommended fuel stops, and total fuel cost.

Example with PowerShell:

```powershell
$body = @{
  start = @{ lat = 37.7749; lon = -122.4194 }
  finish = @{ lat = 34.0522; lon = -118.2437 }
} | ConvertTo-Json

Invoke-RestMethod http://127.0.0.1:8000/api/route/ `
  -Method Post -ContentType "application/json" -Body $body
```

## Tests

```powershell
python manage.py test routing.tests
```
