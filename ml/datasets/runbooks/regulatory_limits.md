# Regulatory Limits

1. Overview
- Scope: incidents and failures driven by regulatory, card-network, or jurisdictional transaction limits, velocity rules, and mandated controls.
- Purpose: give on-call engineers clear detection signals, safe short-term mitigations, and a checklist for required approvals and compliance notifications.

2. Common failure patterns
- Transaction-level declines citing "exceeds limit", "not permitted", or network-specific decline codes.
- Repeated declines for transactions above a threshold amount or velocity (per card/merchant/account).
- Failure spikes in specific geographies after regulatory announcements.
- SCA/3DS challenges failing en masse for specific merchant categories.
- Time-windowed enforcement (daily, monthly caps) causing late-day failures.
- sudden rise in "blocked-by-regulation" codes following policy change.
- Merchant onboarding rejections due to missing local compliance artifacts.

3. Observable signals (metrics/logs)
- Decline counts and types by regulatory code and merchant category.
- Volume of transactions failing with network-specific codes (e.g., PSD2 XS2A codes; RBI-specific messages).
- Velocity metrics: transactions per card/account/merchant per time window (1h, 24h, 30d).
- High failure rate for transactions with specific MCCs or BIN ranges.
- Alerts for SCA/3DS challenge failures, churning authentication statuses.
- Alerts for mismatches in geolocation vs card issuing country.
- Audit logs showing attempted overrides or policy bypass events.
- Increase in customer support tickets citing regulatory decline language.

4. Probable root causes
- New or changed regulator rule (limits, mandatory SCA, geo-blocking).
- Card network or issuer enforcing transaction caps or velocity rules.
- Merchant misclassification (wrong MCC) triggering regulatory blocks.
- Missing or invalid merchant documentation for KYC/AML purpose.
- Misconfigured or outdated business rules encoding regulatory thresholds.
- Time-zone or calendar misalignment (cutoff times, settlement-day rules).
- Payment instrument type (prepaid, PPI) hitting instrument-specific limits.
- Cross-border routing that violates local controls or data residency rules.

5. Safe mitigation actions
- Surface precise decline reason to merchant and customer; avoid speculative messaging.
- Temporarily route to compliant processors only (those with local permissions).
- If merchant is misclassified: tag and route to onboarding flows rather than bypassing regulation.
- For velocity-based incidents: implement soft-throttling with clear merchant feedback.
- Offer split-pay or lower-amount alternative workflows (only where allowed by regulation).
- Log and preserve all decision paths and regulatory checks applied to each transaction.
- If SCA failures spike, reduce non-essential calls that block authentication flows; prioritize auth path stability.
- Open a compliance ticket with exact failure samples and timestamps; include merchant and cardholder identifiers as allowed.
- Provide merchants with guidance to collect additional customer authentication details rather than bypass controls.

6. Actions requiring human approval
- Any action that weakens or disables a regulation-mandated control (e.g., disabling SCA).
- Temporary waivers allowing transactions that exceed statutory caps.
- Reclassifying merchant category codes (MCCs) in production routing tables.
- Permanent routing changes to avoid a regulator’s jurisdiction.
- Communications or disclosures to regulators or public statements.
- Manual settlement or fund movement outside normal processes.

7. What NOT to do
- Do not attempt to circumvent regulatory limits by splitting transactions without legal approval.
- Do not suppress logging of regulatory checks or conceal audit trails.
- Do not alter timestamps, locations, or any evidence required for regulatory reporting.
- Do not re-label or misclassify transactions to evade controls.
- Do not perform ad-hoc code changes in production to “work around” regulation without approval.

8. Regulatory / compliance notes
- Maintain full audit trail per PCI-DSS and local regulator requirements; ensure immutability where required.
- PSD2 / SCA: do not bypass mandated authentication flows for EU transactions without explicit exemptions.
- AML/CTF: high-velocity or high-value exemptions require compliance and legal signoff before action.
- Country-specific: follow RBI/other central bank restrictions on prepaid instruments, cross-border flows, and data residency.
- Any merchant or account-level exemptions must be documented, timeboxed, and approved by compliance/legal.


# Regulatory Limits

## Overview
Regulatory limits impose hard constraints on payment processing behavior.
These constraints vary by geography, payment network, and transaction type
and cannot be bypassed by system logic.

## Common Failure Patterns
- Hard declines due to transaction amount caps
- Velocity-based blocking after regulatory thresholds
- Settlement delays triggered by compliance checks
- Regional payment method unavailability
- Forced step-up authentication failures

## Observable Signals (Metrics / Logs)
- Consistent decline codes tied to geography or amount
- Failures clustered around regulatory thresholds
- Increased compliance_flag or blocked_transaction events
- Settlement holds without processing errors
- Network-provided regulatory response codes

## Probable Root Causes
- Exceeded transaction or daily volume limits
- Cross-border or currency restrictions
- KYC / AML enforcement triggers
- Strong customer authentication enforcement
- Sanctions or watchlist screening hits
- Network-mandated compliance enforcement

## Safe Mitigation Actions
- Surface clear decline reasons to upstream systems
- Route to compliant alternative payment methods
- Enforce transaction throttling near limits
- Preserve transaction state for audit and review
- Apply region-aware routing logic

## Actions Requiring Human Approval
- Blocking or unblocking regulated entities
- Adjusting compliance thresholds
- Overrides impacting settlement or funds movement
- Manual release of held transactions

## What NOT to Do
- Do not attempt automated overrides of regulatory blocks
- Do not mask regulatory decline reasons
- Do not retry transactions blocked by regulation
- Do not alter compliance logs

## Regulatory / Compliance Notes
- Must comply with PCI-DSS, local banking regulations, and network rules
- RBI, SEPA, and card network rules vary by region
- All compliance actions must be explainable and logged


# Regulatory Limits and Compliance Constraints

## Overview

