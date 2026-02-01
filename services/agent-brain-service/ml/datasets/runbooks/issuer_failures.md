# Issuer Failures

1. Overview
- Scope: failures where the issuing bank (card issuer) is the proximate cause of payment decline, timeout, or anomalous behavior.
- Purpose: give on-call engineers clear signals, short-term safe mitigations, escalation triggers, and compliance constraints.
- Assumption: gateway and acquirer components are functioning unless signals indicate otherwise.

2. Common failure patterns
- Sudden spike in `issuer_declined` responses for one BIN/issuer.
- Gradual degradation in authorization success over hours (regional outage).
- Increased p95/p99 authorization latency with stable request volume.
- Time-windowed failures correlated to business hours or batch jobs at issuer.
- Repeated identical ISO8583/HTTP error codes across different merchants.
- Sporadic failures only for high-value transactions or specific card products.
- Region- or BIN-scoped failures (all cards from a country or bank).
- Retry storms amplifying declines due to immediate automatic retries.
- Partial success: some acquirers succeed, others fail for same card.

3. Observable signals (metrics/logs)
- Authorization success rate by issuer/BIN (per minute, 5m, 1h windows).
- p50/p95/p99 authorization latency by issuer/BIN.
- Rate of specific decline codes (e.g., issuer_declined, pick_up_card, insufficient_funds).
- Network-level errors to issuer IP ranges (TCP reset, connection timeout).
- Increase in socket reuse errors or TLS handshake failures for issuer endpoints.
- Consistent ISO8583 response codes repeated across requests (same stan, same response code).
- Traffic volume stable but success rate falling; no upstream gateway errors.
- Retry_count and retry latency distribution per payment attempt.
- Correlation of failures to routing decisions (acquirer A vs B).
- Spike in chargeback or dispute-related flags shortly after decline bursts.
- Pager/alert for per-issuer error-rate threshold breach.

4. Probable root causes
- Issuer-side outage or degraded capacity.
- Issuer-side rate-limiting or sudden throttling (per-merchant or global).
- New issuer fraud/scoring rule causing soft or hard declines.
- Network routing issues between acquirer and issuer (BGP, ISP problems).
- TLS certificate issues, cipher mismatch, or protocol upgrades at issuer endpoint.
- BIN reassignments, issuer mergers, or product changes not reflected in routing.
- Misconfigured routing rules on gateway (wrong acquirer, expired credentials).
- Issuer maintenance windows or delayed batch processing impacting auth flow.
- Settlement or reconciliation holds at issuer causing rejects for certain transaction types.
- Card product deactivation (lost/stolen, blocked by issuer).
- Rate-limiting cascades due to automated retries from multiple gateways.

5. Safe mitigation actions
- Reduce or pause retries for affected BIN/issuer immediately (prevent retry-storm).
- Increase client-visible backoff with exponential backoff + jitter for this issuer.
- Route affected traffic to alternate acquirer(s) if validated and credentialed.
- Apply per-issuer circuit breaker: fail-fast with helpful decline reason to merchant.
- Throttle merchant/requestor traffic toward the issuer (rate-limit by merchant or BIN).
- Temporarily disable non-essential risk checks that produce synchronous issuer calls (only if safe and approved per policy).
- Enable granular routing to fallback processors that historically succeed for the BIN.
- Add temporary user-facing messaging that reflects issuer decline (do not speculate on cause).
- Collect and tag representative failed request payloads for issuer ops and postmortem.
- Open an operations ticket with issuer (include timestamps, sample requests, response codes).
- Preserve full request/response and network traces for the affected window.
- If duplicate-charge risk exists, enforce idempotency checks before retrying.

6. Actions requiring human approval
- Full suppression (permanent routing removal) of an issuer.
- Making merchant-visible long-term routing/rule changes (>24–48 hours).
- Disabling SCA/3DS or other mandated controls to work around declines.
- Any change that can cause financial exposure (manual re-routing of settlement or reversal behavior).
- Public or merchant-facing notices and SLA-impacting communications.
- Opening regulator-facing incident reports that reference issuer behavior.
- Authorizing charge reversals or refunds outside standard automated flows.

7. What NOT to do
- Do not aggressively increase retry volume or reduce backoff to force success.
- Do not suppress logs or reduce audit fidelity to “hide” incident details.
- Do not change idempotency semantics to skirt duplicate-detection safeguards.
- Do not change compliance-enforced controls (e.g., 3DS rules) without legal approval.
- Do not mark issuer as "ok" based on a single successful test request; require statistically significant recovery.

