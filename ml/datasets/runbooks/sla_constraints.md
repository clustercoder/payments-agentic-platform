# SLA Constraints

1. Overview
- Scope: incidents that threaten or cause breach of contractual Service Level Agreements (availability, latency, error rate).
- Purpose: provide immediate detection cues, safe mitigations to protect uptime and minimize SLA impact, and guidelines for escalations and customer communications.

2. Common failure patterns
- Sustained p95/p99 latency above SLA thresholds across a service or endpoint.
- Error budget consumption spike: rapid increase in error rates or availability drops.
- Partial outages causing subset of customers to exceed latency guarantees.
- Capacity exhaustion: CPU, memory, DB connections, or network bandwidth saturation.
- Cascading failures from a degraded dependency pushing requests to fallback systems.
- Automated scaling not keeping pace with sudden traffic spikes (cold-start delays).
- Configuration changes or deployments causing regression in performance or errors.

3. Observable signals (metrics/logs)
- SLA alert triggers (p95/p99, success-rate thresholds) and chatops pager firing.
- Error budget burn rate exceeding configured alerting thresholds.
- System resource metrics: CPU, memory, conn counts, thread pools, GC pause durations.
- Latency heatmaps by endpoint, region, customer.
- Increase in queue/backlog sizes and retry worker queues.
- Health-check failures for downstream systems and dependency timeouts.
- Customer-impact metrics: number of active sessions failing, orders failing, revenue delta.
- Recent deployments or config changes preceding SLA degradation.

4. Probable root causes
- Insufficient capacity or poor autoscaling configuration.
- Regressions from recent code or configuration changes.
- Heavy downstream dependency latencies (DB, partner APIs, third-party services).
- Unbounded resource usage in a component (memory leak, connection leak).
- Ineffective load-shedding or absence of graceful degradation strategies.
- DDoS or traffic spikes from legitimate high-volume clients.
- Misrouted traffic due to DNS or load-balancer misconfiguration.

5. Safe mitigation actions
- Activate traffic shaping: reduce non-essential traffic paths (analytics, background jobs).
- Apply graceful degradation: disable non-critical features that are high-cost in compute.
- Engage load shedding: reject lowest-priority requests with clear failure codes to preserve core flows.
- Scale horizontally or vertically where autoscaling is slow — use known safe instance types.
- Route traffic to healthy regions or read-only replicas for read-heavy workloads.
- Roll back recent deployment if telemetry indicates regression and rollback is validated.
- Throttle heavy consumers by merchant or API key to protect overall SLA.
- Open circuit breakers for failing dependencies to prevent cascading failures.
- Implement temporary caching to reduce load on downstream services.
- Preserve detailed incident logs and annotate runbooks with actions taken and observed impact.

6. Actions requiring human approval
- SLA renegotiation or customer compensation (credits, refunds).
- Cross-regional failovers that impact data residency or regulatory constraints.
- Authorizing capacity increases with cost or procurement impact.
- Public/merchant-facing incident communications and postmortem publish.
- Long-term architectural changes that affect SLAs for multiple customers.

7. What NOT to do
- Do not perform piecemeal changes that hide the real issue (workarounds without root cause triage).
- Do not suppress or alter monitoring/alerting to avoid SLA alerts.
- Do not take irreversible data or settlement actions without approvals to “fix” SLA metrics.
- Do not promise SLA remediation timelines to customers without alignment from ops/leadership.

