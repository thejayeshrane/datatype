# backend/tools.py

def calculate(operation: str, x: float, y: float) -> float:
    """
    Performs basic arithmetic operations.
    Valid operations: 'add', 'subtract', 'multiply', 'divide'
    """
    print(f"!!! TOOL CALLED: {operation} {x} and {y} !!!")
    
    if operation == 'add':
        return x + y
    elif operation == 'subtract':
        return x - y
    elif operation == 'multiply':
        return x * y
    elif operation == 'divide':
        if y == 0:
            return "Error: Division by zero"
        return x / y
    else:
        return "Error: Unknown operation"

# The "Schema" tells the AI how to use this tool
calculate_schema = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Perform basic math operations (add, subtract, multiply, divide). Use this for ALL math questions.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The math operation to perform"
                },
                "x": {
                    "type": "number",
                    "description": "The first number"
                },
                "y": {
                    "type": "number",
                    "description": "The second number"
                }
            },
            "required": ["operation", "x", "y"]
        }
    }
}