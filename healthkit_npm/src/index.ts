/**
 * @agentsforge/healthkit
 * 
 * Health monitoring and cluster management for AI agents.
 * Monitor soul drift, manage multi-agent clusters, and ensure agent identity preservation.
 * 
 * @example Quick Start
 * ```typescript
 * import { HealthKit, ClusterManager } from '@agentsforge/healthkit';
 * 
 * // Monitor health via API
 * const kit = new HealthKit();
 * const status = await kit.getStatus();
 * console.log(status.drift_risk);
 * 
 * // Manage clusters
 * const cluster = new ClusterManager(config);
 * await cluster.deploy();
 * ```
 * 
 * @packageDocumentation
 */

// Re-export all types
export type {
  // Config types
  GlobalAnchor,
  OrchestrationConfig,
  AgentConfig,
  SyncProtocolConfig,
  HealthCheckConfig,
  ClusterConfig,
  // Status types
  AgentHealthStatus,
  HealthStatus,
  DriftReport,
  ValidationResult,
  DeploymentResult,
  ClusterReport,
  // Options
  HealthKitOptions,
  ClusterManagerOptions,
} from './types';

// Export classes
export { HealthKit } from './health-kit';
export { ClusterManager, loadCluster, setYamlParser } from './cluster-manager';

// Default export for convenience
import { HealthKit } from './health-kit';
export default HealthKit;
