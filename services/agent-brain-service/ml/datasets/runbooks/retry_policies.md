# Retry Policies

1. Overview
- Scope: retry behavior for failed payment attempts and downstream calls (authorizations, captures, reversals, settlement).
- Purpose: reduce client-visible failures while preventing amplification of downstream outages and duplicate charging.

2. Common failure patterns
- Retry storm: many retries in a short window causing higher downstream load and increased error rates.
- Flat success rate despite higher retry_count per transaction.
- Increasing p95/p99 latency correlated with rising retries.
- Duplicate transactions detected due to missing idempotency or inconsistent keys.
- Recursive retries caused by intermediate services retrying on timeouts (client + gateway + acquirer).
- Threshold flapping: transient improvements followed by repeat failures as retries resume.
- Sparse success only after many retries, indicating transient issuer-side issues.

3. Observable signals (metrics/logs)
- Distribution of retry_count per transaction (median, 90th, max).
- Retry success rate vs initial attempt success rate.
- Duplicate transaction rate (same idempotency_key or correlated payment token).
- Time-to-final-state (success/failure) distribution.
- Queue length for retry worker processes and backlog growth.
- Increase in downstream error codes during high retry windows.
- Correlation between retry volume and request latencies at downstream services.
- Alerts for worker crashes or OOMs within retry subsystems.

4. Probable root causes
- Non-idempotent operations combined with repeated client retries.
- Misclassification of retryable vs non-retryable errors (e.g., treating issuer_declined as retryable).
- Tight fixed retry intervals (no jitter) creating synchronized bursts.
- Multiple systems implementing independent retry policies without coordination.
- Timeouts shorter than downstream processing windows, causing premature retries.
- Lack of per-merchant or per-issuer backoff control.
- Background retry workers mis-scheduled or unthrottled.

5. Safe mitigation actions
- Classify and centralize error taxonomy: map which error codes are retryable, which are not.
- Enforce idempotency keys on operations that change state; verify uniqueness semantics.
- Implement exponential backoff with jitter; prefer randomized windows to avoid thundering herd.
- Apply per-entity (merchant, issuer, card) retry budgets and throttles.
- Introduce sliding-window circuit breakers that block retries when downstream error rates exceed threshold.
- Limit maximum retry_count and implement monotonic backoff escalation.
- Stall or pause retries when downstream service reports degraded capacity (health-check driven).
- Route retries to alternate processors/acquirers only when validated for idempotency and liability.
- Ensure retry worker pools are autoscaled and have bounded queue sizes; apply backpressure when full.
- Add observability: per-retry attempt logs with idempotency_key and final outcome.
- When duplicate-charge risk exists, halt retries and escalate if pending confirmation within timeout window.

6. Actions requiring human approval
- Changing global retry_count or global backoff strategy.
- Per-merchant permanent override to disable retries or change idempotency semantics.
- Permanent change to duplicate-detection logic or reconciliation windows.
- Releasing a paused retry queue back into production after a large incident without postmortem approval.
- Any change increasing financial exposure (e.g., increasing retry aggressiveness for high-value transactions).

7. What NOT to do
- Do not increase retry frequency to “force” success during a downstream outage.
- Do not remove idempotency protections to simplify retry behavior.
- Do not synchronize retry attempts across services (avoid fixed aligned retry intervals).
- Do not perform blind global policy flips during an incident; prefer scoped, timeboxed changes.
- Do not treat all failures as retryable — distinguish between transient, permanent, and business-level declines.

8. Regulatory / compliance notes
- Duplicate charge mitigation: maintain traceable evidence (logs, timestamps, idempotency keys) to resolve disputes.
- Audit trails for retries are required for dispute resolution and for meeting PCI and local reconciliation rules.
- Changes that increase risk of unauthorized fund movement require legal/compliance signoff.
- Retention of logs and reconciliation artifacts must comply with local data retention regulations (e.g., financial record-keeping laws).




# Retry Policies

## Overview
Retries can improve authorization success but can destabilize systems
if misapplied. Retry behavior must be conservative, targeted, and bounded.

## Common Failure Patterns
- Retry storms during downstream outages
- Increased latency with no success improvement
- Duplicate authorizations or captures
- Recursive retry loops across services
- Issuer throttling triggered by excessive retries

## Observable Signals (Metrics / Logs)
- Rising retry_count per transaction
- Flat or declining success rate despite retries
- Latency growth proportional to retry attempts
- Increased duplicate transaction identifiers
- Elevated reversal or timeout rates

## Probable Root Causes
- Downstream dependency outage
- Misconfigured retry thresholds
- Non-idempotent retry logic
- Uniform retry policy applied to all failure types
- Network or issuer timeouts misclassified as transient

## Safe Mitigation Actions
- Reduce retry attempts globally or per issuer
- Increase exponential backoff intervals
- Disable retries for deterministic declines
- Enforce idempotency keys strictly
- Apply failure-type-aware retry logic

## Actions Requiring Human Approval
- Global retry policy changes
- Merchant-specific retry overrides
- Changes impacting settlement timing
- Retry behavior affecting network quotas

## What NOT to Do
- Do not retry indefinitely
- Do not retry identical failures rapidly
- Do not retry regulatory or fraud declines
- Do not bypass idempotency safeguards

## Regulatory / Compliance Notes
- Excessive retries may violate network rules
- Duplicate charges must be prevented
- Retry decisions must be traceable




# Payment Retry Policies

## Overview

Retry mechanisms are critical for improving payment success rates by re-attempting failed transactions that may succeed on subsequent attempts. However, improper retry implementation can transform isolated failures into systemic outages, create duplicate charges, violate network rules, and damage customer relationships.

Effective retry strategies must balance:
- **Success rate improvement**: Recovering from transient failures to increase transaction completion
- **System stability**: Preventing retry storms that overwhelm downstream systems
- **Cost management**: Minimizing unnecessary processing costs and network fees
- **Customer experience**: Avoiding duplicate charges and excessive delays
- **Regulatory compliance**: Adhering to card network rules and consumer protection laws

Key principles:
- Not all failures should be retried (permanent failures require different handling)
- Retry timing matters as much as retry count
- Context-aware retry logic performs better than fixed policies
- Monitoring and circuit breakers prevent retry storms
- Retry behavior must be auditable for compliance and debugging

This runbook covers:
- Identifying retriable vs non-retriable failures
- Optimal retry strategies by failure type
- Implementing exponential backoff and jitter
- Circuit breaker patterns for failure containment
- Monitoring and alerting for retry effectiveness
- Preventing duplicate transactions and idempotency
- Network-specific retry requirements (Visa, Mastercard, ACH)

