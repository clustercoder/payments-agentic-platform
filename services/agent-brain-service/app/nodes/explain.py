def explain_node(state):
    explanation = f"""
    Anomaly detected for issuer {state['anomaly']['issuer']}.

    Hypothesis:
    {state['hypotheses']}

    Policy decision:
    {state['policy_flags']}

    Proposed action:
    {state['proposed_action']}
    """

    return {
        "explanation": explanation
    }