Payment systems operate within complex regulatory frameworks that vary by jurisdiction, payment type, and customer segment. Regulatory limits exist to prevent money laundering, fraud, terrorism financing, and to protect consumer rights. Unlike technical constraints that can be optimized for performance, regulatory limits are hard boundaries that must never be violated, regardless of business impact.

Violations can result in:
- Substantial fines (ranging from $10,000 to $100,000,000+ depending on jurisdiction and severity)
- License revocation or suspension
- Criminal prosecution of executives and employees
- Reputational damage and customer loss
- Mandatory business process audits
- Enhanced regulatory oversight and restrictions

This runbook covers:
- Transaction amount limits by jurisdiction and payment type
- Velocity limits and monitoring requirements
- Customer verification and authentication thresholds
- Cross-border transaction constraints
- Reporting and notification obligations
- Record-keeping and audit requirements

## Common Regulatory Constraint Violations

### Transaction Amount Limit Breaches

**Single transaction limit violations**
- Customer attempting transaction exceeding daily limit ($10,000 USD in many jurisdictions)
- Merchant processing single transaction above authorization tier
- Cross-border transaction exceeding country-specific caps
- High-risk merchant category exceeding restricted limits
- Prepaid card transaction exceeding load or spending limits
- Cash-equivalent purchase limits violated (gift cards, money orders)

**Pattern indicators:**
- Multiple transactions just below reporting threshold (structuring)
- Transaction split across multiple cards from same customer
- Rapid succession of maximum-allowed transactions
- Geographic pattern suggesting attempt to avoid higher-scrutiny jurisdictions
- Time-based patterns aligned with limit reset periods

**Cumulative limit violations**
- Daily aggregate limits exceeded ($50,000 typical threshold)
- Weekly rolling window limits breached
- Monthly transaction volume caps violated
- Annual transaction limits for specific customer segments
- Account-level cumulative limits over account lifetime
- Merchant category aggregate limits exceeded

### Velocity and Frequency Violations

**Transaction velocity breaches**
- Too many transactions in short time period (>10 transactions/minute)
- Exceeding hourly transaction count limits
- Daily transaction count violations (varies by customer type: 20-50 typical)
- Geographic velocity violations (transactions from multiple countries within minutes)
- Card-present and card-not-present mixed velocity patterns
- Device fingerprint velocity indicating account testing or credential stuffing

**Customer onboarding velocity**
- Too many new accounts from single IP address
- Rapid account creation exceeding risk thresholds
- Multiple accounts with similar or identical details
- Geographic clustering of new account registrations
- Temporal clustering suggesting coordinated account creation

**Merchant enrollment velocity**
- Multiple merchant applications from single entity
- Rapid merchant category switching indicating potential fraud
- High-risk MCC applications exceeding approval quotas
- Geographic concentration of merchant applications

### Know Your Customer (KYC) and Identity Verification Failures

**Insufficient customer verification**
- Transaction attempted before KYC completion
- KYC verification expired or incomplete
- High-risk transaction requiring enhanced due diligence not performed
- Beneficial owner information missing for business accounts
- Source of funds not adequately verified for large transactions
- Politically exposed person (PEP) screening not completed

**Identity verification gaps**
- Document verification not completed for threshold transactions
- Biometric verification bypassed when required
- Two-factor authentication not enforced for regulated operations
- Address verification insufficient for cross-border transactions
- Age verification missing for age-restricted purchases

### Cross-Border and International Violations

**Sanctions and embargo violations**
- Transaction with sanctioned country (OFAC list violations)
- Payment to entity on denied parties list (SDN, EU sanctions)
- Transaction through sanctioned financial institutions
- Cryptocurrency transaction from restricted jurisdiction
- Dual-use goods transaction without proper export license

**Cross-border limit violations**
- Exceeding country-specific incoming payment limits
- Outgoing payment caps violated for source jurisdiction
- Foreign exchange transaction limits breached
- Remittance limits exceeded (often $2,500-$10,000 per transaction)
- Trade finance limits not properly verified

**Currency control violations**
- Hard currency transaction limits exceeded in restricted economies
- Capital control evasion patterns detected
- Unofficial exchange rate usage indicating black market participation
- Required government approvals for forex not obtained

### Strong Customer Authentication (SCA) Violations

**European PSD2 SCA requirements**
- Transaction >€30 without SCA in EU
- Cumulative transactions >€100 since last SCA
- Merchant-initiated transaction without valid exemption
- Trusted beneficiary list not properly maintained
- Transaction risk analysis exemption applied incorrectly
- Low-value exemption misused (>5 consecutive transactions)

**Two-factor authentication gaps**
- High-risk transaction without 2FA
- Step-up authentication not triggered at threshold
- Authentication method not meeting regulatory standard
- Biometric authentication bypass in regulated scenario
- One-time password not required when mandated

### Anti-Money Laundering (AML) Red Flags

**Structuring and smurfing patterns**
- Multiple transactions just below $10,000 reporting threshold
- Coordinated transactions across multiple accounts
- Rapid deposits followed by immediate withdrawals
- Round-dollar amounts suggesting deliberate structuring
- Pattern of cash deposits followed by wire transfers

**Suspicious activity patterns**
- Transactions inconsistent with customer profile
- Business account with personal-looking transaction patterns
- Dormant account suddenly active with large volumes
- Geographic patterns inconsistent with customer location
- Industry or business type mismatched with transaction patterns

**High-risk transaction indicators**
- Transactions with high-risk countries
- Cryptocurrency purchases exceeding normal patterns
- Precious metals or cash-equivalent purchases
- Transactions with known money service businesses
- Complex transaction chains with no clear business purpose

### Consumer Protection Violations

**Unauthorized transaction processing**
- Recurring payment without active customer consent
- Card-on-file transaction without proper authorization
- Automatic renewal without adequate notice (15-30 days typical)
- Free trial conversion without explicit customer acknowledgment

**Disclosure and transparency failures**
- Fees not properly disclosed before transaction
- Exchange rate markup not clearly communicated
- Subscription terms not adequately presented
- Dispute rights and chargeback information not provided
- Cancellation policy not prominently displayed

