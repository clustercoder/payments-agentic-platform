import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for Auto-Execution
AUTO_EXECUTE = os.getenv("AUTO_EXECUTE_HIGH_CONFIDENCE", "false").lower() == "true"
THRESHOLD = float(os.getenv("AUTO_EXECUTE_THRESHOLD", 1.0))

SAFE_ACTIONS = {
    "reduce_retries",
    "increase_backoff",
    "circuit_breaker"
}

def execute_action(action, state_client):
    # Fix 1: Handle schema mismatch (agent-brain sends 'proposed_action')
    action_type = action.get("action_type") or action.get("proposed_action")
    
    if not action_type:
        logger.warning("Message missing 'action_type' or 'proposed_action'")
        return {"status": "failed", "reason": "missing_action_type", "executed_at": datetime.utcnow().isoformat()}

    # ---------------------------------------------------------
    # New Logic: Auto-Execution Gate
    # ---------------------------------------------------------
    confidence = action.get("confidence", 0.0)
    
    # Check if we should execute based on config and confidence
    if AUTO_EXECUTE and confidence >= THRESHOLD:
        logger.info(f"Auto-execution threshold met (Confidence: {confidence} >= {THRESHOLD})")
    else:
        # Fallback for low confidence or disabled auto-execution
        reason = "auto_execute_disabled" if not AUTO_EXECUTE else f"confidence_too_low_{confidence}"
        logger.info(f"Skipping execution: {reason}")
        return {
            "status": "skipped", 
            "reason": reason, 
            "executed_at": datetime.utcnow().isoformat()
        }
    # ---------------------------------------------------------

    # Fix 2: Don't crash on unsafe/approval-pending actions
    if action_type not in SAFE_ACTIONS:
        logger.info(f"Skipping execution for action: {action_type} (requires approval or is unknown)")
        return {"status": "skipped", "reason": "unsafe_or_pending_approval", "executed_at": datetime.utcnow().isoformat()}

    issuer = action.get("issuer")
    if not issuer:
        logger.error("Action missing 'issuer'")
        return {"status": "failed", "reason": "missing_issuer", "executed_at": datetime.utcnow().isoformat()}

    # Fix 3: Handle missing parameters safely
    params = action.get("parameters", {})

    try:
        if action_type == "reduce_retries":
            # Default to sensible values if parameters are missing
            max_retries = params.get("max_retries", 1)
            backoff_ms = params.get("backoff_ms", 1000)
            state_client.set_retry_policy(
                issuer=issuer, max_retries=max_retries, backoff_ms=backoff_ms
            )
            logger.info(f"Executed reduce_retries for {issuer}")

        elif action_type == "circuit_breaker":
            state_client.open_circuit(issuer)
            logger.info(f"Opened circuit breaker for {issuer}")

        return {
            "status": "executed",
            "executed_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to execute action {action_type}: {e}")
        return {"status": "failed", "reason": str(e), "executed_at": datetime.utcnow().isoformat()}