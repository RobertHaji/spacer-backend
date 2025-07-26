from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Adjust if deploying

# Sample venue data
spaces = [
    {
        "id": 1,
        "name": "Uasin Gishu Hall",
        "location": "Uasin Gishu",
        "activity": "Meeting",
        "available_date": "2025-07-28",
        "description": "Spacious hall with modern amenities.",
        "address": "Eldoret CBD, near Zion Mall"
    },
    {
        "id": 2,
        "name": "Nairobi Conference Room",
        "location": "Nairobi",
        "activity": "Wedding",
        "available_date": "2025-08-01",
        "description": "Elegant space for formal weddings and receptions.",
        "address": "Upper Hill, Nairobi"
    },
    {
        "id": 3,
        "name": "Kisumu Open Grounds",
        "location": "Kisumu",
        "activity": "Concert",
        "available_date": "2025-07-28",
        "description": "Outdoor space suitable for large public events.",
        "address": "Milimani Area, Kisumu"
    },
]

@app.route("/api/venues")
def search_spaces():
    activity = request.args.get("activity")
    location = request.args.get("location")
    date = request.args.get("date")

    print("Received search:", activity, location, date)

    # Filter results
    results = [
        s for s in spaces
        if (not activity or s["activity"].lower() == activity.lower())
        and (not location or s["location"].lower() == location.lower())
        and (not date or s["available_date"] == date[:10])
    ]

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