**Refund and reversal violations**
- Refund not processed within regulatory timeline (typically 5-10 days)
- Partial refund without customer agreement
- Refund to different payment method without authorization
- Failed transaction not reversed within required timeframe

## Observable Signals

### Real-Time Monitoring Metrics

**Transaction limit monitoring**
- `regulatory.transaction.amount.daily_aggregate` approaching threshold
- `regulatory.transaction.count.hourly` exceeding configured limit
- `regulatory.customer.transaction.monthly_volume` nearing cap
- `regulatory.merchant.transaction.category_limit` breached
- `regulatory.cross_border.amount.daily` approaching country limit
- `regulatory.prepaid.load.monthly_limit` exceeded

**Velocity and pattern detection**
- `regulatory.velocity.transactions_per_minute` exceeding threshold
- `regulatory.velocity.unique_cards_per_ip` indicating testing
- `regulatory.velocity.geographic_distance` suggesting impossible travel
- `regulatory.pattern.structuring_score` elevated above baseline
- `regulatory.pattern.smurfing_probability` triggered
- `regulatory.chaining.transaction_depth` exceeding normal

**Authentication and verification metrics**
- `regulatory.sca.exemption_rate` exceeding permitted percentage
- `regulatory.sca.authentication_failures` clustering
- `regulatory.kyc.verification_pending.age` exceeding threshold
- `regulatory.2fa.bypass_rate` above policy limits
- `regulatory.identity.verification_incomplete` count elevated

**Geographic and sanctions monitoring**
- `regulatory.sanctions.screening_hits` requiring review
- `regulatory.geographic.restricted_country.attempts` detected
- `regulatory.ofac.potential_match.count` elevated
- `regulatory.cross_border.unapproved_corridor` transactions attempted
- `regulatory.currency_control.violation_probability` triggered

### Logging and Alert Patterns

**Compliance event logs**
```
CRITICAL: Daily transaction limit exceeded for customer_id=12345 ($10,247 vs $10,000 limit)
WARNING: SCA exemption rate 22% (limit: 20%) for merchant_id=67890
ERROR: Transaction attempted with sanctioned entity: country=XYZ, list=OFAC_SDN
INFO: Structuring pattern detected: 5 transactions of $9,900 in 2 hours
CRITICAL: KYC verification expired for customer_id=54321 attempting $5,000 transaction
WARNING: Velocity limit approached: 18/20 hourly transactions for customer_id=11111
ERROR: Cross-border limit violated: $12,000 attempted, $10,000 daily limit for corridor US->IN
```

**Regulatory alert triggers**
- Alert: "Customer approaching daily transaction limit (90% of $10,000)"
- Alert: "Potential structuring pattern: Multiple transactions near $10,000 threshold"
- Alert: "SCA required but not performed: Transaction amount €45"
- Alert: "Sanctions screening match: Review required before processing"
- Alert: "KYC verification gap: Enhanced due diligence required for transaction amount"
- Alert: "Velocity threshold breached: 12 transactions in 5 minutes"

### Audit Trail Indicators

**Compliance documentation gaps**
- Missing customer consent for recurring transactions
- Incomplete beneficial ownership information
- Expired identity verification documents
- Missing transaction risk assessment for high-value transactions
- Insufficient source of funds documentation
- PEP screening not performed or outdated

**Suspicious activity report (SAR) triggers**
- Automated system flagging for manual SAR review
- Customer behavior changes requiring investigation
- Pattern matching known money laundering typologies
- Multiple low-confidence signals combining into high-confidence alert
- Manual review queue backlogs indicating insufficient staffing

## Probable Root Causes

### System Configuration Errors

**Limit configuration mistakes**
- Regulatory limits not updated after rule changes
- Jurisdiction-specific limits applied incorrectly
- Customer segment limits misconfigured (retail vs business)
- Currency conversion errors in limit calculation
- Aggregation logic not accounting for all transaction types
- Rolling window calculations implemented incorrectly
- Time zone handling causing daily limit reset issues

**Rule engine failures**
- Regulatory rule precedence incorrect
- Exception handling bypassing necessary checks
- Rule deployment not synchronized across all systems
- A/B testing framework inadvertently disabling compliance rules
- Feature flags incorrectly toggling off regulatory checks
- Race conditions in distributed systems causing inconsistent enforcement

**Integration issues**
- Sanctions screening service API failures
- KYC provider integration returning stale data
- Identity verification service timeouts causing bypasses
- Cross-border payment network not returning limit info
- Currency exchange rate service failures affecting limit calculations

### Data Quality and Synchronization Issues

**Customer profile data issues**
- Customer jurisdiction incorrectly recorded
- KYC status not updated after verification completion
- Customer type misclassified (individual vs business)
- Risk tier not properly assigned or updated
- Account creation date discrepancies affecting age-based limits
- Duplicate customer records causing limit fragmentation

**Transaction data quality problems**
- Merchant category code (MCC) misclassified
- Currency code errors in multi-currency processing
- Geographic location data inaccurate or missing
- Transaction type misidentified (purchase vs ATM vs cash advance)
- Card-present vs card-not-present flag incorrect
- Cross-border indicator not set properly

**Synchronization failures**
- Customer verification status not propagated to authorization system
- Limit usage counters not updated in real-time
- Distributed cache inconsistency across regions
- Database replication lag causing stale limit data
- Message queue delays in limit update propagation
- Clock skew between systems affecting time-based limits

### Business Process Gaps

**Manual process failures**
- Enhanced due diligence not performed when required
- PEP screening skipped or inadequately documented
- Source of funds verification insufficient
- Beneficial owner identification incomplete
- Risk assessment not conducted for high-value customers
- Periodic review cycles not maintained

**Training and awareness deficiencies**
- Operations team unaware of recent regulatory changes
- Customer service representatives providing incorrect limit information
- Merchant onboarding team not enforcing proper KYC
- Engineering team deploying changes without compliance review
- Risk team not calibrating detection models appropriately

