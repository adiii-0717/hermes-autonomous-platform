# HERMES DEV STUDIO — DOCKER ISOLATION ARCHITECTURE

## 1. Executive Summary

Hermes Dev Studio employs a multi-tiered security defense to protect host infrastructure when executing generated project code, terminal scripts, and automated build tools.

The architecture combines **Application-Level Security Guardrails ()** with **OS-Level Container Isolation ()**.

---

## 2. Sandbox Runtime Options: Docker vs. gVisor

| Feature / Criteria | Docker () | gVisor () | Firecracker MicroVM |
| :--- | :--- | :--- | :--- |
| **Isolation Boundary** | Linux Namespaces, Cgroups, Seccomp | User-space Kernel Sentry | Hardware Virtualization (KVM) |
| **Performance Overhead** | Minimal (< 1% CPU / RAM) | Low-Medium (10-15% Syscall overhead) | Medium (Sub-second boot, VM isolation) |
| **Kernel Attack Surface** | Shared Host Linux Kernel | Intercepted Syscalls (Sentry Layer) | Isolated Guest Kernel |
| **Public Multi-Tenant Fit** | Recommended for Staging & Internal Beta | **Recommended for Untrusted Public Launch** | Ideal for High-Risk Untrusted Code Execution |

### Architectural Recommendation
- **Staging / Internal Beta**: Default Docker  container with capability dropping () and read-only filesystems.
- **Untrusted Public Production**: Configure  to use **gVisor (runsc)**, shielding the host Linux kernel from potential container escape vulnerabilities.

---

## 3. Container Resource & Security Limits

Every containerized worker process launched via  is restricted by default to:



### Enforced Protection Profiles

1. **Unprivileged Execution**: Drops all 38 default Linux capabilities ().
2. **Privilege Escalation Prevention**: Prevents gain of new privileges via SUID/SGID binaries ().
3. **Immutability**: Root filesystem is strictly read-only (). Temporary work is routed to an in-memory  mounted with .
4. **Volume Containment**: Volume mounting is strictly scoped to . Mounting , , , or parent project paths is prohibited by .
5. **Resource Cap**: Max 1.0 vCPU core, 512MB RAM, and 64 max child processes ().

---

## 4. Graceful Host Bounded Fallback

If the Docker daemon is unreachable or disabled (),  seamlessly falls back to **WorkspaceGuard Bounded Host Execution**:

- **Path Verification**:  enforces  canonical containment.
- **Command Classification**: Dangerous commands (, , ) are blocked at application tier.
- **Secret Sanitization**: Environment variables (, ) are stripped before subprocess invocation.
- **Execution Timeouts**: Subprocesses are killed after 30s timeout interval.

---

## 5. Security Boundary & Residual Risks

> [!WARNING]
> **Residual Risk Disclosure**:
> 1. **Standard Docker ()**: Shares host Linux kernel. In public untrusted deployments, kernel zero-days could allow container escape unless gVisor () or MicroVMs are used.
> 2. **Network Egress**: Internal container default is . If network access is required for package installations (), outbound traffic should be routed through a strictly monitored egress proxy.