/**
 * @agentsforge/healthkit - ClusterManager
 * 
 * Manages multi-agent cluster configuration and health.
 * Works in two modes:
 * - API mode: Talks to the Python FastAPI server
 * - Local mode: Validates cluster.yaml without server
 */

import type {
  ClusterConfig,
  ClusterManagerOptions,
  HealthStatus,
  ValidationResult,
  DeploymentResult,
  AgentHealthStatus,
} from './types';

// YAML parsing function - set externally if yaml package is available
let yamlParse: ((content: string) => unknown) | null = null;

/**
 * Set the YAML parser function.
 * Call this if you want to parse YAML strings directly.
 * 
 * @example
 * ```typescript
 * import { setYamlParser } from '@agentsforge/healthkit';
 * import YAML from 'yaml';
 * setYamlParser(YAML.parse);
 * ```
 */
export function setYamlParser(parser: (content: string) => unknown): void {
  yamlParse = parser;
}

/**
 * ClusterManager - Multi-agent cluster configuration and health management.
 * 
 * @example API Mode (with server):
 * ```typescript
 * import { ClusterManager } from '@agentsforge/healthkit';
 * 
 * const cluster = new ClusterManager(config, { host: 'http://localhost:7842' });
 * await cluster.deploy();
 * console.log(await cluster.getHealthStatus());
 * ```
 * 
 * @example Local Mode (no server):
 * ```typescript
 * import { ClusterManager } from '@agentsforge/healthkit';
 * import config from './cluster.yaml';
 * 
 * const cluster = new ClusterManager(config, { localOnly: true });
 * const validation = cluster.validate();
 * console.log(validation.valid);
 * ```
 */
export class ClusterManager {
  private readonly config: ClusterConfig;
  private readonly host: string;
  private readonly apiKey?: string;
  private readonly localOnly: boolean;

  constructor(
    config: ClusterConfig | string,
    options: ClusterManagerOptions = {}
  ) {
    // Parse config if string (YAML/JSON content)
    if (typeof config === 'string') {
      this.config = this.parseConfig(config);
    } else {
      this.config = config;
    }

    this.host = options.host ?? 'http://localhost:7842';
    this.apiKey = options.apiKey;
    this.localOnly = options.localOnly ?? false;
  }

  /**
   * Parse configuration from string (YAML or JSON).
   */
  private parseConfig(content: string): ClusterConfig {
    // Try YAML first if available
    if (yamlParse) {
      try {
        return yamlParse(content) as ClusterConfig;
      } catch {
        // Fall through to JSON
      }
    }

    // Try JSON
    try {
      return JSON.parse(content) as ClusterConfig;
    } catch (e) {
      throw new Error(`Failed to parse config: ${e}`);
    }
  }

  /**
   * Build request headers.
   */
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    return headers;
  }

  /**
   * Make API request.
   */
  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const response = await fetch(`${this.host}${path}`, {
      method,
      headers: this.getHeaders(),
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`ClusterManager API error (${response.status}): ${error}`);
    }

    return await response.json() as T;
  }

  /**
   * Validate cluster configuration.
   * 
   * Works in both local and API modes.
   */
  validate(): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields
    if (!this.config.cluster_id) {
      errors.push('Missing required field: cluster_id');
    }

    if (!this.config.agents || this.config.agents.length === 0) {
      errors.push('Missing required field: agents (must have at least one agent)');
    }

    // Validate agents
    const agentIds = new Set<string>();
    for (let i = 0; i < (this.config.agents ?? []).length; i++) {
      const agent = this.config.agents[i];
      
      if (!agent.id) {
        errors.push(`Agent ${i}: missing required field 'id'`);
      } else {
        if (agentIds.has(agent.id)) {
          errors.push(`Duplicate agent id: ${agent.id}`);
        }
        agentIds.add(agent.id);
      }

      // Warn about missing identity_path (can't check file existence in browser)
      if (!agent.identity_path) {
        warnings.push(`Agent '${agent.id ?? i}': no identity_path specified`);
      }
    }

    // Validate soul_drift_threshold
    const threshold = this.config.health_check?.soul_drift_threshold;
    if (threshold !== undefined && (threshold < 0 || threshold > 1)) {
      errors.push(`soul_drift_threshold must be between 0 and 1, got: ${threshold}`);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Deploy cluster configuration.
   * 
   * In local mode, performs validation only.
   * In API mode, deploys to the server.
   */
  async deploy(): Promise<DeploymentResult> {
    // Validate first
    const validation = this.validate();
    if (!validation.valid) {
      return {
        success: false,
        cluster_id: this.config.cluster_id ?? 'unknown',
        agents_deployed: 0,
        message: `Validation failed: ${validation.errors.join('; ')}`,
        details: { validation },
      };
    }

    if (this.localOnly) {
      // Local mode - validation passed, simulate deployment
      return {
        success: true,
        cluster_id: this.config.cluster_id,
        agents_deployed: this.config.agents.length,
        message: `Local validation passed for cluster '${this.config.cluster_id}' with ${this.config.agents.length} agents`,
        details: {
          mode: 'local',
          validation_warnings: validation.warnings,
        },
      };
    }

    // API mode - deploy to server
    return this.request<DeploymentResult>('POST', '/api/v1/cluster/deploy', {
      config: this.config,
    });
  }

  /**
   * Get current cluster health status.
   * 
   * In local mode, returns a simulated status based on config.
   * In API mode, fetches real-time status from server.
   */
  async getHealthStatus(): Promise<HealthStatus> {
    if (this.localOnly) {
      // Local mode - return simulated healthy status
      const agents: AgentHealthStatus[] = this.config.agents.map((agent) => ({
        id: agent.id,
        status: 'healthy' as const,
        drift_score: 0.5,
        identity_tokens: 1000,
        context_tokens: 1000,
      }));

      return {
        status: 'Locked',
        drift_risk: '0%',
        header_efficiency: '94%',
        agents,
        timestamp: new Date().toISOString(),
        cluster_id: this.config.cluster_id,
      };
    }

    // API mode
    return this.request<HealthStatus>('GET', '/api/v1/cluster/status');
  }

  /**
   * Get the loaded configuration.
   */
  getConfig(): ClusterConfig {
    return this.config;
  }

  /**
   * Get cluster ID.
   */
  getClusterId(): string {
    return this.config.cluster_id;
  }

  /**
   * Get list of agent IDs.
   */
  getAgentIds(): string[] {
    return this.config.agents.map((a) => a.id);
  }
}

/**
 * Load a cluster configuration.
 * 
 * @param config - ClusterConfig object or YAML/JSON string
 * @param options - ClusterManager options
 * @returns Initialized ClusterManager
 */
export function loadCluster(
  config: ClusterConfig | string,
  options?: ClusterManagerOptions
): ClusterManager {
  return new ClusterManager(config, options);
}