**Workflow and approval issues**
- High-risk transactions not routed to manual review
- Approval thresholds set incorrectly
- Exception approval process bypassing required controls
- Insufficient segregation of duties in approval chain
- Escalation procedures not followed for edge cases

### Regulatory Environment Changes

**New regulations not implemented**
- Recent legislation not reflected in system rules
- Jurisdiction added to sanctions list not blocked
- Transaction limit reductions not enforced
- New customer verification requirements not implemented
- Enhanced authentication mandates not coded

**Regulatory interpretation differences**
- Ambiguous regulations implemented inconsistently
- Legal interpretation not aligned with technical implementation
- Industry guidance updates not incorporated
- Regulatory clarifications not reflected in systems
- Safe harbor provisions not properly utilized

### External System Dependencies

**Third-party service failures**
- Sanctions screening service outage causing bypasses
- KYC verification provider downtime
- Identity verification service degraded performance
- Credit bureau lookup failures
- Fraud detection service not available
- Currency exchange rate provider outage

**Network and connectivity issues**
- Cross-border payment network delays causing timeout bypasses
- Card network communication failures
- International wire transfer network unavailability
- Real-time payment system outages
- Cryptocurrency blockchain network congestion

## Safe Mitigation Actions

### Immediate Response (0-15 minutes)

**Transaction blocking and holds**
- **Place immediate hold on violating transactions**: Prevent settlement while investigating
  - Action: Mark transaction as `REGULATORY_HOLD` status
  - Duration: 24-72 hours or until compliance review completed
  - Customer communication: "Your transaction requires additional review for security purposes"
  - Reversibility: Ensure ability to reverse hold if false positive
  
- **Block further transactions for affected customer**: Prevent accumulating violations
  - Scope: Specific customer account only, not all customers
  - Duration: Until compliance review and remediation completed
  - Alternative: Allow low-value transactions under manual review
  - Restore: Automated process once compliance verification obtained

**Alert and escalation**
- **Trigger immediate compliance team notification**: Page on-call compliance officer
  - Severity: Critical for direct regulatory violations
  - Information: Transaction details, regulatory rule violated, customer info
  - Response SLA: 15 minutes for critical violations
  - Escalation: Legal and executive team if high-dollar or high-risk violation
  
- **Create incident ticket with regulatory tag**: Track for audit purposes
  - Required fields: Regulation violated, transaction IDs, customer IDs, amounts
  - Urgency: Highest priority, above technical incidents
  - Assignment: Compliance team with copy to legal
  - SLA: 4 hours for initial assessment, 24 hours for resolution plan

**Data preservation**
- **Capture complete transaction audit trail**: Immutable log of all related events
  - Capture: Request, response, all system interactions, decision points
  - Timestamp: All events with microsecond precision
  - Storage: Write-once compliance database, 7-year retention
  - Access control: Compliance and legal only, full audit log of access
  
- **Preserve all related customer data**: Current state snapshot
  - Include: Customer profile, verification status, transaction history, limits, risk scores
  - Format: Timestamped JSON snapshot immutable storage
  - Purpose: Regulatory investigation or audit support
  - Retention: Indefinite for violations, 7 years minimum

### Short-term Stabilization (15-60 minutes)

**Root cause investigation**
- **Analyze violation pattern**: Single incident vs systematic issue
  - Check: How many customers affected
  - Review: Whether configuration error or malicious activity
  - Assess: If other transactions at risk of similar violations
  - Timeline: Complete initial assessment within 30 minutes
  
- **Review recent system changes**: Identify potential cause
  - Deploy logs: Last 48 hours of production changes
  - Configuration: Recent rule or limit updates
  - Integration: External service changes or failures
  - Code: Recent feature releases that might affect compliance
  
- **Validate regulatory rule implementation**: Confirm correct interpretation
  - Legal review: Verify current regulation understanding
  - Compliance check: Confirm limit values and calculation methods
  - Jurisdictional: Verify correct rules for customer geography
  - Documentation: Check against compliance runbooks and legal memos

**Customer communication**
- **Notify affected customers appropriately**: Transparent but secure communication
  - Template: Pre-approved regulatory hold notification message
  - Timing: Within 1 hour of transaction hold
  - Channel: Secure message in customer portal, not email (avoid phishing concerns)
  - Content: Explain hold reason without detailed regulatory citation, provide next steps
  - Support: Dedicated compliance support line for customer questions
  
- **Provide status updates**: Keep customer informed during investigation
  - Frequency: Every 24 hours if hold extends beyond 24 hours
  - Transparency: Estimated timeline for resolution
  - Empathy: Acknowledge inconvenience while maintaining security posture

**Regulatory notification assessment**
- **Determine if immediate regulatory reporting required**: Check notification thresholds
  - Criteria: Violation severity, customer impact, amount involved
  - Timeframes: Some regulations require 24-hour notification
  - Jurisdictions: Different notification requirements per regulator
  - Consultation: Legal and compliance leadership before filing
  
- **Prepare preliminary incident summary**: Draft for potential regulatory filing
  - Include: What happened, how many affected, immediate actions taken
  - Timeline: Sequence of events with timestamps
  - Impact: Financial amounts, customer count, geographic scope
  - Mitigation: Steps taken to prevent recurrence

### Medium-term Resolution (1-24 hours)

**System remediation**
- **Deploy emergency fix if configuration error**: Correct misconfigured limits
  - Testing: Validate fix in staging environment first
  - Deployment: Use expedited change process with compliance approval
  - Monitoring: Enhanced monitoring post-deployment
  - Rollback: Immediate rollback plan if fix causes issues
  
- **Implement temporary safeguards**: Additional validation layers
  - Double-check: Add redundant limit validation before transaction approval
  - Manual review: Route borderline transactions to human review queue
  - Alert threshold: Lower alert thresholds to catch near-violations
  - Rate limiting: Reduce transaction velocity to allow better monitoring
  
