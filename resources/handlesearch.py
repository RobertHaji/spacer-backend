# from flask import Flask, jsonify, request
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)


# @app.route("/spaces", methods=["GET"])
# def get_spaces():
    
#     activity = request.args.get("activity")
#     location = request.args.get("location")

    
#     filtered = spaces

#     if activity:
#         filtered = [s for s in filtered if s["activity"].lower() == activity.lower()]
#     if location:
#         filtered = [s for s in filtered if s["location"].lower() == location.lower()]

#     return jsonify(filtered)

# if __name__ == "__main__":
#     app.run(debug=True)