## Common Failure Patterns

### Retry Storm Amplification

**Characteristics**
- Initial failure rate increases from 5% to 10%
- Automatic retry policy triggers 3 retries per failed transaction
- Effective load increases from 100 TPS to 130 TPS (100 + 30% * 3 retries)
- Increased load causes further failures, triggering more retries
- Cascading effect: 10% failures → 20% failures → 40% failures
- System overwhelmed within 5-15 minutes of initial degradation
- P95 latency increases from 500ms to 30+ seconds

**Observable indicators**
- `retry_count_per_transaction` metric spiking from avg 0.3 to 2.5+
- `total_requests` growing faster than `unique_payment_attempts`
- Ratio of `retry_requests / initial_requests` exceeding 1.5
- Queue depth growing exponentially
- Connection pool exhaustion
- Circuit breakers triggering in downstream services
- Database connection saturation

**Root causes**
- Downstream dependency degradation (issuer slowness, network issues)
- Aggressive retry policy (immediate retries, high retry count)
- No exponential backoff implementation
- Missing circuit breakers
- Retry logic not respecting backpressure signals
- Synchronous retry blocking request threads
- No retry budget or rate limiting

**Impact**
- Complete service outage within minutes
- Extended recovery time (30+ minutes after root cause resolved)
- Customer-facing timeouts and errors
- Merchant revenue loss
- Potential data inconsistencies
- High infrastructure costs (compute, network, database)

### Latency Inflation Without Success Improvement

**Characteristics**
- Retry logic adds 3-10 seconds to failed transaction processing
- Success rate remains flat at 75% despite retries
- Customer-facing latency increases from 2s to 15s average
- Retry success rate <10% (90% of retries also fail)
- Resources consumed on unproductive retries
- Queue buildup as retries block new requests

**Observable indicators**
- `transaction.total_duration` p95 increasing from 5s to 30s
- `payment.success_rate_with_retries` similar to `payment.success_rate_without_retries`
- `retry.success_rate` below 15%
- `retry.latency` comprising >50% of total transaction time
- High `retry.timeout_rate` indicating retries timing out
- Merchant complaints about slow checkout experience

**Root causes**
- Retrying hard failures that will never succeed (invalid card, expired card)
- Downstream system completely unavailable (not degraded)
- Network-level failures affecting all attempts
- Retry timing too short for system recovery
- Missing decline code analysis before retry
- Retrying during known maintenance windows

**Impact**
- Poor customer experience (long wait times)
- Cart abandonment increase (30-50% when latency >10s)
- Higher infrastructure costs without benefit
- Thread pool exhaustion from blocking retries
- Cascading latency to other services

### Duplicate Transaction Attempts

**Characteristics**
- Same payment processed multiple times
- Customer charged twice or more for single purchase
- Merchant receives multiple authorizations for same transaction
- Reconciliation challenges between systems
- Chargeback risk from customer disputes

**Observable indicators**
- `duplicate_transaction_alerts` firing
- Same `idempotency_key` appearing multiple times with different outcomes
- Customer complaints about multiple charges
- Merchant reports of duplicate authorizations
- Accounting discrepancies in settlement reports
- `transaction.duplicate_rate` above 0.1%

**Root causes**
- Retry triggered after successful but slow response
- Network timeout causing retry while original still processing
- Missing or improper idempotency key usage
- Race condition in distributed retry logic
- Client-side retry in addition to server-side retry
- Improper handling of 5xx errors (retriable but transaction may have succeeded)
- Message queue duplicate delivery

**Impact**
- Customer dissatisfaction and support costs
- Chargeback fees ($15-$25 per chargeback)
- Potential card network fines for excessive duplicate transactions
- Reconciliation overhead
- Trust and reputation damage
- Refund processing costs and delays

### Incorrect Retry Escalation

**Characteristics**
- Failed transaction retried with increased aggression
- Retry delays decreased instead of increased
- Retry count increased during outages
- Retries bypassing rate limits or throttling
- Exponential increase in retry attempts across customer base

**Observable indicators**
- `retry.interval` decreasing over time instead of increasing
- `retry.count` exceeding configured maximum
- `retry.rate` increasing during high failure periods
- Circuit breaker `OPEN` state with continued retry attempts
- Load on downstream system increasing during its degradation

**Root causes**
- Misconfigured retry backoff (linear instead of exponential)
- Missing or broken circuit breaker implementation
- Retry logic not respecting system health signals
- Individual request retries not coordinating globally
- Customer frustration leading to manual re-attempts
- Frontend retry logic conflicting with backend retry

**Impact**
- Prolonged outages due to preventing system recovery
- Issuer or processor penalties for excessive traffic
- Permanent blocking by downstream systems
- Extended recovery time (hours instead of minutes)
- Brand reputation damage

### Recursive Retry Loops

**Characteristics**
- Service A retries to Service B
- Service B retries to Service C
- Service C fails, causing B to retry, causing A to retry
- Exponential multiplication of retries through the stack
- 1 customer request generates 27 backend requests (3^3 retries)

**Observable indicators**
- `request_depth` metrics showing unusual depths (>5 levels)
- Distributed tracing showing retry loops and cycles
- Exponential increase in backend traffic vs frontend traffic
- `request.fanout_ratio` exceeding 10:1
- Cross-service call graphs showing amplification

**Root causes**
- Each service implementing independent retry without coordination
- Missing context propagation about retry attempts
- No circuit breakers at service boundaries
- Synchronous retry chains
- Lack of overall retry budget across system
- Missing request depth tracking

**Impact**
- Massive resource waste (CPU, memory, network)
- Cascading failures across multiple services
- Difficult-to-diagnose performance issues
- Very long recovery times
- Database and cache exhaustion

### Issuer-Specific Retry Failures

**Characteristics**
- Specific issuer explicitly requesting no retries (decline code or message)
- Issuer rate limiting causing increased failures on retry
- Issuer-specific maintenance windows making retries futile
- BIN-specific retry restrictions

**Observable indicators**
- `issuer.retry_success_rate` significantly lower than average for specific issuer
- Decline codes indicating "do not retry" (61 - exceed withdrawal limit, 65 - exceeds frequency limit)
- Error messages containing "do not retry" or "call issuer"
- Issuer-specific timeout rates elevated
- Correlation with known issuer maintenance schedules

**Root causes**
- Issuer experiencing systematic issues
- Issuer implementing aggressive rate limiting
- Issuer requesting specific retry behavior via network
- Card network rules restricting retries for certain conditions
- Issuer fraud system becoming more aggressive on retries

**Impact**
- Wasted retry attempts
- Customer frustration with multiple failure messages
- Potential issuer penalties or throttling
- Cart abandonment
- Negative customer experience