- **Enhance monitoring and alerting**: Catch future violations proactively
  - Real-time: Add alerts at 50%, 75%, 90% of regulatory limits
  - Dashboard: Create compliance-specific monitoring dashboard
  - Reporting: Automated daily compliance metrics reports
  - Trending: Identify customers approaching limits before violation

**Compliance review and documentation**
- **Complete formal compliance assessment**: Document full incident analysis
  - Scope: All transactions during relevant period
  - Review: Customer verification status, limit calculations, rule applications
  - Findings: Root cause, contributing factors, regulatory exposure
  - Recommendations: Short-term and long-term remediation actions
  
- **Assess regulatory reporting obligation**: Determine filing requirements
  - Regulations: SAR, CTR, FinCEN Form 8300, or jurisdiction-specific filings
  - Thresholds: Compare incident to regulatory reporting thresholds
  - Timing: Calculate filing deadlines
  - Preparation: Gather all required documentation for filing
  
- **Document remediation plan**: Formal plan for preventing recurrence
  - Technical: System changes, configuration updates, validation enhancements
  - Process: Workflow improvements, approval process changes
  - Training: Staff education on regulatory requirements
  - Timeline: Implementation schedule with milestones
  - Ownership: Assign responsible parties for each remediation item

**Customer remediation**
- **Review held transactions for release**: Determine which can proceed
  - Compliant: Release transactions that pass enhanced review
  - Violations: Permanently decline transactions that cannot be compliantly processed
  - Alternatives: Offer compliant alternatives (lower amount, different method)
  - Communication: Notify customers of decision with explanation
  
- **Compensate for valid transaction delays**: Customer goodwill where appropriate
  - Policy: Follow established compensation guidelines
  - Approval: Finance and compliance approval for compensation
  - Documentation: Record rationale for compensation decisions
  - Limits: Cap compensation amounts appropriately

**Regulatory and legal coordination**
- **Brief legal counsel**: Ensure legal team aware and engaged
  - Exposure: Potential fine amounts and legal consequences
  - Strategy: Legal approach to regulatory communication
  - Documentation: Legal hold on incident-related data
  - Privilege: Attorney-client privileged analysis of exposure
  
- **Coordinate with compliance officer**: Align on regulatory approach
  - Reporting: Confirm regulatory filing strategy
  - Remediation: Validate compliance remediation plan
  - Communication: Prepare for potential regulatory inquiries
  - Examination: Consider potential for regulatory examination

### Long-term Prevention (24 hours - weeks)

**Systematic improvements**
- **Implement enhanced compliance controls**: Strengthen regulatory framework
  - Dual validation: Require two independent systems to validate regulatory limits
  - Pre-transaction screening: Check compliance before initiating transaction
  - Limit buffering: Set internal limits 10% below regulatory thresholds
  - Automated testing: Continuous compliance rule validation in CI/CD pipeline
  
- **Enhance compliance monitoring**: Proactive detection capabilities
  - Machine learning: Deploy ML models to detect structuring and suspicious patterns
  - Behavioral analytics: Monitor customer behavior changes indicating risk
  - Network analysis: Detect coordinated activity across accounts
  - Geospatial: Identify impossible geographic patterns
  
- **Improve data quality**: Address root cause data issues
  - Validation: Stricter data validation at point of entry
  - Enrichment: Enhance customer and transaction data with external sources
  - Synchronization: Eliminate data synchronization delays
  - Reconciliation: Regular data quality reconciliation processes

**Process enhancements**
- **Strengthen compliance training**: Ensure all staff understand requirements
  - Frequency: Quarterly compliance training for all employees
  - Role-specific: Targeted training for high-risk roles
  - Testing: Compliance knowledge testing and certification
  - Updates: Rapid training deployment for regulatory changes
  
- **Enhance change management**: Compliance review in all changes
  - Checkpoint: Mandatory compliance review before production deployment
  - Assessment: Compliance impact assessment for all changes
  - Testing: Compliance test cases in QA process
  - Approval: Compliance sign-off required for regulatory-adjacent changes
  
- **Implement periodic compliance audits**: Regular self-assessment
  - Frequency: Monthly internal compliance audits
  - Scope: Sample-based transaction review
  - Remediation: Documented action plans for findings
  - Trending: Track compliance metrics over time

**Technology investments**
- **Upgrade compliance technology**: Invest in better tools
  - Sanctions screening: Real-time, comprehensive screening solution
  - KYC platform: Modern, automated KYC and customer verification
  - Transaction monitoring: Advanced AML transaction monitoring system
  - Case management: Compliance case management and workflow platform
  - Reporting: Automated regulatory reporting solution
  
- **Implement compliance orchestration**: Centralized compliance decision engine
  - Rules engine: Centralized regulatory rule management
  - Decision service: Real-time compliance decision API
  - Audit logging: Comprehensive compliance audit trail
  - Testing: Compliance rule simulation and testing framework

## Actions Requiring Human Approval

### Transaction and Customer Actions

**Release of regulatory holds**
- **Approval required from**: Compliance Officer or designated deputy
- **Documentation needed**: 
  - Completed compliance review summary
  - Customer verification status confirmation
  - Transaction legitimacy assessment
  - Regulatory risk evaluation
- **Criteria**: Transaction must pass enhanced due diligence
- **Timeline**: Approval decision within 48 hours of review completion
- **Communication**: Customer notification of decision and reasoning

**High-value transaction exceptions**
- **Approval required from**: Chief Compliance Officer for amounts >$100,000
- **Process**:
  - Enhanced due diligence documentation
  - Source of funds verification
  - Business purpose justification
  - Beneficial owner identification
  - Risk assessment completion
- **Approval levels**:
  - $50,000-$100,000: Compliance Manager
  - $100,000-$500,000: Chief Compliance Officer
  - >$500,000: Chief Compliance Officer + Legal Counsel
- **Documentation**: Comprehensive approval memo with rationale

