# core/exceptions.py

class C2LabError(Exception):
    """Base C2Lab exception"""

    def __init__(self, message: str, code: str = "ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"[{self.code}] {self.message}"


class AgentError(C2LabError):
    """Agent-related errors"""

    def __init__(self, message: str, agent_id: str = None):
        code = f"AGENT_{agent_id}" if agent_id else "AGENT_ERROR"
        super().__init__(message, code)


class TelemetryError(C2LabError):
    """Telemetry processing errors"""

    def __init__(self, message: str):
        super().__init__(message, "TELEMETRY_ERROR")


class ModelError(C2LabError):
    """Model training/prediction errors"""

    def __init__(self, message: str):
        super().__init__(message, "MODEL_ERROR")


class SecurityError(C2LabError):
    """Security validation errors"""

    def __init__(self, message: str):
        super().__init__(message, "SECURITY_ERROR")
