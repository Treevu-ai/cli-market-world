#!/usr/bin/env python3
"""
market_logging.py — Structured JSON logging for CLI Market.

Centralizes logging configuration to ensure consistent, parseable logs
across all modules (CLI, server, collector, MCP).
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Format logs as structured JSON for better parsing and observability."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Convert LogRecord to JSON."""
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields (if any)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_obj.update(record.extra)
        
        return json.dumps(log_obj, default=str)


class ContextFilter(logging.Filter):
    """Add request/user context to logs."""
    
    def __init__(self, context: Optional[Dict[str, str]] = None):
        super().__init__()
        self.context = context or {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context fields to record."""
        record.extra = self.context
        return True


def setup_logging(
    log_level: str = "INFO",
    json_output: bool = True,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure logging system for CLI Market.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: If True, output JSON; otherwise, human-readable
        log_file: Optional path to log file. If set, logs to both console and file.
    
    Returns:
        Configured logger instance
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Formatter
    if json_output:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)


# Module-level logger
logger = get_logger("market")
