# SwiftDeploy CLI 🚀

**SwiftDeploy** is a lightweight, Python-based DevOps orchestration tool designed to automate the deployment of containerized services with built-in support for **Canary releases**, **Chaos Engineering**, and **Automated Health Monitoring**.

## 🛠 Features
*   **Infrastructure as Code (IaC):** Generate Nginx and Docker Compose configurations from a single `manifest.yaml` source of truth.
*   **Canary Deployment:** Seamlessly toggle between `normal` and `canary` modes using the `promote` command.
*   **Chaos Engineering:** Built-in API to simulate network latency and service errors for resilience testing.
*   **Security-First:** Docker images run as a non-privileged `swiftuser` to minimize the attack surface.
*   **Observability:** Custom Nginx log formatting for structured, pipe-separated monitoring.

---

##  Project Structure
```text
.
├── app/
│   ├── main.py            # FastAPI/Flask Application with Chaos Logic
│   └── requirements.txt   # Python Dependencies
├── templates/
│   ├── docker-compose.yml.j2
│   └── nginx.conf.j2      # Jinja2 Templates for Orchestration
├── Dockerfile             # Optimized <300MB non-root image
├── manifest.yaml          # Service Configuration (Single Source of Truth)
├── swiftdeploy            # Main CLI Executable
└── README.md
```

---

##  Getting Started

### 1. Installation
Ensure you have Python 3.10+ and Docker/Docker Compose installed.
```bash
# Clone the repository
git clone <your-repo-link>
cd swift-deploy-project

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install PyYAML Jinja2
chmod +x swiftdeploy
```

### 2. Deployment Lifecycle
```bash
# Initialize configurations
./swiftdeploy init

# Validate manifest integrity
./swiftdeploy validate

# Deploy the stack
./swiftdeploy deploy

# Promote to Canary
./swiftdeploy promote canary
```

---

##  Resilience & Chaos Testing
Once the service is deployed, you can test system resilience using the following endpoints:

**Simulate Latency (5s delay):**
```bash
curl -X POST http://localhost:8081/chaos -H "Content-Type: application/json" -d '{"mode": "slow", "duration": 5}'
```

**Simulate 50% Error Rate:**
```bash
curl -X POST http://localhost:8081/chaos -H "Content-Type: application/json" -d '{"mode": "error", "rate": 0.5}'
```

**Recover to Normal State:**
```bash
curl -X POST http://localhost:8081/chaos -H "Content-Type: application/json" -d '{"mode": "recover"}'
```

---

##  Verification Commands

### Log Inspection
Check for the custom pipe-separated log format:
```bash
docker logs swift-deploy-project-nginx-1 --tail 10
```
*Expected Output Format:* `TIMESTAMP | STATUS | TIME | UPSTREAM_ADDR | REQUEST`

### Security Check
Confirm the service is running as a non-root user:
```bash
docker exec swift-deploy-project-api-service-1 whoami
# Output: swiftuser
```

### Cleanup
To remove all generated files and stop containers:
```bash
./swiftdeploy teardown --clean
```

---

##  Configuration (manifest.yaml)
```yaml
app_name: "api-service"
version: "1.0.0"
port: 8081
image: "swift-deploy-1-node:latest"
mode: "normal"  # normal or canary
```

---

**Developed by Ugwu Samuel E bube**  
*HNG14 Stage 4A DevOps Task*