### Network Protocol Retry Issues

**Characteristics**
- TCP connection failures causing application-level retries
- DNS resolution failures triggering full payment retries
- TLS handshake failures being retried at payment level
- Load balancer timeouts causing duplicate requests

**Observable indicators**
- High `connection.retry_rate` metrics
- `dns.lookup_failure_rate` elevated
- `tls.handshake_failure_rate` above baseline
- Network-level errors (ECONNREFUSED, ETIMEDOUT) in logs
- Same transaction attempting multiple TCP connections

**Root causes**
- Network infrastructure issues
- DNS propagation delays or failures
- Certificate expiration or misconfiguration
- Load balancer health check failures
- Firewall or security group rule changes
- Geographic routing issues

**Impact**
- Unnecessary payment retries for network issues
- Increased latency from network-level retries
- Potential duplicate transactions
- Difficult debugging (network vs application issue)

## Observable Signals

### Retry Effectiveness Metrics

**Success and conversion metrics**
- `retry.first_attempt_success_rate`: Baseline success without retries (target: 85-95%)
- `retry.final_success_rate`: Success rate including retries (target: 90-98%)
- `retry.incremental_success`: Improvement from retries (target: 5-10%)
- `retry.success_rate_by_attempt`: Success rate for attempt 1, 2, 3 (decreasing pattern expected)
- `retry.conversion_rate`: Percentage of initial failures recovered by retry (target: 40-60%)
- `retry.marginal_value`: Success gain per additional retry attempt (should decrease)

**Sample targets and thresholds**
```
retry.first_attempt_success_rate: 88% (alert if < 85%)
retry.second_attempt_success_rate: 35% (of first attempt failures)
retry.third_attempt_success_rate: 15% (of second attempt failures)
retry.final_success_rate: 94%
retry.incremental_success: 6% (94% - 88%)
```

**Volume and load metrics**
- `retry.total_count`: Total retry attempts across all transactions
- `retry.attempts_per_transaction`: Average retries per transaction (target: <0.5)
- `retry.transaction_percentage`: Percentage of transactions retried (target: <15%)
- `retry.volume_amplification`: Ratio of total requests to unique transactions (target: <1.3)
- `retry.load_multiplier`: Impact on system load from retries (should be <30%)
- `retry.count_distribution`: P50, P95, P99 of retry counts per transaction

**Timing and latency metrics**
- `retry.delay.first`: Time before first retry (target: 2-5 seconds)
- `retry.delay.second`: Time before second retry (target: 5-15 seconds)
- `retry.delay.third`: Time before third retry (target: 15-45 seconds)
- `retry.total_duration`: Total time spent on retries per transaction
- `retry.latency_contribution`: Percentage of total latency from retries (target: <40%)
- `retry.wait_time.p95`: 95th percentile time spent waiting for retries

**Error and decline code analysis**
- `retry.hard_decline_retry_rate`: Retries on non-retriable declines (target: <1%)
- `retry.by_decline_code`: Success rate breakdown by original decline code
- `retry.timeout_rate`: Percentage of retries timing out (target: <5%)
- `retry.by_error_type`: Retry distribution by error category (network, issuer, gateway)
- `retry.duplicate_detection_rate`: Potential duplicate transactions caught (target: >99%)

### System Health Indicators

**Load and resource utilization**
- `retry.queue_depth`: Number of pending retry attempts
- `retry.queue_age`: Time oldest retry has been waiting
- `retry.thread_utilization`: Percentage of threads handling retries
- `retry.connection_pool_usage`: Connection pool saturation from retries
- `retry.cpu_usage`: CPU consumption attributable to retry logic
- `retry.memory_pressure`: Memory used for retry state management

**Circuit breaker metrics**
- `circuit_breaker.state`: CLOSED, OPEN, HALF_OPEN per issuer/service
- `circuit_breaker.failure_threshold`: Failures before tripping (e.g., 50%)
- `circuit_breaker.recovery_interval`: Time before testing recovery (e.g., 60s)
- `circuit_breaker.trip_count`: Number of times tripped in time window
- `circuit_breaker.request_rejection_rate`: Requests blocked by open circuit

**Backpressure signals**
- `retry.backpressure_active`: Boolean indicating retry throttling active
- `retry.shed_rate`: Percentage of retries dropped due to overload
- `retry.budget_exhausted`: Retry budget depletion indicator
- `retry.rate_limit_hits`: Times retry rate limiter engaged
- `retry.downstream_capacity`: Available capacity at retry target

### Failure Pattern Detection

**Retry storm indicators**
- Rapid increase in `retry.volume_amplification` (>2x in 5 minutes)
- `retry.attempts_per_transaction` exceeding 2.0
- Exponential growth in `retry.total_count`
- `system.total_requests` growing faster than `business.payment_volume`
- Queue depths increasing across multiple services
- P95 latency correlation with retry volume increase

**Duplicate transaction signals**
- `idempotency.collision_rate`: Same idempotency key with different results
- `duplicate.detection_count`: Suspected duplicates caught
- `duplicate.authorization_rate`: Multiple auths for same transaction
- Time gap between duplicate attempts (<5 seconds suspicious)
- Customer complaints about duplicate charges

**Ineffective retry patterns**
- Flat `retry.success_rate_by_attempt` (similar success across attempts)
- High `retry.timeout_rate` (>20%)
- No improvement in `retry.final_success_rate` vs baseline
- High `retry.same_error_rate`: Same error on all retry attempts
- Low `retry.conversion_rate` (<20%)

### Alert Triggers and Thresholds

**Critical alerts (immediate page)**
```
CRITICAL: Retry storm detected
  - retry.volume_amplification > 3.0
  - retry.attempts_per_transaction > 3.0
  - Sustained for > 5 minutes
  
CRITICAL: Circuit breaker failures
  - circuit_breaker.trip_rate > 5 per minute
  - circuit_breaker.state = OPEN for critical issuer
  - Duration > 10 minutes

CRITICAL: Duplicate transaction rate elevated
  - duplicate.detection_count > 10 per minute
  - idempotency.collision_rate > 1%
  - Customer complaints > 5 per hour
```

**Warning alerts (investigate)**
```
WARNING: Retry effectiveness degraded
  - retry.incremental_success < 3%
  - retry.conversion_rate < 25%
  - Sustained for > 30 minutes

WARNING: Retry latency impact high
  - retry.latency_contribution > 50%
  - retry.total_duration.p95 > 20 seconds
  - Customer experience impact likely

WARNING: Hard decline retry rate elevated
  - retry.hard_decline_retry_rate > 5%
  - Wasting resources on non-retriable errors
  - Need retry logic refinement
```

