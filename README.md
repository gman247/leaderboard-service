# leaderboard-service
Flask app to prepend leaderboard entries to Outline
# Leaderboard Service for Netwrix Xchange

This Flask app prepends leaderboard entries to a Markdown document hosted in Outline (Netwrix Xchange Wiki).

## API

### POST /prepend-entry

Send JSON:

```json
{
  "name": "Jane Doe",
  "score": 92,
  "date": "2025-06-02",
  "highlights": [
    "Strong discovery",
    "Handled objections well"
  ]
}
