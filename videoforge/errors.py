"""Shared safe errors for VideoForge pipeline and channel routing."""

class VideoForgeError(ValueError):
    """Error identifiers never include paths, prompts or private content."""