8. Regulatory / compliance notes
- SLA incidents affecting transaction processing may have contractual and regulatory reporting obligations.
- Preserve immutable incident timelines and actions for potential regulatory audits.
- Cross-border failovers or routing changes can trigger data residency or local regulator constraints; consult legal/compliance before making such moves.
- Compensation actions that affect consumer funds or settlement require reconciliation and often legal approval.
- Ensure post-incident reports and RCA meet contractual SLA reporting requirements.
```


# SLA Constraints

## Overview
Service-level agreements define contractual limits for latency,
availability, and error rates. Breaches have operational and
financial consequences.

## Common Failure Patterns
- Sustained latency above SLA thresholds
- Error budget exhaustion
- Partial outages impacting specific regions or merchants
- Cascading failures from shared dependencies
- Silent degradation without full outage

## Observable Signals (Metrics / Logs)
- SLA breach alerts firing
- p95/p99 latency exceeding limits
- Error rate trending toward budget exhaustion
- Increased timeout or queue depth metrics
- Regional or merchant-scoped degradation

## Probable Root Causes
- Traffic spikes beyond capacity planning
- Dependency saturation or outages
- Inefficient fallback paths
- Misconfigured load balancing
- Resource contention or throttling

## Safe Mitigation Actions
- Traffic shaping or rate limiting
- Graceful degradation of non-critical features
- Load shedding for lowest-priority traffic
- Fail open or fail closed based on SLA policy
- Regional isolation to prevent blast radius expansion

## Actions Requiring Human Approval
- SLA renegotiation
- Merchant compensation or credits
- Permanent capacity changes
- Public or merchant incident communication

## What NOT to Do
- Do not hide SLA breaches
- Do not shift traffic blindly without capacity validation
- Do not disable monitoring to suppress alerts

## Regulatory / Compliance Notes
- SLA breaches must be logged and reviewed
- Root cause analysis is mandatory
- Incident timelines must be preserved



# SLA Constraints

## Overview

Service Level Agreements (SLAs) define contractual obligations for payment system performance across latency, availability, throughput, and error rates. SLA breaches trigger financial penalties, merchant churn, and regulatory scrutiny. This runbook addresses detection, mitigation, and escalation procedures when SLA metrics approach or exceed defined thresholds.

**Critical SLA Dimensions:**
- **Latency:** P50, P95, P99, P99.9 response times for authorization, capture, refund operations
- **Availability:** Uptime percentage measured per service component and end-to-end transaction flow
- **Success Rate:** Ratio of successful transactions to total attempts, excluding expected declines
- **Throughput:** Transactions per second (TPS) capacity under normal and peak load conditions
- **Error Budget:** Allowable failure rate over measurement period (typically monthly or quarterly)

**Measurement Windows:**
- Real-time: 1-minute, 5-minute rolling windows for immediate detection
- Operational: 1-hour, 24-hour windows for trend analysis
- Contractual: Monthly, quarterly periods for formal SLA reporting
- Peak period overrides: Special thresholds during known high-traffic events

**Stakeholders Impacted by SLA Breaches:**
- Merchants: Revenue loss, customer experience degradation, contract penalties
- Payment processors: Reputation damage, potential contract termination
- Card networks: Network stability, fraud detection accuracy
- Regulators: Compliance violations if availability affects consumer protection
- Internal teams: On-call burden, incident investigation overhead

---

## Common Failure Patterns

### Latency Degradation Patterns

**Gradual Latency Creep:**
- P95 latency increases by 5-10% daily over 3-5 day period
- Often indicates resource exhaustion (memory leaks, connection pool depletion)
- May not trigger immediate alerts but erodes error budget steadily
- Typically affects specific merchant cohorts or payment methods first
- Root cause often in database query performance or external dependency slowdown

**Sudden Latency Spike:**
- P95 jumps 200-500% within single measurement window (1-5 minutes)
- Usually caused by deployment, traffic surge, or downstream service degradation
- May recover automatically or require intervention
- High correlation with increased retry rates and timeout errors
- Can cascade to availability failures if persistent

**Bimodal Latency Distribution:**
- Two distinct latency populations emerge (e.g., 50ms and 5000ms)
- Indicates partial system degradation affecting subset of requests
- Common causes: database replica lag, regional datacenter issues, partial cache invalidation
- Dangerous because average metrics may appear acceptable while P95/P99 breach SLA
- Requires partition-level analysis to identify affected segment

**Peak Hour Latency Violations:**
- Predictable SLA breaches during known traffic peaks (lunch hours, payday, sales events)
- Indicates insufficient capacity provisioning or lack of auto-scaling
- May be acceptable under "best effort" SLA clauses but signals architectural limitation
- Often combined with increased queue depths and connection timeouts

**Weekend/Off-Peak Degradation:**
- Latency increases during low-traffic periods
- Counter-intuitive pattern suggesting keep-alive issues, cold start problems, or scheduled maintenance conflicts
- May indicate batch processing jobs competing for resources
- Automated scaling policies may reduce capacity too aggressively

### Availability Failure Patterns

**Total Service Outage:**
- 0% success rate across all transaction types
- Hard failures: database unreachable, load balancer misconfiguration, DNS resolution failure
- Immediate SLA breach with maximum severity
- Requires immediate failover or rollback procedures
- Typically detected within 1-2 minute alert windows

**Partial Availability Degradation:**
- 80-95% success rate, indicating subset of requests failing
- Causes: specific database shards down, regional pod failures, partial network partition
- May remain undetected if only aggregate metrics monitored
- Disproportionately affects specific merchants, geographies, or payment methods
- Requires granular monitoring by segment to identify

**Brown-Out Conditions:**
- Success rate oscillates between 50-99% over short intervals
- Indicates system operating at capacity limit with intermittent failures
- Often accompanied by retry storms that worsen the condition
- Circuit breakers may be rapidly opening and closing
- Resource contention between competing workloads

**Cascading Failure:**
- Initial component failure triggers secondary failures across dependent services
- Example: database slowdown causes connection pool exhaustion, leading to application timeouts, triggering retry storms
- Failure propagates upstream to API gateway and load balancer
- May start as latency issue and evolve into availability crisis
- Requires identifying and isolating initial failure point

**Planned Downtime Overruns:**
- Maintenance window extends beyond agreed duration
- May violate SLA if not properly communicated or approved
- Requires documented change control procedures
- Merchant notifications must be sent before breach occurs

### Throughput Constraint Patterns

**Hard Capacity Ceiling:**
- System unable to accept requests beyond specific TPS threshold
- New requests rejected with 503 Service Unavailable or rate limit errors
- May indicate queue depth limits, connection pool saturation, or license restrictions
- Predictable pattern during known traffic spikes
- Requires capacity planning and horizontal scaling

**Throughput Degradation Under Load:**
- TPS decreases as request volume increases (inverse relationship)
- Indicates lock contention, CPU saturation, or inefficient request handling
- System spends more time on coordination overhead than productive work
- May stabilize at lower throughput or continue degrading to zero
- Requires profiling under load to identify bottleneck

**Uneven Geographic Distribution:**
- Some regions experience throttling while others operate normally
- Indicates regional capacity imbalance or routing misconfiguration
- May violate regional SLA commitments even if global metrics acceptable
- Requires geo-distributed monitoring and capacity allocation

### Error Budget Depletion Patterns

**Slow Burn:**
- Error budget consumed steadily at 2-5% daily rate
- Indicates persistent low-level issues not severe enough for immediate alerts
- Requires proactive intervention before month-end SLA breach
- Common causes: increased retry rates, specific merchant issues, slow dependency degradation

**Rapid Depletion:**
- Error budget consumed 20-50% within single day or incident
- Typically follows major incident or deployment issue
- Leaves little margin for additional failures during measurement period
- May trigger feature freeze or deployment moratorium

**Clustered Depletion:**
- Error budget consumed during specific time windows (weekends, peak hours)
- Indicates capacity or configuration issues during predictable patterns
- Requires time-based mitigation strategies

**Merchant-Specific Depletion:**
- Aggregate SLA metrics acceptable but individual merchant SLAs breached
- High-volume merchants disproportionately affected
- May require merchant-specific capacity allocation or priority queuing

---

## Observable Signals (Metrics/Logs)

### Latency Metrics

**Authorization Latency:**
- `payment.authorization.latency.p50` < 100ms (target), < 150ms (SLA threshold)
- `payment.authorization.latency.p95` < 300ms (target), < 500ms (SLA threshold)
- `payment.authorization.latency.p99` < 800ms (target), < 1500ms (SLA threshold)
- `payment.authorization.latency.p99.9` < 2000ms (target), < 3000ms (SLA threshold)
- Measurement window: 5-minute rolling average

**Capture Latency:**
- `payment.capture.latency.p95` < 500ms (target), < 1000ms (SLA threshold)
- `payment.capture.latency.p99` < 1500ms (target), < 2500ms (SLA threshold)
- Asynchronous captures may have relaxed SLA (5-10 seconds)

**Refund Latency:**
- `payment.refund.latency.p95` < 1000ms (target), < 2000ms (SLA threshold)
- Partial refunds may have different thresholds than full refunds
- Measurement excludes issuer processing time (external dependency)

**Webhook Delivery Latency:**
- `webhook.delivery.latency.p95` < 5000ms (target), < 10000ms (SLA threshold)
- Critical for merchant reconciliation workflows
- May have separate SLA from transaction processing

**Database Query Latency:**
- `db.query.latency.p95` < 50ms (internal target)
- Leading indicator for transaction latency issues
- Monitor per query type: SELECT, INSERT, UPDATE
- Track slow query log for statements exceeding 100ms

**External Dependency Latency:**
- `issuer.latency.p95` < 1500ms (tracking metric, no SLA control)
- `fraud_check.latency.p95` < 200ms (internal SLA)
- `tokenization.latency.p95` < 100ms (internal SLA)
- Track separately to distinguish internal vs external latency contribution

**Latency Breakdown Metrics:**
- `latency.network` - Time spent in network transit
- `latency.queue` - Time spent waiting in processing queue
- `latency.processing` - Actual computation time
- `latency.external` - Time waiting for external dependencies
- Sum should equal total end-to-end latency for diagnosis

### Availability Metrics

**Overall Availability:**
- `payment.availability.rate` > 99.95% (SLA threshold for critical systems)
- `payment.availability.rate` > 99.5% (SLA threshold for non-critical systems)
- Calculated as: (successful_transactions / total_transactions) * 100
- Excludes expected declines (insufficient funds, fraud detection, card validation failures)

**Component-Level Availability:**
- `api_gateway.availability` > 99.99%
- `authorization_service.availability` > 99.95%
- `capture_service.availability` > 99.9%
- `database.availability` > 99.99%
- `cache.availability` > 99.9% (degraded mode acceptable)

**Geographic Availability:**
- Track per region: NA-EAST, NA-WEST, EU-CENTRAL, EU-WEST, APAC-NORTHEAST, APAC-SOUTHEAST
- Regional SLA may differ from global SLA
- `availability.region.{region_code}` > 99.9%

**Payment Method Availability:**
- `availability.card.visa` > 99.95%
- `availability.card.mastercard` > 99.95%
- `availability.card.amex` > 99.9%
- `availability.bank_transfer` > 99.5%
- `availability.wallet` > 99.9%

**Merchant-Tier Availability:**
- Tier 1 (enterprise): > 99.99% availability guarantee
- Tier 2 (growth): > 99.95% availability guarantee
- Tier 3 (standard): > 99.5% availability guarantee
- Track `availability.merchant.{merchant_id}` for contractual reporting

**Uptime vs Availability Distinction:**
- Uptime: Binary metric (service responding to health checks)
- Availability: Success rate metric (service processing requests correctly)
- Service can be "up" but unavailable if returning errors

### Error Rate Metrics

**HTTP Error Rates:**
- `http.5xx.rate` < 0.1% (internal errors, SLA-impacting)
- `http.4xx.rate` < 2% (client errors, typically non-SLA-impacting)
- `http.429.rate` < 0.5% (rate limiting, indicates capacity issues)
- `http.503.rate` < 0.05% (service unavailable, critical SLA breach)
- `http.504.rate` < 0.05% (gateway timeout, indicates latency cascade)

**Transaction Error Rates:**
- `transaction.error.internal` < 0.1% (system errors, SLA-impacting)
- `transaction.error.external` < 5% (issuer declines, non-SLA-impacting)
- `transaction.error.timeout` < 0.5% (indicates latency issues)
- `transaction.error.validation` < 1% (merchant integration issues)

**Retry and Circuit Breaker Metrics:**
- `retry.rate` - Percentage of transactions requiring retry
- `retry.exhaustion.rate` < 0.1% - Transactions failing after max retries
- `circuit_breaker.open.count` - Number of open circuit breakers
- `circuit_breaker.half_open.rate` - Recovery attempts in progress

**Error Budget Metrics:**
- `error_budget.remaining` - Percentage of error budget remaining for current period
- `error_budget.burn_rate` - Rate of error budget consumption (per hour/day)
- `error_budget.days_remaining` - Projected days until budget exhaustion at current burn rate
- Alert thresholds:
  - Critical: < 10% budget remaining with > 7 days left in period
  - Warning: < 25% budget remaining with > 14 days left in period
  - Fast burn: > 5% budget consumed in single hour

### Throughput Metrics

**Request Volume:**
- `requests.per_second` - Current TPS
- `requests.per_second.peak` - Peak TPS in current measurement window
- `requests.per_second.capacity` - Maximum supported TPS based on capacity planning
- Alert when `requests.per_second` > 80% of `requests.per_second.capacity`

**Queue Depth:**
- `queue.depth.authorization` - Pending authorization requests
- `queue.depth.capture` - Pending capture requests
- `queue.depth.webhook` - Pending webhook deliveries
- Alert thresholds:
  - Warning: Queue depth > 1000 for > 5 minutes
  - Critical: Queue depth > 10000 or growing > 500/minute

**Connection Pool Metrics:**
- `connection_pool.active` - Connections currently in use
- `connection_pool.idle` - Connections available for use
- `connection_pool.wait_time.p95` < 10ms
- Alert when `connection_pool.active / connection_pool.size` > 90%

**Thread Pool Metrics:**
- `thread_pool.active` - Threads processing requests
- `thread_pool.queued` - Requests waiting for thread
- Alert when `thread_pool.queued` > 100 for > 1 minute

### Resource Utilization Metrics

**CPU Utilization:**
- `cpu.utilization` < 70% (sustained), < 85% (peak)
- Track per service and per host
- Spike above 95% indicates imminent capacity constraint
- Monitor `cpu.steal` metric in cloud environments (indicates noisy neighbor)

**Memory Utilization:**
- `memory.utilization` < 80% (sustained), < 90% (peak)
- `memory.heap.utilization` < 75% for JVM-based services
- Track garbage collection frequency and duration
- Alert on memory leak indicators: steady growth without plateau

**Disk I/O:**
- `disk.io.wait` < 10% (sustained), < 20% (peak)
- `disk.queue_depth` < 10
- Particularly critical for database hosts
- SSD vs HDD thresholds differ significantly

**Network Utilization:**
- `network.throughput` < 70% of interface capacity
- `network.packet_loss` < 0.01%
- `network.retransmit.rate` < 0.1%
- Monitor both inbound and outbound separately

### Log Patterns Indicating SLA Risk

**Error Log Patterns:**
- `ERROR: Database connection pool exhausted` - Immediate capacity issue
- `ERROR: Timeout waiting for response from {service}` - Latency cascade beginning
- `WARN: Circuit breaker opened for {dependency}` - Availability degradation
- `ERROR: Rate limit exceeded for {resource}` - Throughput constraint
- `FATAL: Out of memory` - Immediate availability failure

**Performance Log Patterns:**
- `SLOW_QUERY: Query took {time}ms` when time > 1000ms - Database performance degradation
- `WARN: Request queue depth {depth}` when depth > 500 - Throughput saturation
- `WARN: GC pause {duration}ms` when duration > 100ms - Memory pressure
- `ERROR: Thread pool exhausted` - Processing capacity limit

**Dependency Health Patterns:**
- `WARN: {dependency} latency increased to {latency}ms` - External factor
- `ERROR: {dependency} returning elevated error rate` - Availability impact
- `WARN: Issuer {issuer_name} degraded performance` - Segment-specific issue

**Audit Log Requirements:**
- All SLA-impacting events must generate audit log entries
- Include: timestamp, affected service, metric values, automated actions taken
- Retention: minimum 13 months for annual compliance reviews
- Format: structured JSON for automated analysis

---

## Probable Root Causes

### Infrastructure-Level Causes

**Insufficient Capacity Provisioning:**
- Auto-scaling policies not aggressive enough for traffic growth rate
- Manual scaling procedures not executed during known peak events
- Resource limits (CPU, memory, network) hit during normal operation
- Insufficient connection pool sizes for database or external dependencies
- Diagnosis: Compare current utilization to historical baselines and capacity planning documents

**Resource Contention:**
- Multiple services competing for shared resources (CPU, memory, network, disk I/O)
- Batch processing jobs scheduled during peak transaction hours
- Noisy neighbor problem in multi-tenant cloud environments
- Database locks preventing concurrent transaction processing
- Diagnosis: Correlate performance degradation with other workload schedules

**Hardware Degradation:**
- Disk failure in RAID array causing degraded read/write performance
- Network interface card (NIC) errors increasing packet loss and retransmits
- Memory errors requiring frequent ECC corrections
- CPU thermal throttling due to cooling system issues
- Diagnosis: Review system hardware health metrics and error logs

**Network Issues:**
- Routing table misconfiguration after network change
- BGP route flapping causing intermittent connectivity
- Cross-datacenter link saturation during peak hours
- DNS resolution failures or increased latency
- Firewall rule changes blocking legitimate traffic
- Diagnosis: Network trace analysis, compare latency across different paths

**Cloud Provider Issues:**
- Regional service degradation affecting specific availability zones
- Hypervisor issues causing VM performance degradation
- Storage service throttling due to burst credit exhaustion
- Load balancer misconfiguration or health check failures
- Diagnosis: Check cloud provider status page, correlate with multi-region metrics

### Application-Level Causes

**Code Regression:**
- Recent deployment introduced inefficient algorithm or query
- Memory leak causing gradual performance degradation
- Infinite loop or recursive call consuming CPU
- Synchronous operation blocking request processing
- Diagnosis: Compare performance before and after recent deployments, code review

**Database Performance Issues:**
- Missing or outdated indexes causing full table scans
- Query plan regression due to stale statistics
- Lock contention on hot tables or rows
- Connection leak exhausting database connection pool
- Replication lag between primary and read replicas
- Diagnosis: Analyze slow query logs, explain plan for expensive queries

**External Dependency Degradation:**
- Issuer bank experiencing downtime or throttling
- Fraud detection service latency increased
- Third-party API rate limiting applied
- Network path to external service degraded
- External service deployed breaking change
- Diagnosis: Monitor external dependency latency and error rates separately

**Configuration Errors:**
- Incorrect timeout values causing premature failures
- Circuit breaker thresholds too sensitive or too lenient
- Rate limiting configured incorrectly
- Caching invalidation policy too aggressive
- Thread pool sizes misconfigured
- Diagnosis: Review recent configuration changes, validate against documented standards

**Memory Management Issues:**
- Garbage collection pauses exceeding acceptable duration
- Memory fragmentation reducing available heap space
- Large object allocation causing frequent full GC cycles
- Off-heap memory leak in native libraries
- Diagnosis: Analyze GC logs, heap dumps, memory profiling

**Concurrency Issues:**
- Deadlock between competing transactions
- Race condition causing data corruption or retry loops
- Thread starvation due to blocking operations
- Lock convoy effect reducing overall throughput
- Diagnosis: Thread dumps, lock contention analysis, distributed tracing

### Traffic-Pattern Causes

**Unexpected Traffic Surge:**
- Viral social media post driving traffic to merchant
- Marketing campaign not communicated to operations team
- Bot attack or credential stuffing attempt
- DDoS attack on payment endpoints
- Diagnosis: Analyze traffic patterns by source, user agent, geographic origin

**Retry Storm:**
- Client-side retries overwhelming system capacity
- Automated retry logic in merchant integration
- Mobile app offline-queue replay
- Webhook delivery retries cascading
- Diagnosis: Track retry attempt counts, identify sources of excessive retries

**Seasonal or Event-Driven Load:**
- Holiday shopping season exceeding capacity plan
- Flash sale or limited-time offer
- Payday-correlated transaction surge
- Time-zone-driven peak hour shifting
- Diagnosis: Compare current patterns to historical seasonal data

**Geographic Traffic Shift:**
- Traffic shifting to different region due to outage or routing change
- New merchant onboarding concentrating traffic in single region
- Time-zone progression of daily peak hours
- Diagnosis: Geographic distribution analysis, compare to baseline

### Data-Related Causes

**Data Growth:**
- Database tables exceeding efficient query size
- Index size causing memory pressure
- Log volume filling disk partitions
- Archive policies not executing correctly
- Diagnosis: Analyze table sizes, index sizes, disk usage trends

**Data Skew:**
- Hot partition in distributed database receiving disproportionate load
- Specific merchant or payment method dominating traffic
- Uneven shard key distribution
- Diagnosis: Analyze data distribution across partitions/shards

**Data Corruption:**
- Inconsistent state between primary and replica databases
- Corrupt index requiring rebuild
- Transaction log corruption preventing replication
- Diagnosis: Data validation queries, replication lag monitoring

### Operational Causes

**Change Management Failures:**
- Deployment during peak hours violating change control policy
- Insufficient testing before production rollout
- Missing rollback plan or rollback procedure failure
- Configuration change applied without validation
- Diagnosis: Review change logs, deployment history

**Monitoring Blind Spots:**
- Critical metric not being monitored
- Alert thresholds set too high to detect gradual degradation
- Monitoring system itself experiencing outage
- Delayed alert delivery due to notification system issues
- Diagnosis: Gap analysis of monitoring coverage

**Insufficient Testing:**
- Load testing did not simulate realistic traffic patterns
- Chaos engineering not performed regularly
- Dependency failure scenarios not tested
- Diagnosis: Review test coverage, compare test vs production load

**Documentation Gaps:**
- Runbook outdated or incomplete
- Tribal knowledge not documented
- Architecture diagrams not reflecting current state
- Diagnosis: Knowledge transfer failures during incidents

---

## Safe Mitigation Actions

### Immediate Response Actions (< 5 Minutes)

**Traffic Shaping:**
- Enable rate limiting at API gateway level to protect backend services
- Configuration: `rate_limit.max_requests_per_minute` = 80% of current capacity
- Apply per-merchant rate limits to prevent single merchant from consuming all capacity
- Preserve fairness: implement token bucket algorithm with burst allowance
- Monitor: `rate_limit.dropped_requests` to quantify impact on merchants
- Revert criteria: When backend service latency returns to < SLA threshold for 5 consecutive minutes
- Risk: May cause merchant-visible errors but prevents total system collapse

**Circuit Breaker Activation:**
- Open circuit to failing dependency to prevent cascade
- Configuration: `circuit_breaker.failure_threshold` = 50% error rate over 1-minute window
- Fallback behavior: Return cached response or safe default
- Half-open retry: Attempt recovery every 30 seconds with single test request
- Monitor: `circuit_breaker.fallback_invocations` to track degraded mode usage
- Revert criteria: When dependency error rate < 5% for 3 consecutive minutes
- Risk: Degraded functionality but maintains system stability

**Load Shedding:**
- Reject lowest-priority requests to preserve capacity for critical transactions
- Priority order: Enterprise merchants > Growth merchants > Standard merchants
- Implement: Return HTTP 503 with Retry-After header for low-priority requests
- Configuration: `load_shed.enabled = true`, `load_shed.priority_threshold = 2`
- Monitor: `requests.shed.count` by priority tier
- Revert criteria: When system utilization < 70% for 5 minutes
- Risk: Impacts specific merchant cohort but prevents widespread outage

**Cache Warming:**
- Pre-populate cache with frequently accessed data to reduce database load
- Targets: merchant configuration, routing rules, fraud rules
- Implementation: Background job reading from database replica
- Monitor: `cache.hit_rate` should increase from baseline ~70% to > 90%
- Revert criteria: Not applicable, cache warming is additive
- Risk: Minimal, may temporarily increase memory usage

**Request Queue Management:**
- Increase queue capacity temporarily to buffer traffic spikes
- Configuration: `queue.max_depth` increased from 1000 to 5000
- Add queue timeout: Drop requests older than 30 seconds
- Monitor: `queue.depth`, `queue.timeout_drops`
- Revert criteria: When queue depth remains < 500 for 10 minutes
- Risk: Increased memory usage, delayed request processing

**Retry Backoff Adjustment:**
- Increase delay between retries to reduce load on degraded system
- Configuration: Change from fixed 1s delay to exponential backoff 1s, 2s, 4s, 8s
- Maximum retry attempts: Reduce from 5 to 3 during degradation
- Monitor: `retry.backoff_duration.avg`, `retry.success_rate`
- Revert criteria: When dependency latency < SLA threshold for 10 minutes
- Risk: Slower recovery from transient failures but prevents retry storms

**Read Replica Promotion:**
- Redirect read queries to secondary database replicas to offload primary
- Configuration: Update connection pool to include replica endpoints
- Monitor replication lag: `db.replication_lag_seconds` must be < 5 seconds
- Consistency consideration: May serve stale data if replication lagged
- Revert criteria: When primary database CPU < 60%
- Risk: Potential data staleness, acceptable for non-critical reads

### Short-Term Mitigations (5-30 Minutes)

**Horizontal Scaling:**
- Add additional service instances to increase capacity
- Cloud: Trigger auto-scaling group to add 20-50% capacity
- Monitor: Instance startup time (~3-5 minutes), health check pass rate
- Verify: New instances receiving traffic and processing successfully
- Revert criteria: Once traffic returns to normal, allow auto-scaling to reduce capacity
- Risk: Increased cost, potential configuration drift if instances misconfigured

**Vertical Scaling:**
- Increase resource allocation (CPU, memory) for existing instances
- Cloud: Modify instance type to larger size (requires brief downtime per instance)
- Rolling upgrade: Scale instances one at a time to maintain availability
- Monitor: Resource utilization should decrease proportionally
- Revert criteria: When sustained load confirms smaller instance adequate
- Risk: Brief per-instance downtime during resize, increased cost

**Database Connection Pool Tuning:**
- Increase connection pool size to reduce wait time
- Configuration: `db.pool.max_connections` increased from 100 to 200
- Validate database can handle increased connections without overload
- Monitor: `db.connection.wait_time`, `db.connection.active`
- Revert criteria: When connection wait time consistently < 10ms
- Risk: Increased database load, may cause database-side issues if too aggressive

**Caching Strategy Adjustment:**
- Increase cache TTL to reduce database queries
- Configuration: Extend merchant config cache from 5 minutes to 15 minutes
- Trade-off: Slower propagation of configuration changes
- Monitor: `cache.hit_rate`, `db.query.rate`
- Revert criteria: When database load returns to acceptable level
- Risk: Stale data served for longer period, acceptable for stable configurations

**Query Optimization:**
- Add missing database indexes identified in slow query log
- Create indexes online (non-blocking): `CREATE INDEX CONCURRENTLY`
- Monitor: Query execution time should decrease for affected queries
- Validate: Ensure index actually used by query planner (EXPLAIN plan)
- Revert criteria: Index remains useful for future queries, typically not reverted
- Risk: Index creation consumes resources, minimal if done correctly

**Batch Processing Postponement:**
- Delay non-critical batch jobs to free resources for transaction processing
- Examples: Reporting jobs, data exports, analytics processing
- Reschedule: Move from peak hours to off-peak (2-6 AM local time)
- Monitor: Ensure batch jobs complete before next scheduled run
- Revert criteria: When system capacity sufficient for both transactions and batch jobs
- Risk: Delayed reporting, may affect SLAs for non-transactional workflows

**Geographic Traffic Redistribution:**
- Redirect traffic from overloaded region to regions with available capacity
- Implementation: Update DNS records or load balancer routing rules
- Monitor: Latency may increase for redirected traffic due to distance
- Validate: Receiving region has sufficient capacity for additional load
- Revert criteria: When original region capacity restored
- Risk: Increased cross-region latency, potential data residency concerns

**Feature Flag Disabling:**
- Temporarily disable non-essential features to reduce system load
- Examples: Advanced fraud checks, premium analytics, experimental payment methods
- Implementation: Set feature flag `feature.{name}.enabled = false`
- Monitor: Reduction in specific request types or processing paths
- Revert criteria: When system capacity sufficient to support full feature set
- Risk: Reduced functionality for merchants, potential revenue impact

### Medium-Term Actions (30 Minutes - 4 Hours)

**Deployment Rollback:**
- Revert recent deployment suspected of causing degradation
- Procedure: Restore previous container image or artifact version
- Implementation: Rolling rollback maintaining availability during process
- Validate: Performance metrics return to pre-deployment baseline
- Post-rollback: Root cause analysis required before re-deployment
- Risk: Loss of new features/fixes from rolled-back deployment

**Database Failover:**
- Promote standby database to primary if primary database degraded
- Automated failover: Typically 30-60 seconds with monitoring system
- Manual failover: Requires validation of standby health and replication status
- Post-failover actions: Update application connection strings, verify data consistency
- Monitor: Replication lag must be < 10 seconds before failover
- Risk: Brief write unavailability during cutover, potential data loss if replication lagged

**Configuration Optimization:**
- Adjust system configuration based on observed behavior
- Examples: Thread pool sizes, garbage collection parameters, network buffers
- Procedure: Update configuration, restart service with rolling deployment
- Validation: A/B testing or canary deployment to verify improvement
- Monitor: Target metric improvement within 10 minutes of configuration change
- Risk: Incorrect configuration may worsen situation, requires expertise

**Cache Cluster Expansion:**
- Add nodes to distributed cache (Redis, Memcached) to increase capacity
- Procedure: Add nodes to cluster, rebalance data distribution
- Monitor: Cache eviction rate should decrease, hit rate should stabilize
- Revert criteria: Cache performance adequate with fewer nodes
- Risk: Data redistribution may cause temporary cache miss spike

**Traffic Pattern Analysis and Filtering:**
- Identify and block abusive or anomalous traffic patterns
- Examples: Credential stuffing, scraping bots, DDoS traffic
- Implementation: Update WAF rules or rate limiting by IP, user agent, or behavior
- Monitor: Reduction in request volume without impacting legitimate traffic
- Validation: Sample blocked requests to confirm they're truly malicious
- Risk: False positives blocking legitimate users

**Dependent Service SLA Renegotiation:**
- Contact external dependency provider to request temporary SLA relaxation or support
- Examples: Issuer banks, fraud detection providers, tokenization services
- Communication: Escalate through account management or technical support channels
- Monitor: Improvement in external dependency performance
- Documentation: Record agreement details for future reference
- Risk: May not receive immediate support depending on provider responsiveness

**Data Archival Acceleration:**
- Archive or purge old data to reduce database size and improve query performance
- Identify: Tables growing beyond optimal size for query performance
- Procedure: Export old data to cold storage, delete from primary database
- Validation: Ensure archived data remains accessible for compliance
- Monitor: Database size reduction, query performance improvement
- Risk: Potential data loss if archival process flawed

**Regional Capacity Redistribution:**
- Permanently shift merchant traffic to region with better capacity
- Procedure: Update merchant configuration to prefer specific region
- Gradual migration: Move 10% of traffic per hour to validate stability
- Monitor: Both source and destination region metrics during migration
- Revert criteria: If destination region shows degradation, halt migration
- Risk: Increased cross-region latency for affected merchants

### Long-Term Actions (4+ Hours, Requires Planning)

**Capacity Planning and Procurement:**
- Analyze historical trends and forecast future capacity needs
- Procurement: Order additional hardware or reserve cloud capacity
- Lead time: Hardware procurement 4-12 weeks, cloud reservation immediate but requires cost approval
- Implementation: Schedule installation/configuration during maintenance window
- Validation: Load testing to confirm capacity meets projections
- Risk: Over-provisioning wastes budget, under-provisioning leaves gaps

**Architecture Redesign:**
- Implement fundamental architectural changes to address scalability limits
- Examples: Microservices decomposition, database sharding, async processing
- Planning: 2-4 weeks for design, 4-12 weeks for implementation
- Testing: Comprehensive load testing, shadow traffic validation
- Rollout: Phased deployment with extensive monitoring
- Risk: Complex change with potential for new failure modes

**Dependency Migration:**
- Replace unreliable external dependency with alternative provider
- Evaluation: Assess alternative providers for performance, reliability, cost
- Integration: Develop and test integration with new provider
- Migration: Gradual cutover with fallback to original provider
- Validation: Monitor error rates and latency with new provider
- Risk: Integration bugs, contract negotiations, data migration complexity

**SLA Renegotiation with Merchants:**
- Propose revised SLA terms reflecting realistic system capabilities
- Analysis: Document historical performance, identify realistic commitments
- Communication: Proactive outreach to affected merchants with proposed changes
- Negotiation: May require discounts or service credits for reduced SLA
- Legal review: Contract amendments require approval
- Risk: Merchant dissatisfaction, potential churn

---

## Actions Requiring Human Approval

### Financial Impact Decisions

**Merchant Compensation:**
- Issuing service credits or refunds for SLA breaches exceeds automated authority
- Approval required: Finance team for amounts > $10,000, executive for > $100,000
- Documentation: Detailed incident report, financial impact analysis, root cause
- Timing: Compensation decisions typically made 24-48 hours post-incident after full analysis
- Process: Incident commander submits request, finance approves based on SLA contract terms
- Precedent: Consider past compensation decisions for consistency

**Emergency Capacity Procurement:**
- Purchasing additional cloud resources beyond approved budget
- Approval required: Engineering manager for 20% budget increase, VP for >50%
- Justification: Demonstrate capacity crisis, forecast of continued need
- Alternatives: Must explore all cost-free mitigations first
- Timing: Approval typically granted within 1-2 hours for genuine emergencies
- Accountability: Post-incident review of whether emergency spending was justified

**Merchant Suspension:**
- Temporarily blocking high-volume merchant causing capacity issues
- Approval required: Vice President of Payments, Legal review
- Justification: Demonstrate merchant's traffic violating fair use policy or causing widespread degradation
- Communication: Legal team must notify merchant with contractual justification
- Alternatives: Rate limiting, traffic shaping should be attempted first
- Risk: Contract breach lawsuit if not properly justified

### Contractual and Legal Decisions

**SLA Exception Approval:**
- Declaring force majeure or SLA exception for unusual circumstances
- Approval required: Legal team, Chief Operations Officer
- Circumstances: Natural disasters, vendor outages, regulatory changes, security incidents
- Documentation: Comprehensive incident timeline, third-party status pages, impact analysis
- Communication: Formal notification to all affected merchants within contractual timeframe (typically 24 hours)
- Risk: Weakens merchant trust if overused, legal exposure if improperly claimed

**Third-Party Disclosure:**
- Sharing incident details with external parties (vendors, regulators, media)
- Approval required: Legal team, Communications/PR team
- Content review: All disclosures must be vetted for accuracy, legal exposure, confidentiality
- Timing: Regulatory disclosures may have mandatory timelines (e.g., 72 hours for GDPR breach)
- Coordination: Align messaging across all communication channels
- Risk: Inconsistent messaging damages credibility, premature disclosure creates legal liability

**Contract Breach Declaration:**
- Formally notifying vendor or partner of SLA breach on their part
- Approval required: Legal team, Vendor Management
- Documentation: Evidence of breach, contractual SLA terms, impact quantification
- Negotiation: Opportunity for vendor to cure before formal breach declaration
- Remedies: Service credits, penalty clauses, or contract termination per agreement
- Risk: Vendor relationship damage, potential counter-claims

### Architecture and System Changes

**Emergency Architecture Changes:**
- Implementing significant architectural modifications during active incident
- Approval required: Principal Engineer, VP of Engineering
- Justification: Demonstrate other mitigations exhausted, clear improvement path
- Risk assessment: Potential for introducing new failures during incident
- Testing: Minimum viable validation in staging environment
- Rollback plan: Must have clear rollback procedure
- Decision criteria: High confidence of improvement (>80%), acceptable blast radius if fails

**Database Schema Changes in Production:**
- Altering table structures, indexes, or constraints during incident
- Approval required: Database Administrator, Senior Engineer
- Risk assessment: Lock duration, disk space requirements, replication impact
- Validation: Test exact DDL statements in staging environment first
- Timing: Execute during lowest traffic period if possible
- Monitoring: Track query performance before/after change
- Rollback: Document rollback procedure (typically recreating old index)

**Multi-Region Failover:**
- Redirecting all traffic from one geographic region to another
- Approval required: Site Reliability Engineering Manager, VP of Operations
- Validation: Receiving region confirmed to have 2x current capacity
- Data consistency: Ensure no split-brain scenario with database replication
- Communication: Notify merchants of potential latency impact
- Regulatory: Verify data residency requirements allow cross-region processing
- Rollback: Procedure to restore original routing when source region recovered

### Operational Policy Changes

**Change Freeze Override:**
- Deploying code changes during declared change freeze period
- Approval required: Change Advisory Board, CTO
- Justification: Critical security patch or incident resolution requiring code change
- Risk assessment: Potential for deployment to worsen ongoing incident
- Testing: Demonstrate fix resolves issue in staging environment
- Communication: Notify all stakeholders of freeze override and justification
- Accountability: Post-incident review of decision appropriateness

**SLA Metric Definition Changes:**
- Modifying how SLA metrics are calculated or measured
- Approval required: Product Management, Legal, Finance
- Impact analysis: Effect on historical SLA compliance, merchant notifications
- Communication: 30-90 day notice to merchants required per contracts
- Documentation: Update SLA documentation, monitoring dashboards, alerting rules
- Audit: Ensure new calculations align with contractual language
- Risk: Merchant perception of "moving goalposts" to avoid SLA penalties

**Incident Severity Escalation:**
- Upgrading incident from Sev-2 to Sev-1 (critical, all-hands response)
- Approval required: On-call Incident Commander, Engineering Manager
- Criteria: SLA breach imminent or occurring, multiple merchants impacted, financial impact >$100k
- Actions triggered: Page executive team, initiate war room, halt all changes
- Communication: Status updates every 15 minutes to stakeholder Slack channel
- De-escalation: Requires same approval level to downgrade severity

### Resource Allocation Decisions

**On-Call Resource Mobilization:**
- Calling in off-duty engineers during non-business hours
- Approval required: Incident Commander, Engineering Manager (for >5 people)
- Justification: Incident complexity requires specialized expertise not available on current shift
- Compensation: Overtime pay or time-off-in-lieu per company policy
- Timing: Minimize delay in requesting help, early mobilization better than late
- Courtesy: Attempt to distribute load fairly, avoid repeatedly calling same individuals

**Cross-Team Resource Borrowing:**
- Requesting engineers from other teams to assist with incident
- Approval required: Both team's engineering managers
- Justification: Incident impact warrants prioritization over other team's roadmap work
- Duration: Typically limited to duration of incident, not extended projects
- Coordination: Clear handoff procedures when borrowed resources rotate off
- Accountability: Document time spent for future capacity planning

**Vendor Emergency Support Engagement:**
- Requesting premium support from external vendors (often at additional cost)
- Approval required: Engineering Manager, Finance (if cost >$10k)
- Justification: Vendor issue blocking incident resolution, normal support channels inadequate
- Documentation: Open support ticket, escalation case number, vendor commitments
- Monitoring: Track vendor response time and effectiveness
- Follow-up: Post-incident debrief with vendor on support experience

### Communication and PR Decisions

**Public Status Page Update:**
- Publishing incident details to public-facing status page
- Approval required: Communications team, Incident Commander
- Content: Acknowledge issue, estimated impact, expected resolution timeline
- Transparency: Balance between honest communication and avoiding panic
- Timing: Update within 15 minutes of Sev-1 declaration, every 30 minutes thereafter
- Risk: Negative press coverage, competitive intelligence, merchant concern

**Merchant-Direct Communication:**
- Proactive email to affected merchants during or after incident
- Approval required: Customer Success leadership, Legal (for SLA admission)
- Segmentation: Target only actually affected merchants to avoid alarm
- Content: Factual incident summary, impact acknowledgment, remediation steps
- Timing: Within 24 hours of incident resolution for Sev-1, 48 hours for Sev-2
- Follow-up: Offer to discuss incident on dedicated support channel

**Regulatory Reporting:**
- Notifying financial regulators of payment system disruption
- Approval required: Legal team, Chief Compliance Officer
- Trigger criteria: Outage >4 hours, >$1M transaction volume impacted, data breach
- Timing: Per regulatory requirements (typically 24-72 hours)
- Content: Formal incident report, root cause, remediation, prevention measures
- Jurisdictions: May require separate reports to multiple regulators (RBI, PCI-DSS, FCA, etc.)

---

## Regulatory and Compliance Notes

### Payment Card Industry Data Security Standard (PCI-DSS)

**Availability Requirements:**
- PCI-DSS does not mandate specific SLA percentages but requires "reasonable availability" for payment processing
- Requirement 12.10: Incident response plan must include procedures for business continuity and disaster recovery
- Quarterly uptime reports may be requested during PCI audits
- Extended outages (>24 hours) must be documented and reported to acquiring bank

**Incident Documentation:**
- All security incidents, including availability failures, must be logged per Requirement 10
- Log retention: Minimum 1 year, with 3 months immediately available for analysis
- Logs must include: timestamp, user identification, event type, success/failure indicator, origination of event, identity/name of affected resource
- Availability incidents triggering automatic actions must preserve audit trail of decisions made

**Change Management:**
- Requirement 6.4: All system changes must follow documented change control procedures
- Emergency changes during incident response must be retroactively documented
- Production changes require testing in non-production environment first (may be waived for emergency)
- Change documentation must include security impact assessment

**Third-Party Service Providers:**
- Per Requirement 12.8, must maintain list of all service providers with access to cardholder data
- Service provider outages impacting availability must be tracked separately
- Annual attestation of service provider PCI compliance required
- SLA agreements with providers must address security and availability

### Reserve Bank of India (RBI) Guidelines

**Payment System Operators (PSO) Requirements:**
- RBI expects "high availability" for payment systems, typically interpreted as >99.5% monthly uptime
- Systemic failures affecting >10,000 transactions or >₹10 crore must be reported to RBI within 24 hours
- Technical glitches causing customer fund transfer failures must be reported

**Business Continuity Planning:**
- RBI mandates documented business continuity plan (BCP) with recovery time objective (RTO) <4 hours
- BCP must be tested annually and results documented
- Disaster recovery site must be geographically separated (>200 km for critical systems)
- Board-approved incident management framework required

**Data Localization:**
- Payment system data for Indian transactions must be stored in India (copy can be stored abroad)
- SLA mitigations involving cross-border failover must ensure Indian data remains in India
- Latency increases from cross-border operations may be acceptable if data residency maintained

**Customer Grievance Redressal:**
- Failed transactions due to system issues must be resolved within timeline per RBI circular
- Credit reversal for failed debits: Within T+1 day
- Compensation for delays beyond SLA: Auto-credit of ₹100 per day delay (for certain transaction types)
- Annual reporting to RBI on complaints, root causes, and remediation

### General Data Protection Regulation (GDPR)

**Availability as Part of Security:**
- Article 32: Appropriate technical measures must ensure "ongoing confidentiality, integrity, availability and resilience"
- Availability failures are not data breaches unless they indicate loss of data integrity or confidentiality
- However, extended unavailability preventing data subject access requests may violate Article 15 rights

**Breach Notification:**
- Availability failures resulting in unauthorized access or data loss must be reported to supervisory authority within 72 hours (Article 33)
- Affected individuals must be notified "without undue delay" if high risk to rights and freedoms (Article 34)
- Not all SLA breaches constitute "personal data breaches" under GDPR

**Data Processing Agreements:**
- Processors must notify controllers of availability incidents that may affect controller's compliance (Article 28)
- SLA terms between processor and controller should specify incident notification procedures
- Processor must assist controller with breach notification obligations

### Payment Services Directive 2 (PSD2) - European Union

**Strong Customer Authentication (SCA) Availability:**
- SCA systems must maintain high availability as authentication failures block transactions
- Exemptions from SCA (transaction risk analysis) require reliable, available fraud detection systems
- Technical failures in SCA must not unduly prevent legitimate transactions

**Operational and Security Risks:**
- Article 95: Payment service providers must establish framework to mitigate operational risks, including availability risks
- Annual self-assessment of operational resilience required
- Major operational incidents must be reported to competent authority (severity criteria vary by country)

**Third-Party Provider (TPP) Access:**
- Account servicing payment service providers (ASPSPs) must ensure 99.5% availability of API interfaces for TPPs
- Quarterly reports on API availability must be published
- Downtime for scheduled maintenance must be communicated in advance

### Electronic Fund Transfer Act (EFTA) / Regulation E - United States

**Error Resolution:**
- Financial institutions must investigate disputed transactions within 45 days (90 days for new accounts)
- Provisional credit must be issued within 10 business days if investigation not complete
- System failures causing erroneous transfers must be remediated and customers made whole

**Disclosure Requirements:**
- Terms of service must disclose circumstances under which service may be unavailable
- Planned maintenance windows should be disclosed in advance when feasible
- Recurring system issues must be addressed to maintain "reasonable availability"

### Financial Crimes Enforcement Network (FinCEN) - United States

**Suspicious Activity Reporting:**
- System failures enabling fraudulent transactions must be reported via SAR if >$2,000 loss
- Availability failures that prevent AML monitoring may require SAR if suspicious activity not detected
- Technology failures facilitating money laundering require reporting

### Monetary Authority of Singapore (MAS)

**Technology Risk Management:**
- Notice 655: Financial institutions must establish availability targets aligned with business criticality
- Critical systems: RTO <4 hours, RPO <1 hour
- System-wide outages >2 hours must be reported to MAS within 1 hour of occurrence
- Root cause analysis and remediation plan due within 14 days

**Outsourcing:**
- Material outsourcing arrangements must include SLA terms covering availability
- Service provider must notify institution of incidents within timeframes specified in agreement
- Institution remains accountable to MAS for outsourced services' availability

### National Automated Clearing House Association (NACHA) - United States

**ACH Network Rules:**
- Originating depository financial institutions (ODFIs) must maintain operations to support timely ACH processing
- Settlement windows are fixed; availability failures causing settlement misses have financial consequences
- ACH returns due to technical failures must follow specified return reason codes

**Risk Management:**
- ODFI must have business continuity plan ensuring ACH processing continuity
- Third-party service providers must be monitored for operational risk, including availability

### Cross-Regulatory Considerations

**Conflicting Requirements:**
- Data residency laws may conflict with disaster recovery requirements for geographic distribution
- Consult legal team when SLA mitigation strategies involve cross-border data transfer
- Document risk-based decisions where full compliance with all regulations impossible

**Audit Trail Requirements:**
- All regulatory regimes require comprehensive logging of actions taken during incidents
- Logs must be immutable and include automated action justifications
- Periodic log reviews required to demonstrate compliance with incident response procedures

**Third-Party Risk Management:**
- Regulators increasingly scrutinize dependency on third parties for critical functions
- SLA agreements with vendors must flow down regulatory requirements
- Annual vendor risk assessments should include availability performance review

**Incident Reporting Timelines:**
- Map each regulatory regime's reporting requirements to incident severity classification
- Create notification checklist to ensure all required parties notified within mandated timeframes
- False alarms (reporting incidents that later prove non-reportable) generally not penalized

### Compliance During SLA Incidents

**Real-Time Compliance Checks:**
- Before executing SLA mitigation, verify action does not violate regulatory constraints
- Data residency: Ensure traffic rerouting does not move data to non-compliant jurisdiction
- Transaction limits: Verify automated actions do not exceed authorized transaction thresholds
- Segregation of duties: Some mitigations may require dual authorization per compliance policy

**Post-Incident Compliance:**
- Document all actions taken, with timestamps and justification
- Compile evidence for potential regulatory inquiry: logs, metrics, communications
- Calculate financial impact for regulatory reporting thresholds
- Update compliance risk register if incident revealed new compliance risks

**Merchant Communication Compliance:**
- Contractual SLA breach notifications must follow agreement terms (timing, method, content)
- If incident involves data security, privacy laws may mandate consumer notification
- Ensure merchant communications reviewed by legal before sending to avoid admission of liability

---

## Appendix: SLA Monitoring Dashboard Queries

**Latency SLA Query (Prometheus):**
```
histogram_quantile(0.95, 
  rate(payment_authorization_duration_seconds_bucket[5m])
) * 1000 < 500
```

**Availability SLA Query (Prometheus):**
```
(
  sum(rate(payment_requests_total{status="success"}[5m])) 
  / 
  sum(rate(payment_requests_total[5m]))
) * 100 > 99.95
```

**Error Budget Consumption (Prometheus):**
```
(1 - (
  sum(rate(payment_requests_total{status="success"}[30d])) 
  / 
  sum(rate(payment_requests_total[30d]))
)) / (1 - 0.9995) * 100
```

**SLA Breach Detection Alert:**
```
ALERT SLABreach
IF payment_latency_p95 > 500
FOR 5m
LABELS { severity = "critical", team = "payments-sre" }
ANNOTATIONS {
  summary = "Payment latency SLA breach",
  description = "P95 latency {{ $value }}ms exceeds 500ms SLA for 5 minutes",
}
```

**Error Budget Burn Rate Alert:**
```
ALERT ErrorBudgetFastBurn
IF (
  (1 - (sum(rate(payment_requests_total{status="success"}[1h])) / sum(rate(payment_requests_total[1h]))))
  / (1 - 0.9995)
) > 0.05
LABELS { severity = "warning", team = "payments-sre" }
ANNOTATIONS {
  summary = "Error budget consuming rapidly",
  description = "5% of monthly error budget consumed in 1 hour",
}
```

---

## Appendix: Common SLA Breach Scenarios and Response Scripts

**Scenario 1: Database Primary Failure**
- **Detection:** `db.availability = 0`, all write operations failing
- **Immediate Action:** Automated failover to standby database (if configured)
- **Manual Action:** If auto-failover failed, execute: `pg_ctl promote -D /var/lib/postgresql/standby`
- **Verification:** Check replication lag on promoted standby: `SELECT pg_last_xlog_replay_location();`
- **Communication:** "Database failover in progress, expect 60-90 second write disruption"
- **SLA Impact:** Typically 1-2 minutes complete write unavailability

**Scenario 2: API Gateway Overload**
- **Detection:** `api_gateway.cpu > 95%`, `request_latency.p95 > 5000ms`
- **Immediate Action:** Enable rate limiting: `curl -X POST http://api-gateway/config -d '{"rate_limit_enabled": true, "max_rps": 5000}'`
- **Verification:** Monitor `rate_limit.dropped_requests`, should start incrementing
- **Scale Action:** Add gateway instances: `kubectl scale deployment api-gateway --replicas=10`
- **Communication:** "Temporary rate limiting active, some requests may receive HTTP 429"
- **SLA Impact:** Reduced throughput but maintained latency within SLA

