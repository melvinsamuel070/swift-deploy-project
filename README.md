# SwiftDeploy CLI 

SwiftDeploy is a declarative DevOps orchestration tool that automates the deployment and lifecycle management of containerized services. It generates infrastructure configurations dynamically from a single source of truth (`manifest.yaml`) and manages deployments using Docker and Nginx.

---

##  Architecture Overview

SwiftDeploy follows a **declarative infrastructure model**:

* `manifest.yaml` → defines desired system state
* `swiftdeploy` CLI → generates configs + controls lifecycle
* Docker → runs services in isolated containers
* Nginx → acts as a reverse proxy and entry point

All traffic flows through Nginx → API service (no direct exposure of the service port).

---

##  Project Structure

.
├── app/
│   ├── main.py
│   └── requirements.txt
├── templates/
│   ├── docker-compose.yml.j2
│   └── nginx.conf.j2
├── Dockerfile
├── manifest.yaml
├── swiftdeploy
└── README.md
```



##  Manifest Configuration (Single Source of Truth)

```yaml
services:
  image: swift-deploy-1-node:latest
  port: 3000
  mode: stable
  version: "1.0.0"

nginx:
  image: nginx:latest
  port: 8081
  proxy_timeout: 60

network:
  name: swiftdeploy-net
  driver_type: bridge
```

---

##  CLI Commands

### 1. Initialize

```bash
./swiftdeploy init
```

* Parses `manifest.yaml`
* Generates `nginx.conf` and `docker-compose.yml`

---

### 2. Validate

```bash
./swiftdeploy validate
```

Performs pre-flight checks:

* Valid YAML structure
* Required fields present
* Docker image exists locally
* Nginx port availability
* Valid Nginx configuration

---

### 3. Deploy

```bash
./swiftdeploy deploy
```

* Runs `init`
* Starts containers using Docker Compose
* Waits until `/healthz` confirms service readiness

---

### 4. Promote (Canary / Stable)

```bash
./swiftdeploy promote canary
./swiftdeploy promote stable
```

* Updates deployment mode in `manifest.yaml`
* Regenerates configs
* Restarts only the API container (rolling update)
* Verifies mode via `/healthz`

---

### 5. Teardown

```bash
./swiftdeploy teardown --clean
```

* Stops and removes containers, volumes, and networks
* Deletes generated configuration files

---

##  Canary Deployment Strategy

SwiftDeploy supports controlled rollout using **canary deployments**:

* Same container image runs in different modes (`stable` or `canary`)
* Mode is injected via environment variables
* Canary mode:

  * Adds `X-Mode: canary` header
  * Enables `/chaos` endpoint
* Promotion updates only the service container without downtime

---

##  API Endpoints

| Endpoint   | Description                                         |
| ---------- | --------------------------------------------------- |
| `/`        | Returns service metadata (mode, version, timestamp) |
| `/healthz` | Health check with uptime                            |
| `/chaos`   | Simulates failures (canary mode only)               |

---

##  Chaos Engineering

Simulate failures:

```bash
# Slow response
curl -X POST http://localhost:8081/chaos \
-H "Content-Type: application/json" \
-d '{"mode": "slow", "duration": 5}'

# Random errors
curl -X POST http://localhost:8081/chaos \
-H "Content-Type: application/json" \
-d '{"mode": "error", "rate": 0.5}'

# Recover
curl -X POST http://localhost:8081/chaos \
-H "Content-Type: application/json" \
-d '{"mode": "recover"}'
```

---

##  Observability

### Nginx Access Logs Format

```
$time_iso8601 | $status | ${request_time}s | $upstream_addr | $request
```

Example:

```
2026-05-03T21:42:13+00:00 | 200 | 0.005s | 172.21.0.2:3000 | GET / HTTP/1.1
```

---

##  Security Best Practices

* Containers run as non-root user (`swiftuser`)
* Linux capabilities dropped
* Service port is not exposed directly
* Only Nginx is publicly accessible

---

##  Verification

### Check headers

```bash
curl -i http://localhost:8081/
```

Expected:

```
X-Deployed-By: swiftdeploy
X-Mode: canary
```

---

### Check logs

```bash
docker logs swift-deploy-project-nginx-1
```

---

### Check container user

```bash
docker exec swift-deploy-project-api-service-1 whoami
```

---

##  Setup

```bash
git clone <your-repo-link>
cd swift-deploy-project

python3 -m venv venv
source venv/bin/activate

pip install PyYAML Jinja2
chmod +x swiftdeploy
```

---

##  Author

**Ugwu Samuel E Bube**
HNG14 DevOps Track — Stage 4A