8. Regulatory / compliance notes
- Preserve immutable logs for all mitigation actions (who, what, why, timestamps).
- Do not alter or redact cardholder data beyond PCI-DSS permitted truncation/handling.
- Merchant communication templates may be subject to contract/SLA clauses — consult legal.
- Certain actions (fund holds, reversals, settlement changes) may require reporting under local regulator rules (e.g., RBI, PSD2) — escalate to compliance.
- Any suppression or permanent blocking that affects consumer access to funds must be reviewed for dispute and consumer-protection impact.


# Issuer Failures

## Overview
Issuer failures originate from card-issuing banks or issuer processors.
They are external to the payment gateway and often correlated by issuer,
region, card BIN, or time window.

## Common Failure Patterns
- Sudden spike in issuer_declined or do_not_honor responses
- Authorization latency increase isolated to specific issuers
- Time-bound failures during issuer maintenance windows
- Partial approvals followed by reversals
- Retry amplification causing secondary degradation
- Asymmetric impact (e.g., debit affected, credit unaffected)

## Observable Signals (Metrics / Logs)
- Authorization success rate dropping for a single BIN or issuer ID
- p95/p99 latency increase without gateway CPU or queue pressure
- Stable inbound request rate with rising issuer error codes
- Repeated ISO response codes (05, 91, 96)
- No corresponding acquirer or gateway transport errors
- Increased reversal or timeout events

## Probable Root Causes
- Issuer core banking outage
- Issuer fraud or risk rule changes
- Issuer-side rate limiting or throttling
- Network routing issues between acquirer and issuer
- Planned or unplanned issuer maintenance
- Regional telecom or network disruptions

## Safe Mitigation Actions
- Reduce retry attempts for affected issuers
- Increase backoff intervals to avoid retry storms
- Temporarily deprioritize affected issuer traffic
- Surface alternate payment methods to merchants
- Delay retries outside peak issuer load windows
- Preserve original authorization context for reversals

## Actions Requiring Human Approval
- Full suppression of an issuer or BIN range
- Long-term routing or acquirer changes
- Merchant-facing incident communication
- Manual settlement or reconciliation adjustments

## What NOT to Do
- Do not increase retries to recover issuer declines
- Do not assume issuer failures are gateway bugs
- Do not suppress issuers without correlation evidence
- Do not drop audit logs or authorization traces

## Regulatory / Compliance Notes
- Issuer behavior is outside gateway operational control
- Authorization and reversal logs must be immutable
- All mitigation actions must be auditable and reversible


# Issuer Failure Patterns

## Overview

Issuer-related payment failures represent external dependencies in the payment processing chain. These failures originate from issuing banks or card networks and manifest as authorization declines, timeout errors, or degraded response times. Unlike gateway-side failures, issuer problems require different diagnostic approaches and mitigation strategies due to limited direct control over the failing system.

Key characteristics of issuer failures:
- External to payment gateway infrastructure
- Often region-specific or time-dependent
- May affect specific card types, bins, or customer segments
- Typically correlate with issuer maintenance windows, network upgrades, or capacity constraints
- Can propagate through retry mechanisms if not properly managed

## Common Failure Patterns

### Authorization Latency Degradation
- P50 latency increases from baseline 200-300ms to 2-5 seconds
- P95 latency exceeds 10 seconds for specific issuer ranges
- P99 latency hits timeout thresholds (typically 30-45 seconds)
- Gradual degradation over 5-15 minute windows
- Sudden spikes during peak transaction hours (lunch time, evening shopping)
- Weekend vs weekday patterns indicating capacity planning issues
- Geographic clustering of slow responses

### Issuer Decline Spikes
- Authorization decline rate increases from baseline 5-8% to 20-40%
- Specific decline codes dominate (insufficient_funds, do_not_honor, card_declined)
- Decline patterns cluster by BIN range or issuer identifier
- Temporal patterns: start of month (rent/bills), paydays, holiday shopping
- Correlation with specific merchant categories or transaction amounts
- Sudden shifts in decline reasons without corresponding fraud pattern changes

### Time-Bound Degradation
- Regular degradation during specific hours (09:00-10:00 local issuer time)
- Weekend maintenance windows causing elevated failures
- Month-end processing causing capacity constraints
- Holiday-related traffic spikes overwhelming issuer systems
- Timezone-specific patterns for international issuers
- Predictable daily peaks during lunch hours (11:30-13:30) and evening shopping (18:00-21:00)

### Retry Storm Amplification
- Initial issuer slowdown triggers aggressive retry policies
- Retry volume compounds latency issues
- Issuer rate limiting triggers additional failures
- Exponential backoff not properly implemented
- Duplicate transaction attempts create accounting reconciliation issues
- Gateway-side queuing exacerbates the problem
- Circuit breakers fail to trip at appropriate thresholds