**Scenario 3: Issuer Bank Downtime**
- **Detection:** `issuer.{bank_id}.error_rate > 80%`, all transactions to specific issuer failing
- **Immediate Action:** Open circuit breaker for affected issuer: `redis-cli SET circuit:issuer:{bank_id} OPEN EX 300`
- **Fallback:** Return soft decline to merchant with retry suggestion
- **Monitoring:** Check every 60 seconds: `curl https://issuer.{bank_id}.com/health`
- **Communication:** "Issuer {bank_name} experiencing technical difficulties, transactions will be retried"
- **SLA Impact:** No SLA impact if circuit breaker properly configured (external dependency)

**Scenario 4: Deployment Regression**
- **Detection:** `error_rate` increased from 0.1% to 5% immediately after deployment
- **Immediate Action:** Initiate rollback: `kubectl rollout undo deployment payment-service`
- **Verification:** Monitor error rate, should return to baseline within 5 minutes
- **Investigation:** Pull logs from failed deployment: `kubectl logs -l version=v1.2.3 --since=10m`
- **Communication:** "Deployment rolled back due to elevated error rate, investigating root cause"
- **SLA Impact:** 5-10 minutes elevated error rate during detection and rollback

**Scenario 5: Error Budget Near Depletion**
- **Detection:** `error_budget.remaining < 10%` with 15 days remaining in month
- **Immediate Action:** Implement deployment freeze: Update CI/CD pipeline to require VP approval
- **Investigation:** Analyze error budget consumption by component: `group by service_name`
- **Communication:** Notify engineering teams of freeze and reason
- **Prevention:** Schedule incident review meeting to identify recurring failure patterns
- **SLA Impact:** Proactive action to prevent future SLA breach

---

## Document Maintenance

**Last Updated:** 2026-02-01  
**Review Frequency:** Quarterly or after major SLA-impacting incidents  
**Owner:** Site Reliability Engineering Team  
**Approvers:** VP of Engineering, Chief Compliance Officer  
**Related Documents:**
- Incident Response Playbook
- Database Failover Procedures
- Deployment Runbook
- Merchant Communication Templates
- Regulatory Reporting Procedures