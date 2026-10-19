# HERMES DEV STUDIO — PRODUCTION & STAGING DEPLOYMENT GUIDE

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 22.04 LTS / Debian 12 / RHEL 9) or macOS.
- **Python**: Python 3.10+ (Python 3.11 or 3.12 recommended).
- **Container Engine**: Docker 24.0+ (Optional: gVisor `runsc` plugin for untrusted public launch).
- **Reverse Proxy**: Nginx 1.22+ or Caddy 2.7+.
- **Node.js**: Node 20 LTS (For frontend Vite build).

---

## 2. Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables in `.env`:
   ```ini
   PORT=8000
   GEMINI_API_KEY=your_production_gemini_api_key
   HERMES_ENABLE_DOCKER=true
   HERMES_DOCKER_IMAGE=node:20-alpine
   HERMES_DOCKER_CPU_LIMIT=1.0
   HERMES_DOCKER_MEMORY_LIMIT=512m
   HERMES_DOCKER_PIDS_LIMIT=64
   HERMES_SANDBOX_RUNTIME=runc
   ```

3. Install Python Dependencies:
   ```bash
   pip install -r server/requirements.txt
   ```

---

## 3. Reverse Proxy & SSL Setup

### Nginx Production Deployment
1. Copy Nginx configuration:
   ```bash
   sudo cp scripts/nginx_production.conf /etc/nginx/sites-available/hermes.conf
   sudo ln -s /etc/nginx/sites-available/hermes.conf /etc/nginx/sites-enabled/
   ```

2. Obtain TLS Certificate via Certbot:
   ```bash
   sudo certbot --nginx -d hermesdevstudio.com -d www.hermesdevstudio.com
   ```

3. Test and reload Nginx:
   ```bash
   sudo nginx -t && sudo nginx -s reload
   ```

---

## 4. Startup & Shutdown Commands

### Startup
```bash
./scripts/startup.sh
```

### Shutdown
```bash
./scripts/shutdown.sh
```

---

## 5. Staging-to-Production Migration Checklist

- [ ] `.env` updated with production API keys and `HERMES_ENABLE_DOCKER=true`.
- [ ] Docker daemon active and verified (`docker info`).
- [ ] TLS certificate active and SSL auto-renew configured (`certbot renew --dry-run`).
- [ ] Nginx rate limiting enabled (`limit_req_zone`).
- [ ] Health check endpoint monitored (`GET https://hermesdevstudio.com/api/health`).
- [ ] Backup cron job enabled for `.sessions_db.json` and `.project_manifest.json`.