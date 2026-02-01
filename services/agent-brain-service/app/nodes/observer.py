def observer_node(state):
    """
    Observer node - passes through the anomaly data.
    """
    anomaly = state["anomaly"]  # Use dictionary-style access
    return {
        "anomaly": anomaly
    }