### Selective BIN Range Failures
- Specific 6-8 digit BIN ranges show elevated failure rates
- New card programs experiencing teething problems
- Legacy card systems with outdated integration protocols
- Regional issuer infrastructure disparities
- Prepaid vs credit card processing differences
- Co-branded card programs with split processing responsibilities

### Network Routing Failures
- Specific network paths (Visa vs Mastercard) experiencing issues
- Regional network node failures affecting transaction routing
- Cross-border transaction routing degradation
- Network upgrade-related compatibility issues
- Fallback routing not properly configured
- Primary-secondary route failover delays

### Fraud Detection System Overreach
- Issuer fraud systems becoming overly aggressive
- Machine learning model updates causing false positive spikes
- Geographic mismatch triggers (VPN usage, international cards)
- Velocity check failures (multiple cards from same IP)
- Device fingerprinting mismatches
- 3DS authentication challenges increasing substantially

### Capacity Threshold Breaches
- Issuer transaction processing capacity exceeded
- Queue depth growing faster than processing rate
- Connection pool exhaustion on issuer side
- Database read replica lag affecting authorization checks
- Mainframe batch processing windows blocking real-time transactions
- Resource contention during backup operations

## Observable Signals

### Metrics and Monitoring

#### Latency Metrics
- `issuer.authorization.latency.p50` increasing beyond 500ms baseline
- `issuer.authorization.latency.p95` exceeding 5 seconds
- `issuer.authorization.latency.p99` hitting 30+ second timeout thresholds
- `issuer.response_time_variance` showing high standard deviation (>2 seconds)
- `issuer.timeout_rate` climbing above 1% of total requests
- `connection.time_to_first_byte` degrading for specific issuer endpoints
- `ssl_handshake_duration` increasing indicating network layer issues

#### Success Rate Metrics
- `issuer.authorization.success_rate` dropping below 80% threshold
- `issuer.decline_rate` spiking above 15% from 5-8% baseline
- `issuer.hard_decline_ratio` increasing (permanent vs temporary declines)
- `issuer.retry_success_rate` showing diminishing returns (<10% success on retry)
- `transaction.completion_rate` falling despite stable request volume
- `issuer.connection_success_rate` degrading below 98%

#### Error Code Distributions
- Decline code `05` (do_not_honor) increasing to >30% of declines
- Decline code `51` (insufficient_funds) showing unusual spikes
- Decline code `14` (invalid_card_number) for valid cards
- Error code `timeout` becoming dominant error type
- Network error codes (connection_refused, connection_reset) clustering
- HTTP 503 or 504 responses from issuer endpoints
- Specific issuer error codes appearing that weren't previously seen

#### Volume and Traffic Patterns
- Stable or increasing `request.volume` with falling success rates
- Divergence between `requests_sent` and `responses_received` metrics
- Retry volume growing faster than initial request volume
- Queue depth metrics showing accumulation on issuer-bound queues
- Connection pool utilization spiking to 100%
- Issuer-specific traffic shaping triggering more frequently

#### Regional and Temporal Signals
- Failure patterns clustering by issuer geographic region
- Time-of-day correlation with issuer local business hours
- Weekend vs weekday pattern changes
- Holiday period anomalies
- Batch processing window correlations (typically 23:00-02:00 local time)
- Cross-border transaction failure rate divergence

### Logging and Tracing

#### Error Log Patterns
```
WARN: Issuer authorization timeout for BIN 424242** after 32s
ERROR: Issuer connection pool exhausted for issuer_id=CHASE_US
INFO: Increased retry attempts for issuer BARCLAYS_UK (avg: 2.4 retries/txn)
WARN: Decline code distribution anomaly: do_not_honor 45% (expected 15%)
ERROR: Circuit breaker HALF_OPEN -> OPEN for issuer HDFC_IN
```

#### Distributed Tracing Indicators
- Trace spans showing issuer call duration >10x baseline
- Missing trace segments indicating dropped connections
- Retry spans multiplying within single transaction trace
- Timeout spans correlating with specific issuer endpoints
- Circuit breaker state transitions in trace metadata

#### Database and State Indicators
- Issuer health check failures in monitoring database
- Historical pattern analysis showing similar past incidents
- Issuer configuration changes logged in audit trail
- Merchant complaint tickets clustering for specific issuer
- Customer support case volume spiking for payment failures

