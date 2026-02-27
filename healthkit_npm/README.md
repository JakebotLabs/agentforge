# @agentsforge/healthkit

[![npm version](https://img.shields.io/npm/v/@agentsforge/healthkit.svg)](https://www.npmjs.com/package/@agentsforge/healthkit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Health monitoring and cluster management for AI agents. Monitor soul drift, manage multi-agent clusters, and ensure agent identity preservation.

## Features

- 🧠 **Soul Drift Detection** — Alert when agent identity files lose weight in context
- 🔄 **Cluster Management** — Deploy and manage multi-agent configurations
- 📊 **Health Monitoring** — Real-time cluster health status via REST API
- ⚡ **Local Mode** — Validate configs without running a server
- 🔌 **Framework Agnostic** — Works with OpenClaw, LangChain, AutoGen, or standalone

## Installation

```bash
npm install @agentsforge/healthkit

# Optional: for YAML config support
npm install yaml
```

## Quick Start

### API Mode (with HealthKit server)

```typescript
import { HealthKit, ClusterManager } from '@agentsforge/healthkit';

// Connect to HealthKit API
const kit = new HealthKit({ host: 'http://localhost:7842' });

// Check cluster health
const status = await kit.getStatus();
console.log(status);
// Output: { status: "Locked", drift_risk: "0%", header_efficiency: "94%" }

// Get soul drift metrics
const drift = await kit.getDriftRisk();
console.log(drift.soul_drift_risk); // "low" | "medium" | "high"
```

### Local Mode (no server required)

```typescript
import { ClusterManager } from '@agentsforge/healthkit';

const config = {
  cluster_id: "my-cluster",
  agents: [
    { id: "main", identity_path: "./SOUL.md", memory_buffer: 4096 },
    { id: "helper", identity_path: "./AGENTS.md", memory_buffer: 2048 }
  ],
  health_check: {
    soul_drift_threshold: 0.15
  }
};

const cluster = new ClusterManager(config, { localOnly: true });

// Validate configuration
const validation = cluster.validate();
console.log(validation);
// Output: { valid: true, errors: [], warnings: [] }

// Deploy (in local mode, this validates only)
const result = await cluster.deploy();
console.log(result.success); // true
```

### With YAML Config

```typescript
import { ClusterManager } from '@agentsforge/healthkit';
import fs from 'fs';

// Load cluster.yaml
const yamlContent = fs.readFileSync('./cluster.yaml', 'utf-8');
const cluster = new ClusterManager(yamlContent);

await cluster.deploy();
const health = await cluster.getHealthStatus();
console.log(health.status); // "Locked"
```

## API Reference

### HealthKit

REST client for the HealthKit API server.

```typescript
const kit = new HealthKit({
  host: 'http://localhost:7842', // API server URL
  apiKey: 'optional-api-key',    // For authenticated endpoints
  timeout: 10000                  // Request timeout (ms)
});

// Methods
await kit.getStatus(): Promise<HealthStatus>
await kit.getDriftRisk(threshold?: number): Promise<DriftReport>
await kit.checkCluster(configPath?: string): Promise<ClusterReport>
await kit.ping(): Promise<boolean>
```

### ClusterManager

Manages multi-agent cluster configuration and health.

```typescript
const cluster = new ClusterManager(config, {
  host: 'http://localhost:7842', // API server URL
  apiKey: 'optional-api-key',    // For authenticated endpoints
  localOnly: false               // true = validation only, no API calls
});

// Methods
cluster.validate(): ValidationResult
await cluster.deploy(): Promise<DeploymentResult>
await cluster.getHealthStatus(): Promise<HealthStatus>
cluster.getConfig(): ClusterConfig
cluster.getClusterId(): string
cluster.getAgentIds(): string[]
```

### loadCluster

Convenience function to create a ClusterManager.

```typescript
import { loadCluster } from '@agentsforge/healthkit';

const cluster = loadCluster(yamlOrJsonString, { localOnly: true });
```

## cluster.yaml Schema

```yaml
cluster_id: "my-cluster"

orchestration:
  version: "2026.1-compat"
  global_anchors:
    - path: "./SOUL.md"
      priority: high
      persistence: locked

agents:
  - id: "primary"
    identity_path: "./SOUL.md"
    memory_buffer: 4096
    context_isolation: true
  
  - id: "aux"
    identity_path: "./AGENTS.md"
    memory_buffer: 2048
    context_isolation: false

sync_protocol:
  mode: "differential"          # differential | full | none
  frequency: "real-time"        # real-time | periodic | manual

health_check:
  auto_fix_overflow: true
  alert_on_soul_drift: true
  soul_drift_threshold: 0.15    # Alert if identity < 15% of context
```

## Types

```typescript
interface HealthStatus {
  status: 'Locked' | 'Warning' | 'Critical' | 'Unknown';
  drift_risk: string;           // "0%", "15%", etc.
  header_efficiency: string;    // "94%", etc.
  agents: AgentHealthStatus[];
  timestamp: string;
  cluster_id: string;
}

interface DriftReport {
  soul_drift_risk: 'low' | 'medium' | 'high';
  drift_score: number;          // 0-1, higher = more identity preserved
  identity_tokens: number;
  context_tokens: number;
  threshold: number;
  alert: boolean;
  message: string;
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}
```

## Soul Drift Explained

**Soul drift** measures how much your agent's identity files (SOUL.md, AGENTS.md) are being diluted by context accumulation (MEMORY.md, conversation history).

```
drift_score = identity_tokens / (identity_tokens + context_tokens)
```

- **drift_score ≥ 0.30**: LOW risk — Identity well preserved
- **drift_score ≥ 0.15**: MEDIUM risk — Monitor context growth
- **drift_score < 0.15**: HIGH risk — Agent losing core identity

When drift is high, consider:
- Trimming MEMORY.md
- Archiving old context
- Increasing identity file content

## Python Backend

This package is a TypeScript client for the Python HealthKit API. Install the full stack:

```bash
# Install AgentForge (includes Python backend)
curl -fsSL https://agentsforge.dev/install.sh | bash

# Or manually
pip install agentforge
agentforge install
```

Start the API server:

```bash
agentforge start
# API available at http://localhost:7842
```

## Requirements

- Node.js 16+
- Optional: `yaml` package for YAML config parsing
- For API mode: Python HealthKit server running

## License

MIT — Free to use, modify, and distribute.

---

Built by [Jakebot Labs](https://jakebotlabs.com) · [AgentForge](https://agentsforge.dev) · [GitHub](https://github.com/JakebotLabs/agentforge)
