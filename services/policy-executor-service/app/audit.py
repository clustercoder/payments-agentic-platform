import json
from datetime import datetime

def write_audit(action, execution_result):
    # Fix: Use .get() for all fields to handle schema variations safely
    action_type = action.get("action_type") or action.get("proposed_action", "unknown")
    
    record = {
        "action_id": action.get("action_id", "unknown"),
        "issuer": action.get("issuer", "unknown"),
        "action_type": action_type,
        "parameters": action.get("parameters", {}),
        "confidence": action.get("confidence", 0.0),
        "source_anomaly_id": action.get("anomaly_id") or action.get("source_anomaly_id"),
        "execution_status": execution_result.get("status", "unknown"),
        "executed_at": execution_result.get("executed_at", datetime.utcnow().isoformat())
    }
    
    try:
        with open("/data/audit.log", "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print(f"Failed to write audit log: {e}")