**Informational alerts (monitor)**
```
INFO: Retry pattern change detected
  - retry.success_rate_by_attempt shifted significantly
  - Issuer retry behavior changed
  - May need policy adjustment

INFO: Seasonal retry pattern
  - retry.transaction_percentage elevated during peak hours
  - Expected behavior but monitor for excessive growth
  - Capacity planning may be needed
```

### Logging Patterns

**Structured retry logs**
```json
{
  "event": "payment_retry",
  "transaction_id": "txn_abc123",
  "idempotency_key": "idem_xyz789",
  "attempt_number": 2,
  "original_error": "issuer_timeout",
  "original_error_code": "timeout",
  "retry_reason": "retriable_timeout",
  "retry_delay_ms": 3000,
  "backoff_strategy": "exponential_with_jitter",
  "max_attempts": 3,
  "issuer_id": "chase_us",
  "amount_cents": 9999,
  "currency": "USD",
  "timestamp": "2026-02-01T14:23:45.123Z"
}
```

**Retry outcome logs**
```json
{
  "event": "retry_outcome",
  "transaction_id": "txn_abc123",
  "total_attempts": 3,
  "final_status": "success",
  "successful_attempt": 2,
  "total_duration_ms": 8500,
  "retry_contribution_ms": 6000,
  "errors_encountered": ["issuer_timeout", "network_error"],
  "circuit_breaker_state": "CLOSED",
  "duplicate_detected": false
}
```

**Retry storm detection logs**
```
ERROR: Retry storm detected for issuer=BARCLAYS_UK
  - Current retry rate: 450 retries/sec (normal: 50/sec)
  - Volume amplification: 4.2x (threshold: 2.0x)
  - Circuit breaker triggered: YES
  - Mitigation: Reduced max retries from 3 to 1
  - Expected recovery: 5-10 minutes
```

## Probable Root Causes

### Configuration and Policy Errors

**Retry count misconfiguration**
- Maximum retry count set too high (>5 retries)
- No retry count limit (infinite retries possible)
- Retry count not adjusted based on failure type
- Same retry policy applied to all transaction types
- Retry count increased during debugging and not reverted
- Per-customer retry override creating inconsistent behavior

**Backoff strategy errors**
- Linear backoff instead of exponential (1s, 2s, 3s instead of 1s, 2s, 4s)
- Missing jitter causing synchronized retries (thundering herd)
- Backoff delays too short (<1 second between retries)
- Backoff delays too long (>60 seconds causing customer abandonment)
- Maximum backoff not configured (unbounded delay)
- Backoff not resetting between different transactions

**Retry condition misidentification**
- Hard declines being retried (invalid card, fraud)
- Successful-but-slow responses triggering retries
- Network errors not distinguished from application errors
- Timeout values set incorrectly causing premature retry
- Missing decline code analysis
- Retriable/non-retriable classification errors

### System Architecture Issues

**Missing circuit breakers**
- No circuit breaker implementation for critical dependencies
- Circuit breaker thresholds too high (allowing too many failures)
- Circuit breaker thresholds too low (triggering unnecessarily)
- Circuit breaker not coordinated across instances
- Half-open state allowing too much traffic
- Circuit breaker recovery testing inadequate

**Synchronous retry blocking**
- Retries executing synchronously on request thread
- Thread pool exhaustion from blocking retries
- Request queue buildup from slow retries
- Lack of async retry processing
- No retry queue or scheduler implementation
- Retries blocking other transaction processing

**Distributed retry coordination failures**
- Multiple systems independently retrying same transaction
- Client-side and server-side retries compounding
- Load balancer retry in addition to application retry
- No distributed retry budget or coordination
- Request ID not propagated causing retry amplification
- Retry state not shared across instances

### Dependency and Integration Issues

**Downstream system behavior**
- Issuer system returning retriable errors for non-retriable conditions
- Network infrastructure intermittently failing
- Third-party service timeout values too aggressive
- Downstream service not honoring idempotency keys
- Retry-After headers not being respected
- Backpressure signals not being sent or observed

**Network and connectivity**
- DNS failures causing full transaction retries
- TCP connection pool exhaustion
- TLS handshake failures
- Network timeout values mismatched with retry timeouts
- Load balancer health checks causing false failures
- Geographic routing changes causing latency spikes

**External service reliability**
- Payment processor experiencing intermittent outages
- Issuer bank degraded performance
- Card network regional issues
- Fraud screening service timeouts
- Currency conversion service unavailability
- Identity verification service slowness

### State Management Problems

**Idempotency failures**
- Idempotency key not generated or propagated
- Idempotency key expiring too quickly
- Idempotency key not checked before retry
- Multiple different idempotency keys for same transaction
- Idempotency storage system failures
- Race conditions in idempotency checking

**Transaction state tracking**
- Lost transaction state between retry attempts
- Inconsistent state across distributed systems
- State not persisted before retry
- Retry state not cleaned up after completion
- Stale retry state causing incorrect decisions
- Missing transaction lifecycle events

**Duplicate detection failures**
- Duplicate detection not implemented
- Duplicate detection window too short
- Duplicate detection criteria too loose
- Database query performance issues in duplicate checking
- Race conditions allowing duplicates through
- Missing unique constraints in database

### Monitoring and Observability Gaps

**Insufficient retry metrics**
- Retry attempts not tracked or logged
- No visibility into retry effectiveness
- Missing decline code-specific metrics
- Lack of issuer-specific retry tracking
- No retry latency breakdown
- Insufficient alerting on retry patterns

**Poor correlation and tracing**
- Distributed traces not connecting retry attempts
- Request IDs not propagated through retries
- Missing context in retry logs
- Inability to track single transaction across retries
- No retry path visualization
- Difficult to correlate retries with system load

## Safe Mitigation Actions

### Immediate Response (0-15 minutes)

**Reduce retry aggressiveness**
- **Lower retry count**: Reduce from 3 to 1 or 0 for affected service/issuer
  - Configuration: `payment.retry.max_attempts = 1`
  - Feature flag: Enable `retry_reduction_emergency_mode`
  - Scope: Can be global, per-issuer, or per-service
  - Expected impact: 60-70% reduction in retry volume
  - Monitor: Watch for drop in final success rate (acceptable 2-5% reduction)

- **Increase retry delays**: Expand exponential backoff intervals
  - Before: 1s, 2s, 4s delays
  - After: 3s, 9s, 27s delays (3x increase)
  - Add jitter: ±30% randomization to prevent thundering herd
  - Implementation: `retry.delay = base_delay * (backoff_factor ^ attempt) * random(0.7, 1.3)`
  - Expected impact: Spread retry load over time, reduce burst traffic

