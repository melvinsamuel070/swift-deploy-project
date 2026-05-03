import os
import time
import random
from flask import Flask, jsonify, request

app = Flask(__name__)
start_time = time.time()

# Configuration from Environment
# Injected via Docker Compose by the CLI
MODE = os.getenv("MODE", "stable").lower()
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_PORT = int(os.getenv("APP_PORT", 3000))

# Global Chaos State
chaos_config = {"mode": "normal", "duration": 0, "rate": 0}

@app.route('/')
def home():
    response_data = {
        "message": "Welcome to SwiftDeploy API",
        "mode": MODE,
        "version": APP_VERSION,
        "timestamp": time.time()
    }
    
    response = jsonify(response_data)
    
    # Requirement: Canary mode adds "X-Mode: canary" to every response
    if MODE == "canary":
        response.headers["X-Mode"] = "canary"
        
    return response

@app.route('/healthz')
def health():
    uptime = time.time() - start_time
    # Requirement: liveness check returning status and process uptime in seconds
    return jsonify({
        "status": "healthy", 
        "uptime": int(uptime),
        "mode": MODE
    })

@app.route('/chaos', methods=['POST'])
def chaos():
    # Requirement: Chaos endpoint only active in Canary mode
    if MODE != "canary":
        return jsonify({"error": "Chaos endpoint is only active in canary mode"}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    incoming_mode = data.get("mode")

    if incoming_mode == "recover":
        chaos_config["mode"] = "normal"
        chaos_config["duration"] = 0
        chaos_config["rate"] = 0
        return jsonify({"message": "Chaos recovered to normal state"})

    if incoming_mode in ["slow", "error"]:
        chaos_config.update(data)
        return jsonify({"message": f"Chaos updated to {incoming_mode}"})

    return jsonify({"error": "Unsupported chaos mode"}), 400

@app.before_request
def apply_chaos():
    # Only apply chaos if we are in canary mode
    if MODE == "canary":
        # Mode: slow -> sleep N seconds
        if chaos_config["mode"] == "slow":
            duration = chaos_config.get("duration", 0)
            time.sleep(float(duration))
            
        # Mode: error -> return 500 on ~X% of requests
        elif chaos_config["mode"] == "error":
            rate = chaos_config.get("rate", 0)
            if random.random() < float(rate):
                return jsonify({
                    "error": "Simulated Chaos Error",
                    "code": 500,
                    "service": "api-service"
                }), 500

if __name__ == '__main__':
    # Listen on 0.0.0.0 so Docker can route traffic to it
    app.run(host='0.0.0.0', port=APP_PORT)