### Alerting Triggers
- PagerDuty alert: "Issuer CHASE_US authorization success rate below 75%"
- Threshold breach: "HDFC_IN p95 latency >8s for 10 consecutive minutes"
- Anomaly detection: "Unusual decline code distribution for BARCLAYS_UK"
- Correlation alert: "3+ issuers in UK region showing degraded performance"
- SLA alert: "Payment completion SLA at risk due to issuer latency"

## Probable Root Causes

### Issuer Infrastructure Issues

#### Capacity and Performance
- Transaction processing system capacity exceeded during peak hours
- Database connection pool exhaustion on issuer authorization servers
- Mainframe CPU saturation (common with legacy banking systems)
- Memory pressure causing garbage collection pauses
- Network bandwidth saturation at issuer data center
- Load balancer misconfiguration causing uneven distribution
- Insufficient scaling for seasonal traffic (holidays, sales events)
- Batch processing jobs interfering with real-time transaction processing

#### System Outages and Degradation
- Planned maintenance windows not properly communicated
- Unplanned outages due to hardware failures
- Software deployment causing instability
- Database replica lag affecting authorization decisions
- Cache invalidation issues causing elevated database load
- Network equipment failure affecting connectivity
- Power or cooling failures at issuer facilities
- Disaster recovery failover not functioning correctly

#### Configuration and Software Issues
- Misconfigured timeout values causing premature connection drops
- Incorrect routing rules sending traffic to wrong endpoints
- Software bugs introduced in recent releases
- Security certificate expiration causing SSL handshake failures
- API version compatibility issues after gateway upgrades
- Incorrect credential rotation causing authentication failures
- Feature flag changes causing unexpected behavior

### Network and Connectivity Problems

#### Network Layer Failures
- BGP routing changes affecting path to issuer endpoints
- DDoS attacks targeting issuer infrastructure
- ISP-level outages or degradation
- Cross-border network congestion
- DNS resolution failures or propagation delays
- TCP connection exhaustion at network edge
- MTU mismatch causing packet fragmentation
- Firewall rule changes blocking legitimate traffic

#### Card Network Issues
- Visa network processing delays
- Mastercard regional node failures
- Network-level rate limiting or throttling
- Protocol version mismatches
- Message format validation failures
- Network token provisioning service degradation
- Stand-in processing fallback activation

### Issuer Business Logic Changes

#### Fraud and Risk Management
- Fraud detection model updates causing false positive spike
- Risk score threshold adjustments
- Geographic blocking rules expanded
- Velocity checking parameters tightened
- Device fingerprinting requirements changed
- 3D Secure mandatory enforcement introduced
- Merchant category code (MCC) blocking rules added
- Transaction amount limits reduced

#### Regulatory and Compliance
- Compliance-driven rule changes affecting authorization logic
- Regional regulation updates requiring new validation
- Strong Customer Authentication (SCA) enforcement
- Know Your Customer (KYC) verification requirements
- Anti-Money Laundering (AML) screening enhanced
- Card-not-present transaction restrictions
- Cross-border transaction additional scrutiny

#### Operational Changes
- Issuer processing center migration
- System upgrade or modernization project
- Vendor or processor changes
- Authorization scoring algorithm updates
- Credit limit policy changes
- Account status verification logic modified
- Merchant risk profile reclassification

### External Factors

#### Traffic and Load Patterns
- Coordinated merchant promotion driving unexpected volume
- Viral social media campaign causing traffic spike
- Flash sale events overwhelming processing capacity
- Credential stuffing or account testing attacks
- Retry storms from multiple gateways
- Bot traffic attempting fraudulent transactions
- Seasonal shopping patterns (Black Friday, Christmas)

#### Geographic and Temporal Factors
- Regional internet outages affecting customer connectivity
- Natural disasters impacting infrastructure
- Political events causing transaction pattern changes
- Currency fluctuation impacts on cross-border transactions
- Time zone specific processing constraints
- Local holiday periods affecting issuer operations

## Safe Mitigation Actions

### Immediate Response (0-15 minutes)

#### Traffic Management
- **Reduce retry attempts**: Lower retry count from 3 to 1 for affected issuer
  - Configuration: `issuer.{issuer_id}.max_retries = 1`
  - Expected impact: 60-70% reduction in total issuer traffic
  - Rollback if: Success rate improves >5% within 5 minutes
  
- **Implement exponential backoff**: Increase delay between retries
  - Initial delay: 2 seconds (from 500ms)
  - Maximum delay: 30 seconds
  - Backoff multiplier: 2.0
  - Expected impact: Spreading retry load, reducing burst traffic
  
