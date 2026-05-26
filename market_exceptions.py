#!/usr/bin/env python3
"""
market_exceptions.py — Custom exception hierarchy for CLI Market.

Allows for granular error handling throughout the application.
"""


class MarketException(Exception):
    """Base exception for all CLI Market errors."""
    pass


class DatabaseError(MarketException):
    """Database connectivity, schema, or operation failed.
    
    Indicates a persistent storage layer issue that may require
    admin intervention (connection, schema mismatch, etc).
    """
    pass


class ConfigurationError(MarketException):
    """Missing or invalid configuration.
    
    Indicates environment variables, settings, or files are missing/malformed.
    """
    pass


class ValidationError(MarketException):
    """Input validation failed.
    
    Indicates client-provided data doesn't match expected schema.
    """
    pass


class RetryableError(MarketException):
    """Error that can be retried (timeout, transient connection, rate limit).
    
    The caller should implement exponential backoff.
    """
    pass


class ConnectivityError(MarketException):
    """Network connectivity issue (host unreachable, DNS, etc).
    
    Likely transient; retry is appropriate.
    """
    pass


class StoreError(MarketException):
    """Error fetching from a specific retail store.
    
    The store API may be down, or credentials invalid.
    """
    pass


class PaymentError(MarketException):
    """Payment processing failed.
    
    Could be temporary (gateway down) or permanent (invalid payment method).
    """
    pass