**Activate circuit breakers**
- **Enable circuit breaker for degraded services**
  - Threshold: 50% failure rate over 1-minute window
  - Action: Open circuit after threshold breach
  - Recovery: Test every 60 seconds with 10% of traffic (half-open)
  - Full recovery: 95% success rate for 5 minutes before fully closing
  - Bypass: Allow manual override with approval for critical transactions

- **Implement fail-fast logic**
  - Skip retries when circuit breaker is OPEN
  - Immediately return failure to customer with clear message
  - Provide alternative payment methods when available
  - Reduce resource consumption during outages
  - Faster customer feedback rather than long waits

**Enable retry throttling**
- **Implement retry rate limiting**
  - Token bucket algorithm: 100 retries per second per issuer
  - Burst allowance: 150 retries for temporary spikes
  - Scope: Per-issuer rate limits to prevent overloading specific banks
  - Overflow handling: Queue retries up to 1000 deep, then drop
  - Monitoring: Track rate limit hits and dropped retries

- **Activate retry budget system**
  - Global retry budget: Maximum 30% of total traffic can be retries
  - Per-customer budget: Maximum 3 retries per customer per hour
  - Budget replenishment: Gradual increase as system stabilizes
  - Budget exhaustion: Fail fast when budget depleted
  - Priority: High-value transactions get retry budget priority

### Short-term Stabilization (15-60 minutes)

**Implement intelligent retry logic**
- **Decline code-based retry decisions**
  - Never retry: 04 (pick up card), 07 (fraud), 14 (invalid card), 41 (lost), 43 (stolen)
  - Always retry once: 05 (do not honor), 51 (insufficient funds), timeout errors
  - Retry with delay: Network errors, 5xx errors, issuer unavailable
  - Configuration: `retry.decline_code_policy` mapping
  - Validation: Test against historical decline code patterns

- **Temporal awareness in retry logic**
  - Skip retries during known maintenance windows
  - Reduce retries during issuer peak hours
  - Increase retry delays during high failure periods
  - Calendar integration for scheduled issuer maintenance
  - Real-time issuer health score influencing retry decisions

**Enhance observability**
- **Deploy detailed retry metrics**
  - Per-issuer retry success rates
  - Per-decline-code retry effectiveness
  - Retry latency breakdowns (P50, P95, P99)
  - Retry volume trending (hourly, daily)
  - Circuit breaker state changes
  - Real-time dashboards for incident response

- **Enable enhanced logging**
  - Log all retry attempts with full context
  - Include: attempt number, delay used, decline code, issuer response
  - Sampling: 100% during incidents, 5% during normal operations
  - Structured logging for easy querying
  - Distributed tracing correlation IDs
  - Retention: 72 hours for incident analysis

**Implement duplicate prevention**
- **Strengthen idempotency checks**
  - Generate idempotency keys at earliest point in flow
  - Propagate idempotency key through all retry attempts
  - Store idempotency state in distributed cache (Redis, Memcached)
  - TTL: 24 hours minimum for idempotency records
  - Check before every retry attempt
  - Return previous result if idempotency key matched

- **Add duplicate transaction detection**
  - Check for recent identical transactions (same card, amount, merchant)
  - Time window: 5 minutes for duplicate detection
  - Similarity threshold: Exact match on card PAN, amount, merchant
  - Action: Block suspected duplicate, alert for review
  - Customer communication: "This appears to be a duplicate transaction"

### Medium-term Optimization (1-24 hours)

**Analyze retry effectiveness**
- **Data-driven retry policy optimization**
  - Calculate retry success rate by decline code
  - Identify which errors benefit from retry (>20% success on retry)
  - Determine optimal retry delays per error type
  - Measure customer abandonment vs retry latency tradeoff
  - A/B test different retry strategies (10% of traffic)

- **Issuer-specific retry tuning**
  - Analyze per-issuer retry success patterns
  - Identify issuers where retries are ineffective (<15% success)
  - Customize retry policies per issuer
  - Maintain issuer health scores for dynamic adjustment
  - Coordinate with issuers on optimal retry behavior

**Implement advanced retry strategies**
- **Adaptive retry policies**
  - Dynamically adjust retry count based on recent success rate
  - If retry success rate >40%, allow up to 3 retries
  - If retry success rate <15%, reduce to 1 retry
  - Continuous learning from retry outcomes
  - Gradual policy adjustments (no sudden changes)

- **Contextual retry decisions**
  - High-value transactions (>$500): More aggressive retries (up to 5 attempts)
  - Low-value transactions (<$10): Single retry only
  - Returning customers: More retries than new customers
  - Subscription payments: Different strategy than one-time purchases
  - Time-sensitive transactions: Shorter retry delays

**Deploy circuit breaker improvements**
- **Fine-tune circuit breaker thresholds**
  - Test different failure thresholds (30%, 50%, 70%)
  - Optimize recovery interval (30s, 60s, 120s)
  - Adjust half-open traffic percentage (5%, 10%, 25%)
  - Measure false positive vs false negative tradeoffs
  - Document optimal settings per dependency

- **Implement cascading circuit breakers**
  - Service-level circuit breakers (e.g., payment gateway)
  - Issuer-level circuit breakers (e.g., Chase, Bank of America)
  - Geographic circuit breakers (e.g., US region, EU region)
  - Prevent localized issues from causing global circuit trips
  - Coordinate circuit breaker state across instances

**Improve async processing**
- **Implement async retry queue**
  - Move retries off critical request path
  - Use message queue (SQS, Kafka, RabbitMQ) for retry scheduling
  - Process retries asynchronously in background workers
  - Customer receives immediate response, retry happens separately
  - Callback or webhook to notify customer of final outcome

- **Schedule delayed retries**
  - Use distributed scheduler (Celery, Temporal, AWS Step Functions)
  - Precisely control retry timing
  - Distribute retry load evenly over time
  - Avoid retry thundering herds
  - Enable complex retry workflows (e.g., increasing delays, fallbacks)

### Long-term Improvements (24 hours - weeks)

**Architecture enhancements**
- **Distributed retry coordination**
  - Centralized retry orchestration service
  - Global retry budget management
  - Cross-service retry visibility
  - Prevent retry amplification through stack
  - Request depth tracking and limiting

- **Resilience patterns**
  - Bulkhead pattern: Isolate retry resources per issuer
  - Timeout patterns: Aggressive timeouts with appropriate retries
  - Fallback patterns: Alternate payment methods on retry exhaustion
  - Graceful degradation: Reduced functionality during high retry periods
  - Chaos engineering: Test retry behavior under various failures