- **Enable circuit breaker**: Activate for severely degraded issuers
  - Failure threshold: 50% of requests failing
  - Timeout threshold: P95 latency >10 seconds
  - Recovery attempt interval: 60 seconds
  - Half-open state: Allow 10% of traffic through for testing

#### Request Routing
- **Reroute to alternate payment methods**: Present backup options to users
  - Wallet options: Apple Pay, Google Pay (if issuer-independent)
  - Alternative networks: If card supports multiple rails
  - Bank transfer options: For high-value transactions
  - Buy-now-pay-later: For eligible merchants
  - Expected impact: 20-40% of customers complete with alternate method
  
- **Load shift to healthy issuers**: For multi-card customers
  - Check customer wallet for cards from healthy issuers
  - Prompt card re-selection with explanation
  - Implement only for customers with 2+ saved cards
  - Track fallback success rate

#### Monitoring and Alerting
- **Increase monitoring granularity**: From 5-minute to 1-minute intervals
  - Enables faster detection of improvement or degradation
  - Adjust alert thresholds to prevent alert fatigue
  - Add issuer-specific dashboards to incident war room
  
- **Enable detailed logging**: Capture full request/response for debugging
  - Sample rate: 5% of traffic (avoid log volume explosion)
  - Include: request timestamp, BIN, amount, response code, latency
  - Retention: 72 hours for incident analysis
  - Privacy: Ensure PCI compliance in logging

### Short-term Stabilization (15-60 minutes)

#### Capacity Adjustment
- **Scale gateway infrastructure**: Increase headroom for retries and queuing
  - Add 20-30% more API gateway instances
  - Expand connection pool sizes for affected issuer
  - Increase queue depths to buffer traffic spikes
  - Monitor CPU, memory, network for bottlenecks
  
- **Adjust timeout values**: Balance between user experience and resource usage
  - Increase from 30s to 45s if issuer is slow but responding
  - Decrease from 30s to 15s if issuer is unresponsive
  - Implement progressive timeouts based on retry attempt
  
- **Traffic shaping**: Control rate of requests to affected issuer
  - Implement token bucket algorithm with rate limit
  - Start at 80% of recent healthy throughput
  - Gradually increase by 10% every 10 minutes if stable
  - Monitor for re-triggering of issues

#### Communication and Coordination
- **Internal stakeholder notification**: Alert relevant teams
  - Merchant operations: For incoming merchant queries
  - Customer support: Provide guidance on expected failures
  - Product management: For user experience impact assessment
  - Finance: For revenue impact estimation
  - Engineering leadership: For escalation awareness
  
- **Merchant communication**: Proactive notification for high-volume merchants
  - Use pre-approved templates for rapid response
  - Include: affected issuer, expected duration, alternate payment methods
  - Delivery: Email, merchant dashboard notification, API webhook
  - Only for merchants processing >1000 TPH with affected issuer

#### Data Collection
- **Enhanced diagnostics**: Gather data for root cause analysis
  - Capture network traces for sample transactions
  - Enable issuer-side logging if available through partnership
  - Correlate with issuer-provided status pages or APIs
  - Document timeline of events and actions taken
  - Track before/after metrics for each mitigation step

### Medium-term Optimization (1-24 hours)

#### Strategy Refinement
- **Analyze failure patterns**: Use collected data for optimization
  - Identify BIN ranges most affected
  - Determine optimal retry strategy per issuer
  - Assess which payment methods work best as alternatives
  - Calculate cost-benefit of various mitigation approaches
  
- **A/B testing of strategies**: Validate mitigation effectiveness
  - Test different retry counts (0, 1, 2, 3)
  - Compare exponential vs linear backoff
  - Evaluate circuit breaker threshold tuning
  - Measure alternate payment method conversion rates
  - Sample size: 5-10% of traffic for each variant

#### Preventive Measures
- **Update issuer health scoring**: Adjust routing based on reliability
  - Implement composite health score: latency + success_rate + error_rate
  - Weight recent performance more heavily (exponential decay)
  - Use health score to influence card ranking in wallet
  - Dynamically adjust retry policies based on health score
  
- **Implement smart retry logic**: Context-aware retry decisions
  - Decline code analysis: Don't retry hard declines (invalid card, fraud)
  - Temporal awareness: Skip retry during known maintenance windows
  - User context: Higher retry tolerance for high-value transactions
  - Success probability estimation before retry attempt

#### Coordination with External Parties
- **Issuer communication**: If established relationship exists
  - Reach out through technical account manager
  - Share anonymized failure data and patterns
  - Request status updates or maintenance schedules
  - Coordinate on resolution testing
  
- **Network liaison**: For network-level issues
  - Contact Visa/Mastercard technical support
  - Report observed network latency or error patterns
  - Request routing optimization if applicable
  - Coordinate on network token issues