**Customer account restrictions or closures**
- **Approval required from**: Compliance Officer + Legal review
- **Grounds**: 
  - Repeated regulatory violations
  - Suspicious activity pattern that cannot be resolved
  - Customer non-cooperation with verification requests
  - High-risk customer profile beyond appetite
- **Process**:
  - 30-day notice to customer (unless criminal investigation)
  - Opportunity for customer to provide explanations
  - SAR filing if suspicious activity detected
  - Coordination with law enforcement if required
- **Communication**: Legal-approved closure notification letter

### Regulatory and Compliance Actions

**Suspicious Activity Report (SAR) filing**
- **Approval required from**: 
  - Initial determination: Compliance Analyst or Manager
  - Final approval: Chief Compliance Officer
  - Legal review: General Counsel or Deputy General Counsel
- **Timeline**:
  - Initial assessment: Within 24 hours of detection
  - SAR filing: Within 30 days of initial detection
  - Continuing activity: Additional SARs every 90 days if continuing
- **Required documentation**:
  - Detailed narrative of suspicious activity
  - Supporting transaction documentation
  - Customer due diligence records
  - Previous SAR history for customer if applicable
- **Confidentiality**: Strict prohibition on customer notification (tipping off)

**Regulatory notification and reporting**
- **Approval required from**: 
  - General Counsel
  - Chief Compliance Officer
  - CEO (for major incidents)
- **Triggers**:
  - Material regulatory violation
  - Systematic compliance failure
  - Significant customer impact
  - Regulatory inquiry received
- **Coordination**:
  - External legal counsel consultation
  - Board notification for significant issues
  - Insurance carrier notification if appropriate
  - Communications team for public relations considerations

**Regulatory examination responses**
- **Approval required from**: 
  - General Counsel for all exam responses
  - Chief Compliance Officer for compliance representations
  - CEO or CFO for financial representations
- **Process**:
  - Centralized exam response coordination
  - Document collection and review
  - Attorney-client privilege review
  - Response quality control review
- **Timeline**: Typically 30-60 days for full exam responses

### System and Policy Changes

**Regulatory limit adjustments**
- **Approval required from**:
  - Chief Compliance Officer for limit changes
  - Legal Counsel for regulatory interpretation
  - CTO for technical implementation approach
- **Required analysis**:
  - Regulatory requirement documentation
  - Current vs required limit comparison
  - System impact assessment
  - Customer impact analysis
  - Revenue impact projection
- **Testing**: Comprehensive testing in staging environment
- **Rollout**: Phased deployment with monitoring
- **Communication**: Customer notification if limits reduced

**Compliance system changes**
- **Approval required from**:
  - Chief Compliance Officer for functionality changes
  - Information Security Officer for security implications
  - CTO for production deployment
- **Change control**:
  - Compliance impact assessment required
  - Pre-production validation of compliance rules
  - Parallel run with existing system (if feasible)
  - Rollback plan for compliance-critical systems
- **Documentation**:
  - Detailed change specification
  - Compliance rule testing results
  - User acceptance testing sign-off
  - Post-implementation validation plan

**Third-party compliance service changes**
- **Approval required from**:
  - Chief Compliance Officer
  - Chief Information Security Officer
  - Procurement (for contract changes)
  - Legal (for vendor agreements)
- **Due diligence**:
  - Vendor compliance certification verification
  - Data privacy and security assessment
  - Service level agreement review
  - Disaster recovery and business continuity validation
  - Reference checks with similar organizations
- **Contract requirements**:
  - Right to audit clauses
  - Data protection and confidentiality
  - Regulatory examination cooperation
  - Incident notification timelines

### Financial and Business Actions

**Regulatory fine or penalty payment**
- **Approval required from**:
  - CFO for financial approval
  - General Counsel for legal strategy
  - CEO and Board (for amounts >$1,000,000)
- **Assessment**:
  - Settlement vs litigation analysis
  - Precedent and reputation considerations
  - Financial impact evaluation
  - Insurance coverage determination
- **Documentation**:
  - Detailed incident analysis
  - Remediation plan
  - Future prevention measures
  - Board resolution (for significant amounts)

**Compensation for regulatory failures**
- **Approval required from**:
  - Chief Compliance Officer
  - General Counsel
  - CFO (for aggregate amounts)
- **Criteria**:
  - Customer materially harmed by compliance failure
  - Goodwill gesture appropriate
  - Regulatory requirement for customer reimbursement
  - Competitive or reputational considerations
- **Limits**:
  - Individual compensation caps
  - Aggregate monthly limits
  - Board escalation for significant amounts
- **Documentation**: Rationale and approval audit trail

**Business model or product changes**
- **Approval required from**:
  - Chief Compliance Officer for regulatory assessment
  - General Counsel for legal implications
  - CEO and executive team for strategic decisions
  - Board of Directors (for material changes)
- **Regulatory analysis**:
  - Licensing requirements assessment
  - Regulatory approval or notification requirements
  - Ongoing compliance obligations
  - Capital and reserve requirements
  - Examination and reporting obligations
- **Timeline**: Often 6-12 months for regulatory approvals

## What NOT to Do

### Transaction Processing Prohibitions

**Do NOT process transactions that violate regulatory limits**
- **Why**: Direct regulatory violation with immediate consequences
- **Even if**: Customer is long-standing and trusted
- **Even if**: Transaction appears legitimate
- **Even if**: Business impact is significant
- **Instead**: Hold transaction for compliance review, seek exception approval if available

**Do NOT bypass sanctions screening**
- **Why**: Criminal liability for sanctions violations (IEEPA, TWEA)
- **Consequences**: Fines up to $20 million + 2x transaction value, criminal prosecution
- **Even if**: Screening service is experiencing outage
- **Even if**: Transaction is time-sensitive
- **Instead**: Queue transaction until screening available, or decline transaction

**Do NOT split transactions to avoid reporting**
- **Why**: Structuring is itself a crime (31 USC 5324)
- **Applies to**: Even if customer requests splitting
- **Applies to**: Even if for customer convenience
- **Detection**: Automated systems monitor for structuring patterns
- **Instead**: Process as single transaction with appropriate reporting