**Machine learning for retry optimization**
- **Predictive retry modeling**
  - ML model predicting retry success probability
  - Features: decline code, issuer, time of day, customer history, amount
  - Output: Should retry? With what delay? How many times?
  - Continuous model training from retry outcomes
  - A/B testing model-driven vs rule-based retries

- **Anomaly detection**
  - Detect unusual retry patterns automatically
  - Alert on retry storms early (before major impact)
  - Identify new failure modes requiring policy updates
  - Adaptive thresholds based on recent behavior
  - Automatic mitigation trigger for critical anomalies

**Process and governance**
- **Retry policy as code**
  - Version control for retry configurations
  - Code review for retry policy changes
  - Automated testing of retry logic
  - Gradual rollout of policy changes (canary, blue-green)
  - Rollback capability for policy changes

- **Retry effectiveness reviews**
  - Weekly retry metrics review
  - Monthly retry policy optimization sessions
  - Quarterly deep dives on retry behavior
  - Annual retry strategy refresh
  - Continuous improvement culture

## Actions Requiring Human Approval

### Operational Policy Changes

**Global retry policy modifications**
- **Approval required from**: 
  - Engineering Director or VP Engineering
  - Principal Engineer (Payments)
  - Site Reliability Engineering Lead
- **Required analysis**:
  - Current policy effectiveness metrics
  - Proposed policy with rationale
  - Expected impact on success rate, latency, load
  - Rollback plan and success criteria
  - A/B test results (if available)
- **Testing requirements**:
  - Comprehensive unit tests for retry logic
  - Integration tests with retry scenarios
  - Load testing with expected retry volumes
  - Shadow mode testing with production traffic
  - Staged rollout: 1%, 10%, 50%, 100%
- **Monitoring plan**:
  - Enhanced monitoring during rollout
  - Alert thresholds adjusted for expected changes
  - Rollback triggers clearly defined
  - Post-deployment validation checkpoints

**Issuer-specific retry suppression**
- **Approval required from**:
  - Payments Operations Manager
  - Engineering Manager (Payments)
  - Account Manager (for major issuers)
- **Justification required**:
  - Issuer retry success rate <10% for 7+ days
  - Explicit issuer request to stop retries
  - Network rules or regulations prohibiting retries
  - Issuer penalties or warnings received
- **Documentation**:
  - Historical retry effectiveness data for issuer
  - Issuer communication or evidence
  - Expected revenue impact
  - Customer communication plan
  - Reversal criteria and timeline
- **Review cadence**: Re-evaluate every 30 days for continuation

**Retry budget allocation changes**
- **Approval required from**:
  - Engineering Director
  - Product Management (for customer impact)
  - Finance (for cost implications)
- **Scope**: Changes to global retry budget limits
- **Considerations**:
  - Infrastructure cost impact
  - Customer success rate impact
  - Competitive positioning
  - Technical debt and complexity
- **Rollout**: Gradual adjustment over 7-14 days with monitoring

### High-risk Technical Changes

**Circuit breaker modifications for critical dependencies**
- **Approval required from**:
  - Site Reliability Engineering Lead
  - Engineering Manager
  - On-call Engineer Lead (if during incident)
- **Critical dependencies**: Core payment processor, primary issuers, card networks
- **Change process**:
  - Detailed failure scenario analysis
  - Threshold justification with data
  - Impact assessment on availability and success rate
  - Testing in staging with simulated failures
  - Phased deployment with rollback plan
- **Emergency override**: CTO or VP Engineering for P0 incidents

**Retry timeout adjustments**
- **Approval required from**:
  - Principal Engineer (Payments)
  - Performance Engineering Lead
- **Analysis required**:
  - Current timeout distribution (P50, P95, P99)
  - Proposed timeout values with rationale
  - Expected impact on customer experience
  - Downstream dependency timeout values
  - Load and capacity implications
- **Testing**: Load testing with new timeout values under various scenarios

**Idempotency window changes**
- **Approval required from**:
  - Payments Architecture Lead
  - Data Engineering Lead (for storage implications)
  - Security Officer (for data retention implications)
- **Considerations**:
  - Storage costs for longer windows
  - Duplicate detection effectiveness
  - Customer dispute window alignment
  - Regulatory requirements
- **Standard window**: 24 hours (changes require strong justification)

### Customer-facing Changes

**Retry behavior communication**
- **Approval required from**:
  - Product Management
  - Customer Communications Lead
  - Legal (for terms of service implications)
- **Trigger**: Significant changes to visible retry behavior
- **Content review**: Legal review of customer-facing messaging
- **Channels**: Help center, merchant documentation, API docs, support training
- **Rollout**: Advance notice for significant changes (30+ days)

**Aggressive retry policy for VIP customers**
- **Approval required from**:
  - Head of Payments
  - Product Management
  - Engineering Director
- **Justification**:
  - Business value of customer segment
  - Technical feasibility and cost
  - Fairness and ethical considerations
  - Regulatory compliance
- **Implementation**: Separate retry policy configuration for customer tier
- **Monitoring**: Track effectiveness and abuse potential

### Cost and Resource Allocation

**Infrastructure scaling for retry capacity**
- **Approval required from**:
  - Engineering Director
  - Finance Director (for budget >$10K monthly)
  - CTO (for budget >$50K monthly)
- **Justification**:
  - Current capacity utilization metrics
  - Expected retry volume growth
  - Impact on success rate and revenue
  - Alternative optimizations considered
  - ROI calculation
- **Procurement**: Standard infrastructure procurement process

**Third-party retry optimization services**
- **Approval required from**:
  - CTO or VP Engineering
  - Procurement
  - Legal (for vendor contracts)
  - Security Officer (for data sharing)
- **Examples**: Intelligent retry routing, ML-powered retry prediction
- **Evaluation criteria**:
  - Vendor reliability and track record
  - Data privacy and security
  - Integration complexity
  - Cost-benefit analysis
  - Competitive alternatives

## What NOT to Do

### Retry Configuration Mistakes

**Do NOT retry indefinitely**
- **Risk**: Resource exhaustion, cost explosion, permanent customer experience degradation
- **Maximum**: 3-5 retries is industry standard
- **Timeout**: Implement total transaction timeout (60-120 seconds)
- **Reason**: Beyond 3-5 retries, success rate improvement is minimal (<5%)
- **Instead**: Fail gracefully, offer alternatives, allow customer to re-initiate

