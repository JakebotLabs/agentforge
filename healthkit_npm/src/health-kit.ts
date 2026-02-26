/**
 * @agentsforge/healthkit - HealthKit Client
 * 
 * REST client for the HealthKit API server.
 */

import type {
  HealthKitOptions,
  HealthStatus,
  DriftReport,
  ClusterReport,
  ValidationResult,
} from './types';

/**
 * HealthKit - REST client for agent health monitoring.
 * 
 * @example
 * ```typescript
 * import { HealthKit } from '@agentsforge/healthkit';
 * 
 * const kit = new HealthKit({ host: 'http://localhost:7842' });
 * const status = await kit.getStatus();
 * console.log(status.drift_risk);
 * ```
 */
export class HealthKit {
  private readonly host: string;
  private readonly apiKey?: string;
  private readonly timeout: number;

  constructor(options: HealthKitOptions = {}) {
    this.host = options.host ?? 'http://localhost:7842';
    this.apiKey = options.apiKey;
    this.timeout = options.timeout ?? 10000;
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
   * Make API request with timeout.
   */
  private async request<T>(
    method: string,
    path: string,
    body?: unknown
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.host}${path}`, {
        method,
        headers: this.getHeaders(),
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(`HealthKit API error (${response.status}): ${error}`);
      }

      return await response.json() as T;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Get overall health status of the cluster.
   * 
   * @returns HealthStatus with cluster-wide metrics
   */
  async getStatus(): Promise<HealthStatus> {
    return this.request<HealthStatus>('GET', '/api/v1/cluster/status');
  }

  /**
   * Get current soul drift metrics.
   * 
   * @param threshold - Alert threshold (0-1, default 0.15)
   * @returns DriftReport with drift analysis
   */
  async getDriftRisk(threshold = 0.15): Promise<DriftReport> {
    return this.request<DriftReport>(
      'GET',
      `/api/v1/drift?threshold=${threshold}`
    );
  }

  /**
   * Check cluster configuration and health.
   * 
   * @param configPath - Path to cluster.yaml
   * @returns ClusterReport with health and validation info
   */
  async checkCluster(configPath?: string): Promise<ClusterReport> {
    const query = configPath ? `?config_path=${encodeURIComponent(configPath)}` : '';
    
    const [health, validation] = await Promise.all([
      this.request<HealthStatus>('GET', `/api/v1/cluster/status${query}`),
      this.request<ValidationResult>('GET', `/api/v1/cluster/validate${query}`),
    ]);

    return { health, validation };
  }

  /**
   * Check if API server is reachable.
   * 
   * @returns true if server responds
   */
  async ping(): Promise<boolean> {
    try {
      await this.request<{ status: string }>('GET', '/api/v1/health');
      return true;
    } catch {
      return false;
    }
  }
}
