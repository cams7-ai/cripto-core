"""Stable diagnostic types without untrusted payloads."""


class PaperError(ValueError):
    """Somente codigos locais, sem transportar valores fornecidos."""


class MarketError(ValueError):
    """Codigo local seguro; nao transportar mensagens de servidores."""
