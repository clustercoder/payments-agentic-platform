def policy_node(state):
    """
    Policy node - applies business rules and constraints.
    """
    anomaly = state["anomaly"]  # Use dictionary-style access
    flags = {}

    if anomaly["severity"] > 0.9:
        flags["requires_human_approval"] = True

    if anomaly["issuer"] == "RBI_TEST":
        flags["blocked"] = True

    return {
        "policy_flags": flags
    }