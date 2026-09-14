"""Trivial module so an acceptance shard repo has code to change."""


def add(left: int, right: int) -> int:
    """Return the sum of two integers."""
    return left + right


def multiply(left: int, right: int) -> int:
    """Return the product of two integers."""
    return left * right


def validate_timeouts(
    *,
    triage_timeout_hours: int,
    escalation_timeout_hours: int,
    max_job_lifetime_hours: int,
) -> None:
    """Cross-validate lifecycle timeout settings.

    Rejects combinations where the triage and escalation windows together
    exceed the maximum job lifetime, since such a job could never complete.
    """
    if triage_timeout_hours + escalation_timeout_hours >= max_job_lifetime_hours:
        raise ValueError(
            "triage_timeout_hours "
            f"({triage_timeout_hours}) + escalation_timeout_hours "
            f"({escalation_timeout_hours}) must be < "
            f"max_job_lifetime_hours ({max_job_lifetime_hours})"
        )
