/**
 * @agentsforge/healthkit - Type Definitions
 * 
 * TypeScript interfaces for cluster configuration and health monitoring.
 */

// ============================================================================
// Cluster Configuration Types
// ============================================================================

/**
 * Global anchor configuration for identity files.
 */
export interface GlobalAnchor {
  path: string;
  priority?: 'high' | 'medium' | 'low';
  persistence?: 'locked' | 'volatile';
}

/**
 * Orchestration configuration.
 */
export interface OrchestrationConfig {
  version?: string;
  global_anchors?: GlobalAnchor[];
}

/**
 * Individual agent configuration.
 */
export interface AgentConfig {
  id: string;
  identity_path?: string;
  memory_buffer?: number;
  context_isolation?: boolean;
}

/**
 * Sync protocol configuration.
 */
export interface SyncProtocolConfig {
  mode?: 'differential' | 'full' | 'none';
  frequency?: 'real-time' | 'periodic' | 'manual';
}

/**
 * Health check configuration.
 */
export interface HealthCheckConfig {
  auto_fix_overflow?: boolean;
  alert_on_soul_drift?: boolean;
  soul_drift_threshold?: number;
}

/**
 * Complete cluster configuration (cluster.yaml).
 */
export interface ClusterConfig {
  cluster_id: string;
  orchestration?: OrchestrationConfig;
  agents: AgentConfig[];
  sync_protocol?: SyncProtocolConfig;
  health_check?: HealthCheckConfig;
}

// ============================================================================
// Health Status Types
// ============================================================================

/**
 * Health status for a single agent.
 */
export interface AgentHealthStatus {
  id: string;
  status: 'healthy' | 'warning' | 'critical';
  drift_score: number;
  identity_tokens: number;
  context_tokens: number;
}

/**
 * Cluster-wide health status.
 */
export interface HealthStatus {
  status: 'Locked' | 'Warning' | 'Critical' | 'Unknown';
  drift_risk: string;
  header_efficiency: string;
  agents: AgentHealthStatus[];
  timestamp: string;
  cluster_id: string;
}

/**
 * Soul drift analysis report.
 */
export interface DriftReport {
  soul_drift_risk: 'low' | 'medium' | 'high';
  drift_score: number;
  identity_tokens: number;
  context_tokens: number;
  threshold: number;
  alert: boolean;
  message: string;
}

/**
 * Cluster validation result.
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

/**
 * Deployment result.
 */
export interface DeploymentResult {
  success: boolean;
  cluster_id: string;
  agents_deployed: number;
  message: string;
  details: Record<string, unknown>;
}

/**
 * Cluster status report (combines health + validation).
 */
export interface ClusterReport {
  health: HealthStatus;
  validation: ValidationResult;
}

// ============================================================================
// Client Options
// ============================================================================

/**
 * Options for HealthKit client initialization.
 */
export interface HealthKitOptions {
  /** API host URL (default: http://localhost:7842) */
  host?: string;
  /** API key for authentication (optional) */
  apiKey?: string;
  /** Request timeout in ms (default: 10000) */
  timeout?: number;
}

/**
 * Options for ClusterManager initialization.
 */
export interface ClusterManagerOptions {
  /** API host URL (default: http://localhost:7842) */
  host?: string;
  /** API key for authentication (optional) */
  apiKey?: string;
  /** Workspace path for local-only mode */
  workspacePath?: string;
  /** Enable local-only mode (no API server required) */
  localOnly?: boolean;
}