**Do NOT use immediate retries (zero delay)**
- **Risk**: Retry storms, overwhelming downstream systems, no time for recovery
- **Minimum delay**: 1-2 seconds before first retry
- **Reason**: Immediate retry likely to hit same failure condition
- **Exception**: Pure network errors might retry slightly faster (500ms)
- **Instead**: Exponential backoff starting at 1-2 seconds

**Do NOT use same retry policy for all failures**
- **Risk**: Inefficient resource usage, poor customer experience
- **Different strategies needed for**:
  - Network timeouts (aggressive retries)
  - Hard declines (no retries)
  - Soft declines (moderate retries)
  - Issuer unavailable (delayed retries)
  - Fraud declines (no retries, escalate to fraud team)
- **Instead**: Decline code-specific retry policies

**Do NOT retry hard declines**
- **Hard decline codes** (never retry):
  - 04: Pick up card (fraud indicator)
  - 07: Pick up card, special condition (fraud)
  - 14: Invalid card number
  - 41: Lost card
  - 43: Stolen card
  - 57: Transaction not permitted to cardholder
  - 62: Restricted card
- **Risk**: Wasting resources, triggering fraud systems, poor customer experience
- **Customer action**: Prompt to check card details or use different card
- **Instead**: Clear error message, suggest customer contact issuer

**Do NOT implement linear backoff**
- **Linear backoff**: 1s, 2s, 3s, 4s delays
- **Problem**: Doesn't sufficiently spread retry load, still causes thundering herds
- **Exponential backoff**: 1s, 2s, 4s, 8s, 16s delays (2^attempt)
- **With jitter**: Randomize by ±20-30% to prevent synchronized retries
- **Formula**: `delay = min(max_delay, base_delay * (2 ^ attempt) * random(0.7, 1.3))`
- **Instead**: Always use exponential backoff with jitter

### System Design Mistakes

**Do NOT implement synchronous retries on critical path**
- **Risk**: Thread pool exhaustion, request queue buildup, cascading latency
- **Problem**: Each retry blocks a request-handling thread
- **Calculation**: 100 TPS with 3 retries at 10s each = 3000 blocked threads
- **Instead**: Asynchronous retry processing with callback or webhook
- **Architecture**: Message queue for retry scheduling, separate worker pool

**Do NOT ignore circuit breaker signals**
- **Risk**: Prolonging outages, preventing system recovery
- **Behavior**: When circuit is OPEN, fail fast instead of retrying
- **Reason**: System needs time to recover without additional load
- **Testing**: Circuit should enter half-open state periodically
- **Instead**: Respect circuit breaker, provide fallback or clear error message

**Do NOT amplify retries through service layers**
- **Problem**: Service A retries 3x, calls Service B which retries 3x = 9x amplification
- **Risk**: Exponential request multiplication (3 layers = 27x requests)
- **Detection**: Request depth tracking, distributed tracing
- **Instead**: Single retry coordination point, or retry budget shared across layers
- **Pattern**: Caller provides retry budget, callee respects remaining budget

**Do NOT implement retry without idempotency**
- **Risk**: Duplicate transactions, double charging customers
- **Requirement**: Every retriable operation must be idempotent
- **Implementation**: Idempotency keys for all payment requests
- **Storage**: Distributed cache or database for idempotency state
- **TTL**: Idempotency records retained for 24-48 hours minimum
- **Instead**: Always generate and check idempotency keys before retry

### Monitoring and Observability Mistakes

**Do NOT retry without logging**
- **Risk**: Inability to diagnose issues, no visibility into retry effectiveness
- **Required logs**:
  - Each retry attempt with attempt number
  - Original error and retry decision
  - Retry delay used
  - Final outcome after all retries
- **Structured logging**: Use JSON format for easy querying
- **Sampling**: 100% during incidents, 5-10% normally to manage volume
- **Instead**: Comprehensive retry logging with appropriate sampling

**Do NOT ignore retry metrics**
- **Risk**: Retry storms going undetected, ineffective retry policies continuing
- **Key metrics to monitor**:
  - Retry attempts per transaction (should be <0.5 average)
  - Retry success rate by attempt (should decrease: 40%, 20%, 10%)
  - Retry volume amplification (should be <1.5x)
  - Retry latency contribution (should be <30%)
- **Alerting**: Automated alerts on abnormal retry patterns
- **Instead**: Real-time retry dashboards and automated alerting

**Do NOT deploy retry changes without A/B testing**
- **Risk**: Degrading success rate or customer experience
- **Process**: Test new retry policy on 5-10% of traffic
- **Metrics**: Compare success rate, latency, cost between control and test
- **Duration**: Run for 24-48 hours to capture daily patterns
- **Rollback**: Quick rollback if test group shows degradation
- **Instead**: Always validate retry changes with controlled experiments

### Business Logic Mistakes

**Do NOT retry to meet SLA targets**
- **Risk**: Gaming metrics while degrading actual customer experience
- **Wrong approach**: Retry until success to avoid SLA breach
- **Problem**: Hides underlying issues, creates false confidence
- **Customer impact**: Long delays, frustration, cart abandonment
- **Instead**: Address root causes, report accurate SLA compliance

**Do NOT hide failures from customers with retries**
- **Risk**: Customer waiting with no feedback during long retry sequences
- **Problem**: Delays >10 seconds cause significant cart abandonment
- **Customer experience**: "Stuck" on payment screen, no indication of progress
- **Instead**: Show retry progress, offer alternative payment methods, fail gracefully
- **Best practice**: Background retry with customer notification when complete

**Do NOT retry to avoid incident alerts**
- **Risk**: Masking critical issues, delaying proper incident response
- **Wrong approach**: Retry until success to avoid paging on-call
- **Problem**: Underlying issue worsens while retries hide it
- **Consequences**: Eventual catastrophic failure instead of early intervention
- **Instead**: Alert appropriately, investigate root causes, fix underlying issues

**Do NOT use retries to compensate for poor architecture**
- **Risk**: Technical debt accumulation, reliability through brute force
- **Problem**: "Our integration is unreliable, so we retry a lot"
- **Better solutions**:
  - Fix unreliable integrations
  - Implement proper error handling
  - Add circuit breakers and bulkheads
  - Improve monitoring and observability
- **Instead**: Retries are last resort, not primary reliability mechanism

### Compliance and Regulatory Mistakes

**Do NOT violate card network retry rules**
- **Visa retry rules**: Maximum 15 retries per transaction over 30 days
- **Mastercard retry rules**: Specific retry intervals required for recurring
- **Problem**: Excessive retries can result in network fines ($25K-$100K)
- **Monitoring**: Track retry attempts per transaction over extended periods
- **Instead**: Stay well below network limits, implement retry limits