**Do NOT process transactions during KYC gaps**
- **Why**: Processing without adequate customer verification violates AML regulations
- **Threshold**: High-value transactions require enhanced due diligence
- **Even if**: Customer has history of legitimate transactions
- **Instead**: Complete KYC before processing, or decline transaction

### System and Configuration Mistakes

**Do NOT disable compliance checks for performance**
- **Why**: Creates systematic regulatory violations
- **Temptation**: Compliance checks add latency
- **Reality**: Latency is acceptable cost for regulatory compliance
- **Consequences**: Massive systematic violations, regulatory enforcement
- **Instead**: Optimize compliance checks for performance while maintaining accuracy

**Do NOT deploy compliance changes without thorough testing**
- **Why**: Errors can cause either systematic violations or excessive false positives
- **Testing required**: 
  - Unit tests for all compliance rules
  - Integration tests with realistic transaction patterns
  - Regression tests against known scenarios
  - Load testing under peak traffic conditions
- **Validation**: Compliance officer review and sign-off
- **Instead**: Comprehensive test suite with compliance validation

**Do NOT configure limits based on business goals**
- **Why**: Limits must be based on regulatory requirements, not revenue targets
- **Error**: Setting limits above regulatory thresholds for business reasons
- **Example failure**: "We need to support $50K transactions but regulation caps at $10K"
- **Correct approach**: Comply with regulation, find compliant alternatives for customers
- **Instead**: Implement regulatory limits precisely, offer compliant workarounds

**Do NOT rely solely on third-party compliance services**
- **Why**: Responsibility for compliance remains with the company, not the vendor
- **Vendor failure**: Sanctions screening service has coverage gap
- **Company liability**: Company still liable for violations
- **Due diligence**: Regular vendor performance audits required
- **Instead**: Dual vendor strategy or internal backup for critical compliance functions

### Data and Documentation Mistakes

**Do NOT delete compliance audit trails**
- **Why**: Regulatory requirement for record retention (typically 5-7 years)
- **Applies to**: Transaction records, compliance decisions, customer data
- **Even if**: Database storage is expensive
- **Even if**: Customer requests deletion (exceptions apply for GDPR, CCPA)
- **Instead**: Archive to compliant long-term storage, implement retention policies

**Do NOT modify audit logs**
- **Why**: Audit trail integrity is fundamental to regulatory compliance
- **Requirement**: Immutable logs for all compliance decisions
- **Technology**: Write-once storage or blockchain for critical audit data
- **Consequence**: Inability to demonstrate compliance during examination
- **Instead**: Append-only logs with cryptographic integrity verification

**Do NOT share customer data without proper authorization**
- **Why**: Privacy law violations (GDPR, CCPA, GLBA)
- **Requires**: Customer consent or legal basis for sharing
- **Exceptions**: Law enforcement with proper legal process, regulatory examination
- **Vendor sharing**: Data processing agreement required
- **Instead**: Strict data sharing policies with legal review

### Communication Mistakes

**Do NOT tip off customers to SAR filings**
- **Why**: Federal crime to notify customer about SAR (31 USC 5318(g)(2))
- **Prohibition**: Cannot mention SAR in any communication
- **Indirect**: Cannot hint or suggest SAR filing
- **Consequences**: Criminal prosecution, significant fines
- **Customer asks**: "Provide general information about compliance processes without SAR mention"

**Do NOT promise regulatory approval**
- **Why**: Approval is regulator's decision, not company's
- **Avoid**: "This will definitely be approved"
- **Use**: "We will submit for regulatory approval and provide updates"
- **Timeline**: Do not guarantee approval timelines
- **Instead**: Set appropriate expectations about regulatory process uncertainty

**Do NOT discuss customer compliance issues with third parties**
- **Why**: Privacy obligations and reputational risk
- **Exceptions**: Regulators, law enforcement with legal process, internal compliance team
- **Not allowed**: Other merchants, business partners, industry forums
- **Confidentiality**: Treat compliance issues as highly confidential
- **Instead**: Strict need-to-know basis for compliance information

### Business Decision Mistakes

**Do NOT prioritize revenue over compliance**
- **Why**: Regulatory fines and business disruption far exceed short-term revenue
- **Example**: Accepting high-risk customers to increase volume
- **Risk**: License revocation, consent orders, reputational damage
- **Long-term**: Compliance enables sustainable business growth
- **Instead**: Build compliant business model, reject non-compliant opportunities

**Do NOT implement "move fast and break things" for compliance**
- **Why**: Breaking compliance has severe consequences
- **Approach**: Deliberate, careful implementation of compliance features
- **Timeline**: Allow adequate time for compliance validation
- **Testing**: Comprehensive testing before production deployment
- **Instead**: "Move deliberately and comply with regulations"

**Do NOT assume compliance is one-time effort**
- **Why**: Regulations constantly evolve, require ongoing monitoring
- **Reality**: Continuous compliance program necessary
- **Resources**: Dedicated compliance team and budget
- **Training**: Regular staff education on regulatory changes
- **Instead**: Treat compliance as ongoing operational requirement

## Compliance Operational Notes

### Regulatory Landscape Overview

**United States**
- **Bank Secrecy Act (BSA) / Anti-Money Laundering (AML)**
  - Currency Transaction Reports (CTR): $10,000+ cash transactions
  - Suspicious Activity Reports (SAR): Suspicious transactions $5,000+
  - Customer Identification Program (CIP): Identity verification required
  - Enhanced Due Diligence (EDD): High-risk customers require additional scrutiny
  - Regulators: FinCEN, OCC, Federal Reserve, state regulators

- **USA PATRIOT Act**
  - Enhanced AML requirements
  - Beneficial ownership identification for businesses
  - Prohibition on shell bank relationships
  - OFAC sanctions compliance
  - Penalties: Up to $1,000,000 and imprisonment