## Actions Requiring Human Approval

### High-Impact Operational Changes

#### Traffic Management Decisions
- **Full issuer suppression**: Blocking all transactions for an issuer
  - **Risk**: Revenue loss from legitimate customer transactions
  - **Impact**: Potentially 5-20% of total transaction volume
  - **Approval required from**: VP Engineering, Head of Payments Operations
  - **Documentation needed**: Incident severity justification, revenue impact analysis
  - **Reversal plan**: Gradual re-enablement strategy with monitoring
  - **Communication plan**: Merchant and customer notification templates
  
- **Long-term routing changes**: Permanent shifts in issuer preference
  - **Risk**: Unintended consequences on success rates, costs
  - **Impact**: Affects all future transactions for customer segment
  - **Approval required from**: Head of Payments, Product Management
  - **Testing required**: A/B test on 5-10% of traffic for 48 hours minimum
  - **Monitoring period**: 7 days of close observation post-rollout
  
- **Merchant-specific overrides**: Custom routing for specific merchants
  - **Risk**: Operational complexity, maintenance burden
  - **Approval required from**: Account Manager, Engineering Manager
  - **Contract review**: Ensure compliance with merchant agreement
  - **Documentation**: Clear override reason and expected duration

#### Financial and Business Decisions
- **SLA compensation triggers**: Issuing credits or refunds to merchants
  - **Approval required from**: Finance Director, Legal (if contractual)
  - **Documentation**: Detailed outage timeline, affected transaction count
  - **Calculation**: Pro-rata SLA credit based on downtime percentage
  - **Communication**: Merchant-facing explanation and credit notification
  
- **Rate adjustment authorization**: Changing fees for specific routing
  - **Approval required from**: Pricing Committee, Finance
  - **Analysis required**: Cost-benefit analysis, competitive positioning
  - **Contract implications**: Review merchant agreements for change clauses
  
- **Budget override**: Emergency infrastructure spend for scaling
  - **Approval required from**: Engineering Director, CFO (for large amounts)
  - **Justification**: Expected revenue protection, customer impact
  - **Alternatives analysis**: Why existing capacity insufficient

### Communication and Public Relations

#### External Communication
- **Public status page updates**: Posting about ongoing issues
  - **Approval required from**: Communications Director, Legal review
  - **Content guidelines**: Factual, no speculation on causes
  - **Timing**: Must notify before merchant/customer discovery
  - **Template**: Pre-approved incident communication templates
  
- **Direct merchant communication**: Proactive outreach about failures
  - **Approval required from**: Merchant Operations Manager
  - **Criteria**: Affects >100 merchants or >$500K TPV
  - **Content**: Expected issue duration, mitigation in place, alternatives
  - **Channel**: Email for low urgency, phone for critical accounts
  
- **Regulatory notification**: If required by jurisdiction
  - **Approval required from**: Legal, Compliance Officer
  - **Trigger**: Incident affects customer funds or data security
  - **Timeline**: Follow regulatory reporting timelines (often 24-72 hours)
  - **Format**: Use regulator-specified incident report format

#### Data Sharing
- **Sharing failure data with issuers**: Sending diagnostic information
  - **Approval required from**: Data Privacy Officer, Legal
  - **Data sanitization**: Remove merchant and cardholder identifying information
  - **Purpose**: Collaborative troubleshooting only
  - **NDA verification**: Ensure data sharing agreement in place
  
- **Third-party diagnostic access**: Granting vendor access to logs
  - **Approval required from**: Security Officer, Engineering Manager
  - **Access scope**: Minimum necessary data for troubleshooting
  - **Duration**: Time-limited access credentials
  - **Monitoring**: Audit all access during diagnostic period

### Configuration and System Changes

#### Policy Modifications
- **Global retry policy changes**: Altering default retry behavior
  - **Approval required from**: Principal Engineer, Engineering Director
  - **Impact assessment**: Projected effect on success rate, latency, costs
  - **Rollout strategy**: Gradual deployment with kill switch
  - **Testing**: Load testing in staging environment first
  
- **Circuit breaker threshold updates**: Changing failure detection sensitivity
  - **Approval required from**: Site Reliability Engineering Lead
  - **Rationale**: Document why current thresholds insufficient
  - **Simulation**: Model expected behavior under various scenarios
  - **Monitoring**: Enhanced monitoring during change period
  
- **Authorization flow changes**: Modifying transaction processing logic
  - **Approval required from**: Payments Architecture Team, QA Lead
  - **Risk**: Payment processing errors, compliance violations
  - **Testing**: Comprehensive regression testing suite
  - **Rollback**: One-click rollback capability required