**Do NOT retry without proper authorization**
- **Risk**: Processing unauthorized transactions, PCI compliance violations
- **Requirement**: Valid authorization for each retry attempt
- **Recurring**: Separate authorization rules for subscription retries
- **Customer consent**: Required for retry attempts, especially recurring
- **Instead**: Ensure proper authorization and consent for all retries

**Do NOT ignore duplicate transaction regulations**
- **Risk**: Consumer protection violations, chargeback liabilities
- **Requirement**: Prevent duplicate charges from retry logic
- **Detection**: Robust duplicate detection mechanisms
- **Refunds**: Immediate refund process for confirmed duplicates
- **Reporting**: Track and report duplicate transaction rates
- **Instead**: Idempotency and duplicate detection as primary controls

## Network-Specific Retry Requirements

### Visa Retry Guidelines

**Authorization retry limits**
- Maximum 15 authorization retries per transaction
- Time window: 30 days from initial decline
- Applies to: Recurring transactions, installments, retries after decline
- Monitoring: Track retry count per original transaction ID
- Penalties: Non-compliance can result in network fines

**Retry timing requirements**
- First retry: Minimum 24 hours after initial decline
- Subsequent retries: Increasing intervals (not specified but recommended exponential)
- Exception: Technical failures (timeout, network error) can retry immediately
- Account updater: Use Visa Account Updater for expired/replaced cards

**Prohibited practices**
- Retrying multiple times on same day (except technical failures)
- Retry storms overwhelming issuers
- Retrying hard declines (fraud, lost/stolen, invalid card)
- Not using appropriate retry intervals

### Mastercard Retry Guidelines

**Recurring transaction retries**
- Maximum 2 retries for recurring billing failures
- Retry schedule: 10 days after first attempt, 20 days after second
- Total window: 30 days maximum
- Account updater: Use Automatic Billing Updater (ABU)

**Soft decline handling**
- Immediate retry permitted for network errors and timeouts
- 24-hour minimum for soft declines (insufficient funds)
- Maximum 4 retries over 16 days for recurring
- Different intervals for installment transactions

**Prohibited practices**
- Retrying hard declines without customer action
- Excessive retry frequency (multiple times per day)
- Not implementing account updater services
- Ignoring decline code retry guidance

### American Express Guidelines

**Retry best practices**
- Use OptBlue or direct integration retry guidance
- Respect decline code retry recommendations
- Implement retry delays for soft declines
- Use Account Updater for expired cards

**Special considerations**
- Corporate cards may have different retry requirements
- Authorization amount reservations during retries
- Merchant Category Code (MCC) specific rules

### ACH Retry Guidelines

**NACHA retry rules**
- Maximum 2 retry attempts for returned ACH transactions
- Retry timing: 30 days after original return
- Return codes: Check return code before retry (some not retriable)
- Authorization: Ensure customer authorization remains valid

**Prohibited returns to retry**
- R02: Account closed
- R03: No account / unable to locate
- R04: Invalid account number
- R14: Representative payee deceased or unable to continue
- R15: Beneficiary or account holder deceased
- R16: Account frozen

**Retriable returns**
- R01: Insufficient funds (retry after 30 days)
- R09: Uncollected funds (retry with appropriate delay)
- R20: Non-transaction account (contact customer)

### SEPA Retry Guidelines

**European payment retry rules**
- Varies by country and payment scheme
- Generally more restrictive than US
- Strong Customer Authentication (SCA) may be required for retries
- Regulatory reporting for failed payment retries

**Best practices**
- Comply with PSD2 SCA requirements
- Respect country-specific retry regulations
- Use SEPA Direct Debit for recurring with proper mandates
- Implement appropriate retry delays

## Retry Policy Templates

### Standard E-commerce Retry Policy

```yaml
retry_policy:
  name: "standard_ecommerce"
  max_attempts: 3
  backoff_strategy: "exponential_with_jitter"
  base_delay_seconds: 2
  max_delay_seconds: 30
  backoff_multiplier: 2.0
  jitter_factor: 0.3
  
  retriable_errors:
    - "issuer_timeout"
    - "network_error"
    - "connection_timeout"
    - "gateway_timeout"
    - "issuer_unavailable"
    - "service_unavailable"
    - "rate_limit_exceeded"
    
  non_retriable_errors:
    - "invalid_card"
    - "expired_card"
    - "insufficient_funds"
    - "fraud_decline"
    - "do_not_honor"
    - "card_not_supported"
    
  decline_code_policy:
    "05": { retry: true, max_attempts: 2, delay: 3 }
    "51": { retry: true, max_attempts: 1, delay: 10 }
    "timeout": { retry: true, max_attempts: 3, delay: 2 }
    "14": { retry: false }
    "41": { retry: false }
    "43": { retry: false }
    
  circuit_breaker:
    enabled: true
    failure_threshold: 0.5
    recovery_interval_seconds: 60
    half_open_requests: 10
```

### Subscription/Recurring Payment Retry Policy

```yaml
retry_policy:
  name: "subscription_recurring"
  max_attempts: 4
  backoff_strategy: "scheduled"
  
  retry_schedule:
    - delay_days: 3
    - delay_days: 7
    - delay_days: 14
    - delay_days: 21
    
  retriable_errors:
    - "insufficient_funds"
    - "expired_card"
    - "issuer_timeout"
    - "card_not_activated"
    
  non_retriable_errors:
    - "card_lost_stolen"
    - "fraud_decline"
    - "invalid_card"
    - "account_closed"
    
  account_updater:
    enabled: true
    check_before_retry: true
    
  customer_notifications:
    - attempt: 1, notify: "payment_failed"
    - attempt: 2, notify: "retry_scheduled"
    - attempt: 4, notify: "final_attempt"
    - failed: true, notify: "subscription_cancelled"
```

### High-Value Transaction Retry Policy

```yaml
retry_policy:
  name: "high_value_transaction"
  applicability:
    min_amount: 500.00
    currency: "USD"
    
  max_attempts: 5
  backoff_strategy: "exponential_with_jitter"
  base_delay_seconds: 5
  max_delay_seconds: 60
  
  retriable_errors:
    - "issuer_timeout"
    - "network_error"
    - "issuer_unavailable"
    
  special_handling:
    - manual_review_on_failure: true
    - fraud_team_notification: true
    - customer_communication: "immediate"
    
  circuit_breaker:
    enabled: true
    failure_threshold: 0.3
    recovery_interval_seconds: 120
```

This runbook should be reviewed and updated:
- Monthly: Retry effectiveness metrics review
- Quarterly: Retry policy optimization based on data
- After incidents: Document learnings and update policies
- With network rule changes: Update compliance section
- When new payment methods added: Extend policies appropriately