"""Tracking timestamps survive export without allowing phone/secret exemptions."""
import pytest

from capstone_agent.evaluation.export import minimized_json
from capstone_agent.support.privacy import mask_sensitive


@pytest.mark.parametrize('timestamp',[
    '2026-10-05 07:30 UTC', '2026-10-05 07:30:00 UTC',
    '2026-10-05 07:30 GMT', '2026-10-05 07:30Z',
    '2026-10-05 07:30+00:00', '2026-10-05T07:30:00Z',
])
def test_tracking_clock_and_date_survive_repeated_minimization(timestamp):
    text=f'Latest tracking: {timestamp}. Phone +1-555-0100.'
    masked=mask_sensitive(text)
    assert timestamp in masked and '+1-555-0100' not in masked
    assert timestamp in minimized_json({'answer':masked})


@pytest.mark.parametrize('value',[
    '2026-10-05 07123456789', '2026-10-05 07:30 customer',
    '2026-13-05 07:30 UTC', '2026-10-05 29:30 UTC',
    '2026-10-05 07:99 UTC', '2026-10-05 07:30 UTCphone',
])
def test_phone_like_or_invalid_clock_text_has_no_timestamp_exemption(value):
    masked=mask_sensitive(value)
    assert '[REDACTED-' in masked and value not in masked


def test_configured_secret_redaction_precedes_valid_timestamp_preservation():
    timestamp='2026-10-05 07:30 UTC'
    assert timestamp not in mask_sensitive(timestamp,(timestamp,))
    assert '[REDACTED-SECRET]' in mask_sensitive(timestamp,(timestamp,))
