# HERMES DEV STUDIO — OPERATIONAL TROUBLESHOOTING GUIDE

## 1. Common Operational Scenarios & Resolution

### Scenario A: Docker Daemon Unavailable / Fallback Execution
- **Symptom**: Logs show `Docker execution failed, falling back to host bounded execution`.
- **Root Cause**: Docker service stopped or user lacks permission to access `/var/run/docker.sock`.
- **Resolution**:
  1. Verify Docker status: `sudo systemctl status docker`
  2. Start Docker service: `sudo systemctl start docker`
  3. Ensure app user is in docker group: `sudo usermod -aG docker $USER`

---

### Scenario B: WebSocket Connection Timeout
- **Symptom**: Frontend UI disconnects or drops progress streaming during generation.
- **Root Cause**: Nginx proxy default `proxy_read_timeout` (60s) timed out during complex multi-agent reasoning.
- **Resolution**: Ensure `proxy_read_timeout 600s;` and `proxy_send_timeout 600s;` are set in Nginx location `/ws/` block.

---

### Scenario C: Backend Restart State Recovery
- **Symptom**: Server restarted while project generation was in progress.
- **Resolution**:
  1. Hermes Dev Studio automatically loads `.generation_state.json` on restart.
  2. Run `GET /api/projects` to list active projects.
  3. Send client request with project ID to resume from last cycle checkpoint.

---

## 2. Backup & Restore Procedures

### Database & Manifest Backup
```bash
# Backup persistent session database and project manifests
tar -czvf hermes_backup_\$(date +%Y%m%d).tar.gz .sessions_db.json .project_manifest.json workspace/
```

### Restoration
```bash
# Restore persistent session database and project workspace
tar -xzvf hermes_backup_20261004.tar.gz -C ./
```