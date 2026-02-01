def decision_node(state):
    flags = state["policy_flags"]

    if flags.get("blocked"):
        action = "NO_ACTION_BLOCKED"
    elif flags.get("requires_human_approval"):
        action = "PROPOSE_REROUTE_PENDING_APPROVAL"
    else:
        action = "AUTO_REROUTE"

    return {
        "proposed_action": action
    }
