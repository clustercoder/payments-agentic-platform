from app.consumer import get_consumer
from app.executor import execute_action
from app.state import StateClient
from app.audit import write_audit

def main():
    consumer = get_consumer()
    state = StateClient()

    for msg in consumer:
        action = msg.value
        result = execute_action(action, state)
        write_audit(action, result)

if __name__ == "__main__":
    main()