## What NOT to Do

### Retry and Traffic Management Mistakes

**Do NOT increase retry volume aggressively**
- **Risk**: Exacerbating issuer degradation, turning partial outage into complete failure
- **Why**: Retry storms compound the problem by adding more load to already struggling system
- **Example failure**: 2019 incident where aggressive retries amplified 2x slowdown into complete outage
- **Instead**: Reduce retries and implement exponential backoff

**Do NOT retry identical requests rapidly**
- **Risk**: Creating duplicate transactions, triggering fraud detection
- **Why**: Rapid identical requests appear as replay attack or credential stuffing
- **Time minimum**: Wait at least 2 seconds between retry attempts
- **Request variation**: Add idempotency key to distinguish legitimate retries

**Do NOT retry hard decline codes**
- **Risk**: Wasted resources, customer frustration, issuer penalties
- **Hard decline codes**: 04 (pick up card), 07 (fraud), 14 (invalid card), 41 (lost card), 43 (stolen card)
- **Why**: These indicate card should not be retried without customer intervention
- **Instead**: Prompt user to check card details or use different payment method

**Do NOT implement infinite retry loops**
- **Risk**: Resource exhaustion, cost explosion, violating rate limits
- **Maximum**: 3 retry attempts is industry standard
- **Timeout**: Implement total transaction timeout (e.g., 60 seconds)
- **Circuit breaker**: Fail fast after pattern of failures detected

### Suppression and Blocking Mistakes

**Do NOT suppress issuer without confirmation**
- **Risk**: Blocking legitimate transactions, revenue loss, customer dissatisfaction
- **Required**: Multiple confirmation signals before suppression
- **Signals needed**: High failure rate (>50%), extended duration (>30 min), issuer status page confirmation
- **Instead**: Implement degraded mode with reduced traffic, not complete block

**Do NOT block based on single signal**
- **Risk**: False positive suppression during transient issues
- **Required signals**: Failure rate AND latency AND error code pattern
- **Time window**: Observe pattern for at least 10 minutes
- **Confirmation**: Cross-check with multiple monitoring systems

**Do NOT suppress without rollback plan**
- **Risk**: Unable to recover quickly when issuer recovers
- **Required**: Automated re-enablement testing every 5-10 minutes
- **Health check**: Synthetic transactions to test issuer recovery
- **Gradual**: Re-enable traffic at 10%, 25%, 50%, 100% increments

### Communication Mistakes

**Do NOT communicate speculation as fact**
- **Risk**: Misinformation, damaged issuer relationship, regulatory issues
- **Stick to**: Observed symptoms and impacts only
- **Avoid**: "The issuer's database is down" (unless confirmed)
- **Use**: "We're observing elevated failure rates from this issuer"

**Do NOT alert merchants prematurely**
- **Risk**: Alert fatigue, loss of credibility, unnecessary merchant concern
- **Threshold**: Only alert when >100 merchants affected or >30 minute duration expected
- **Content**: Include specific actions merchants can take
- **Updates**: Provide regular updates every 30-60 minutes if ongoing

**Do NOT share customer or transaction details externally**
- **Risk**: PCI compliance violation, privacy breach, regulatory penalty
- **Sanitization**: Remove all cardholder data before sharing any information
- **Aggregation**: Share only aggregate statistics, never individual transactions
- **Approval**: Require legal and compliance approval for any external data sharing

### Monitoring and Diagnostic Mistakes

**Do NOT ignore correlated signals**
- **Risk**: Missing root cause, implementing ineffective mitigation
- **Look for**: Multiple issuers in same region failing simultaneously
- **Consider**: Network-level or card network issues, not individual issuer
- **Action**: Escalate to network operations team

**Do NOT disable monitoring during incidents**
- **Risk**: Losing visibility when you need it most
- **High load concern**: Scale monitoring infrastructure instead
- **Reduce**: Unnecessary metrics, but keep failure signals
- **Sampling**: Use intelligent sampling to reduce volume while maintaining signal

**Do NOT modify production during active incident**
- **Risk**: Compounding problems with untested changes
- **Exception**: Well-tested, pre-approved mitigation playbooks only
- **Testing**: Emergency changes should be tested in staging when possible
- **Rollback**: Ensure immediate rollback capability before any change

### Business Logic Mistakes

**Do NOT alter transaction amounts**
- **Risk**: Accounting discrepancies, compliance violations, fraud
- **Never**: Round, adjust, or modify transaction amounts
- **Decline**: Rather than modify, decline with clear error message

