#
# Factory functions for error messages emitted by both the Sync and Async
# WebProxy clients.
#

def invalid_response_format(reason: str) -> str:
    return f"Invalid response format: {reason}"


def error_on_operation(operation_name: str, status: int, reason: str) -> str:
    return f"Error {operation_name}: {reason} ({status})"


def error_401_put(operation_name: str, operand_id: str) -> str:
    return ("Lacking valid access_token with permissions to "
            f"{operation_name} of '{operand_id}': "
            "please obtain a token and pass it to set_access_token.")


def error_403_put(operation_name: str, operand_id: str) -> str:
    return (f"Cannot {operation_name} ("
            f"'{operand_id}'): check if the device is reconfigurable and"
            " the access_token has the required permissions.")


def error_422_put(operation_name: str, operand_id: str) -> str:
    return (f"Cannot {operation_name} ({operand_id}): "
            "device is not reconfigurable.")