- **Electronic Fund Transfer Act (EFTA) / Regulation E**
  - Consumer protection for electronic payments
  - Error resolution requirements (10 business days)
  - Unauthorized transaction liability limits
  - Disclosure requirements for fees and terms
  - Applies to: ACH, card, P2P transactions

- **State Money Transmitter Laws**
  - Licensing requirements vary by state
  - Bond and net worth requirements
  - Transaction reporting to state regulators
  - Examination and audit requirements
  - 50+ different state regulatory regimes

**European Union**

- **Payment Services Directive 2 (PSD2)**
  - Strong Customer Authentication (SCA): €30 threshold, cumulative €100
  - Open banking requirements
  - Transaction monitoring requirements
  - Incident reporting: 24 hours for major incidents
  - Regulators: National competent authorities (FCA, BaFin, etc.)

- **Anti-Money Laundering Directives (AMLD 5 & 6)**
  - Enhanced due diligence for high-risk transactions
  - Beneficial ownership registers
  - Cryptocurrency exchange regulation
  - Politically exposed persons (PEP) screening
  - Transaction limits and reporting thresholds vary by member state

- **General Data Protection Regulation (GDPR)**
  - Lawful basis required for processing
  - Right to explanation for automated decisions
  - Data minimization principles
  - Right to erasure (conflicts with retention requirements - compliance exception applies)
  - Fines: Up to €20 million or 4% of global revenue

**United Kingdom**

- **Financial Conduct Authority (FCA) Rules**
  - Payment Services Regulations 2017 (PSR)
  - SCA requirements similar to PSD2
  - Consumer protection requirements
  - Financial crime prevention obligations
  - Senior Managers Regime (individual accountability)

- **Money Laundering Regulations 2017**
  - Risk-based approach to AML
  - Customer due diligence requirements
  - Ongoing monitoring obligations
  - Suspicious activity reporting to NCA
  - Penalties: Unlimited fines, imprisonment up to 14 years

**India**

- **Reserve Bank of India (RBI) Regulations**
  - Payment and Settlement Systems Act, 2007
  - Prepaid payment instruments (PPI) regulations
  - Know Your Customer (KYC) norms
  - Transaction limits: ₹10,000 minimum KYC, ₹1,00,000 full KYC
  - Cross-border transaction restrictions

- **Prevention of Money Laundering Act (PMLA)**
  - Customer identification requirements
  - Record keeping: 5 years after transaction
  - Suspicious transaction reporting to FIU-IND
  - Penalties: Rigorous imprisonment up to 10 years, fines

**Singapore**

- **Payment Services Act 2019**
  - Licensing requirements for payment service providers
  - AML/CFT requirements
  - Technology risk management
  - Outsourcing requirements
  - Regulator: Monetary Authority of Singapore (MAS)

- **Personal Data Protection Act (PDPA)**
  - Consent requirements for data processing
  - Cross-border data transfer restrictions
  - Data protection impact assessments
  - Notification of data breaches
  - Fines: Up to 10% of annual turnover

### Industry-Specific Considerations

**Card Networks (Visa, Mastercard)**
- Network rules supplement regulatory requirements
- Operating regulations and bylaws compliance required
- Chargeback rules and timelines
- PCI-DSS compliance for card data security
- Fines and penalties for rule violations
- Possible loss of processing ability for severe violations

**Cryptocurrency and Digital Assets**
- Travel Rule: $1,000+ crypto transactions require beneficiary information
- FinCEN guidance: Cryptocurrency exchanges are money transmitters
- FATF standards: Cryptocurrency subject to AML requirements
- State licensing: Many states require money transmitter license
- Sanctions compliance: OFAC applies to cryptocurrency transactions

**Cross-Border and Remittances**
- Remittance limits vary by corridor
- Registration with FinCEN as money transmitter
- State licensing requirements
- Destination country receiving limits
- Source of funds verification for large amounts
- Correspondent banking relationships subject to enhanced due diligence

### Audit and Examination Readiness

**Regulatory Examination Preparation**
- Maintain current compliance program documentation
- Regular internal compliance audits (quarterly minimum)
- Management information systems (MIS) reporting
- Board oversight documentation
- Independent compliance testing (annually minimum)
- Staff training records
- Vendor management documentation
- Incident response and remediation tracking

**Required Documentation**
- Compliance policies and procedures (reviewed annually)
- Risk assessments (updated annually or when material changes)
- Transaction monitoring scenarios and tuning
- Customer due diligence files
- SAR documentation and decisions not to file
- Training materials and attendance records
- Board meeting minutes showing compliance oversight
- Independent audit and testing reports

**Common Examination Findings**
- Inadequate transaction monitoring
- Insufficient customer due diligence
- Lack of beneficial ownership identification
- Inadequate SAR filing or documentation
- Missing or inadequate risk assessments
- Insufficient board oversight
- Inadequate training programs
- Poor vendor management

### Continuous Compliance Improvement

**Compliance Metrics and KPIs**
- SAR filing rate and quality scores
- False positive rate in transaction monitoring
- Customer due diligence completion timeliness
- Alert investigation turnaround time
- Regulatory examination findings remediation time
- Staff training completion rates
- Vendor audit completion and findings
- System availability for compliance tools

**Technology and Automation**
- Machine learning for transaction monitoring
- Automated sanctions screening
- Digital identity verification
- Automated regulatory reporting
- Compliance case management workflow
- Real-time compliance decision engines
- Advanced analytics for pattern detection
- Blockchain for audit trail immutability

**Emerging Regulatory Trends**
- Increased cryptocurrency regulation
- Cross-border payment oversight
- Real-time payment system regulation
- Open banking expansion
- Artificial intelligence governance
- Climate-related financial regulation
- Consumer data protection enhancement
- Beneficial ownership transparency requirements

This runbook should be reviewed and updated:
- Immediately upon any regulatory change
- Quarterly for operational improvements
- After any regulatory examination
- Following any compliance incident
- When expanding to new jurisdictions
- When launching new products or services