**Do NOT store full card details during failures**
- **Risk**: PCI compliance violation, data breach risk
- **Storage**: Only store last 4 digits and BIN for diagnostics
- **Retention**: Delete diagnostic data after 90 days maximum
- **Encryption**: All stored data must be encrypted at rest

**Do NOT bypass fraud checks to improve success rate**
- **Risk**: Enabling fraudulent transactions, regulatory violations
- **Maintain**: All fraud and risk checks even during degraded operations
- **Accept**: Lower success rate is preferable to increased fraud loss
- **Escalate**: If fraud checks causing false positives, escalate to risk team

## Regulatory and Compliance Notes

### Audit and Logging Requirements

**Immutable audit trail required**
- All issuer suppression or routing changes must be logged with:
  - Timestamp (UTC) of change implementation
  - Engineer or system making the change
  - Justification and incident reference
  - Expected duration and rollback criteria
  - Approval chain documentation
- Retention period: Minimum 7 years for financial audit compliance
- Storage: Write-once storage or blockchain for immutability
- Access: Audit trail must be accessible to compliance and regulatory auditors

**Decision reasoning documentation**
- Every automated decision must be explainable:
  - Input signals that triggered the decision
  - Algorithm or rule set applied
  - Thresholds and parameters used
  - Expected outcome vs actual outcome
- Human override: Document reason for manual intervention
- Model decisions: If using ML, log model version, features, and confidence score

### Regional Compliance Considerations

**European Union (PSD2/SCA)**
- Strong Customer Authentication cannot be bypassed during issuer issues
- Transaction monitoring reports must include issuer failure patterns
- Account information service disruptions must be reported to regulators within 24 hours
- Customer refund rights apply even if failure is issuer-originated

**United States (FCRA/EFTA)**
- Electronic Fund Transfer Act requires provisional credit for failed transactions
- Fair Credit Reporting Act implications if failures affect credit reporting
- State-specific requirements for transaction failure notification
- Error resolution timeline requirements (10 business days for investigation)

**India (RBI Guidelines)**
- Reserve Bank of India mandates transaction success rate monitoring
- Customer not to be charged for failed transactions
- Refund timeline: T+5 days for failed transactions
- Technical declines to be reported separately from fraud declines

**Global PCI-DSS**
- Card data must not be logged in diagnostic data
- Failure analysis must comply with data retention policies
- Incident must not expose cardholder data environment
- Third-party access for diagnostics requires PCI compliance validation

### Settlement and Funds Movement

**No autonomous action impacting settlement**
- Automated systems cannot:
  - Initiate refunds or credits without explicit transaction failure
  - Modify settlement amounts or timing
  - Cancel settled transactions
  - Adjust merchant payout amounts
- Human approval required for any settlement-related action
- Financial operations team must validate all fund movements

**Chargeback and dispute implications**
- Failed authorization attempts may trigger customer disputes
- Documentation required: Full authorization attempt history
- Issuer response codes must be preserved for dispute resolution
- Timeline: Disputes may arrive 60-120 days after incident

### Data Protection and Privacy

**GDPR compliance for EU customers**
- Customer right to explanation for payment decline
- Data minimization: Only collect necessary diagnostic data
- Data processing agreements with issuers must be in place
- Breach notification if incident exposes customer data (72 hours)

**CCPA compliance for California customers**
- California residents have right to know what data collected during failures
- Diagnostic data sharing with issuers must be disclosed
- Opt-out rights apply to sharing failure data with partners

### Incident Reporting Obligations

**Internal reporting**
- Risk committee notification for incidents >1 hour duration
- Board reporting for incidents affecting >5% of transaction volume
- Quarterly trend analysis for issuer reliability reporting

**External reporting**
- Card networks: Report systematic issuer issues within 24 hours
- Regulatory bodies: Report customer fund exposure within required timeframes
- Merchant contractual reporting: As per service level agreements
- Public disclosure: As required by jurisdiction for customer-affecting incidents

### Compliance During Mitigation

**Maintain compliance while mitigating**
- Fraud detection rules must remain active
- KYC/AML screening cannot be bypassed
- Transaction limits must be enforced
- Customer notification requirements must be met
- Dispute rights must be preserved

**Documentation for compliance**
- Incident postmortem must include compliance review
- Mitigation actions must be mapped to compliance framework
- Any compliance exceptions must be documented and time-limited
- Audit-ready documentation package within 48 hours of incident resolution

This comprehensive runbook should be reviewed quarterly and updated based on:
- New issuer failure patterns observed
- Regulatory requirement changes
- Technology stack evolution
- Postmortem insights from incidents
- Industry best practice developments