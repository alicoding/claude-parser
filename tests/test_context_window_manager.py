"""
Tests for Context Window Manager - Critical for workflow automation.

Validates that context monitoring works correctly for detecting
when approaching auto-compact threshold without watching UI.
"""

import pytest

from claude_parser.domain.services.context_window_manager import (
    ContextStatus,
    ContextWindowManager,
)


class TestContextWindowManager:
    """Test context window monitoring functionality."""

    @pytest.fixture
    def manager(self):
        """Create manager with default settings."""
        return ContextWindowManager()

    def test_green_status_below_50_percent(self, manager):
        """Below 50% usage should be green status."""
        # 50K tokens = 25% of 200K
        info = manager.analyze(50_000)

        assert info.status == ContextStatus.GREEN
        assert info.emoji == "🟢"
        assert info.percentage_used == 25.0
        assert not info.should_compact
        assert not info.is_critical
        assert not info.needs_attention

    def test_yellow_status_at_50_percent(self, manager):
        """50-75% usage should be yellow status."""
        # 100K tokens = 50% of 200K
        info = manager.analyze(100_000)

        assert info.status == ContextStatus.YELLOW
        assert info.emoji == "🟡"
        assert info.percentage_used == 50.0
        assert not info.should_compact
        assert not info.needs_attention

    def test_orange_status_at_75_percent(self, manager):
        """75-90% usage should be orange status."""
        # 150K tokens = 75% of 200K
        info = manager.analyze(150_000)

        assert info.status == ContextStatus.ORANGE
        assert info.emoji == "🟠"
        assert info.percentage_used == 75.0
        assert not info.should_compact
        assert info.needs_attention  # Should alert at 75%

    def test_red_status_at_90_percent(self, manager):
        """90% usage should trigger red status and auto-compact."""
        # 180K tokens = 90% of 200K (compact threshold)
        info = manager.analyze(180_000)

        assert info.status == ContextStatus.RED
        assert info.emoji == "🔴"
        assert info.percentage_used == 90.0
        assert info.should_compact  # Auto-compact triggers at 90%
        assert info.is_critical
        assert info.needs_attention
        assert info.tokens_until_compact == 0

    def test_critical_status_at_95_percent(self, manager):
        """95% usage should be critical status."""
        # 190K tokens = 95% of 200K
        info = manager.analyze(190_000)

        assert info.status == ContextStatus.CRITICAL
        assert info.emoji == "🚨"
        assert info.percentage_used == 95.0
        assert info.should_compact
        assert info.is_critical
        # Message shows auto-compact when past threshold
        assert "AUTO-COMPACT" in info.message

    def test_tokens_until_compact_calculation(self, manager):
        """Verify tokens until compact is calculated correctly."""
        # Test at various levels
        test_cases = [
            (50_000, 130_000),  # 50K used, 130K until compact
            (100_000, 80_000),  # 100K used, 80K until compact
            (150_000, 30_000),  # 150K used, 30K until compact
            (170_000, 10_000),  # 170K used, 10K until compact
            (180_000, 0),  # 180K used, 0 until compact (at threshold)
            (190_000, 0),  # 190K used, 0 (past threshold)
        ]

        for tokens_used, expected_until_compact in test_cases:
            info = manager.analyze(tokens_used)
            assert info.tokens_until_compact == expected_until_compact, (
                f"At {tokens_used} tokens, expected {expected_until_compact} until compact"
            )

    def test_percentage_until_compact(self, manager):
        """Verify percentage until compact calculation."""
        # 100K tokens = 50% used, 80K until compact = 40% until compact
        info = manager.analyze(100_000)
        assert info.percentage_until_compact == 40.0

        # 150K tokens = 75% used, 30K until compact = 15% until compact
        info = manager.analyze(150_000)
        assert info.percentage_until_compact == 15.0

    def test_simple_status_api(self, manager):
        """Test the 95% use case simple API."""
        # Simple status at 75% usage
        emoji, percent_until = manager.get_simple_status(150_000)

        assert emoji == "🟠"
        assert percent_until == 15.0  # 15% until compact

    def test_should_alert_threshold(self, manager):
        """Test alert triggering at 75% threshold."""
        # Below 75% - no alert
        assert not manager.should_alert(140_000)  # 70%

        # At or above 75% - alert
        assert manager.should_alert(150_000)  # 75%
        assert manager.should_alert(180_000)  # 90%

    def test_webhook_payload(self, manager):
        """Test webhook payload generation for integrations."""
        payload = manager.get_webhook_payload(150_000)

        assert payload["status"] == "orange"
        assert payload["percentage_used"] == 75.0
        assert payload["percentage_until_compact"] == 15.0
        assert payload["tokens_used"] == 150_000
        assert payload["tokens_limit"] == 200_000
        assert payload["tokens_until_compact"] == 30_000
        assert not payload["should_compact"]
        assert not payload["critical"]

    def test_cli_formatting(self, manager):
        """Test CLI status formatting."""
        output = manager.format_cli_status(150_000)

        assert "🟠" in output
        assert "75.0%" in output
        assert "150,000/200,000" in output
        assert "█" in output  # Progress bar fill
        assert "░" in output  # Progress bar empty

    def test_custom_context_limit(self):
        """Test with custom context limit (e.g., for different model)."""
        # Test with 100K limit instead of 200K
        manager = ContextWindowManager(context_limit=100_000)

        # 50K tokens = 50% of 100K
        info = manager.analyze(50_000)
        assert info.percentage_used == 50.0
        assert info.status == ContextStatus.YELLOW

        # 90K tokens = 90% of 100K (should compact)
        info = manager.analyze(90_000)
        assert info.percentage_used == 90.0
        assert info.should_compact

    def test_edge_cases(self, manager):
        """Test edge cases and boundary conditions."""
        # Zero tokens
        info = manager.analyze(0)
        assert info.percentage_used == 0.0
        assert info.status == ContextStatus.GREEN
        assert info.tokens_until_compact == 180_000

        # Exactly at compact threshold
        info = manager.analyze(180_000)
        assert info.should_compact
        assert info.tokens_until_compact == 0

        # Over the limit
        info = manager.analyze(250_000)
        assert info.percentage_used == 125.0
        assert info.tokens_remaining == 0  # Can't be negative
        assert info.should_compact

    def test_real_world_scenario(self, manager):
        """Test with real-world token counts from production."""
        # From earlier test: 19,899 tokens (actual production data)
        info = manager.analyze(19_899)

        assert info.percentage_used == pytest.approx(9.95, 0.01)
        assert info.status == ContextStatus.GREEN
        assert info.tokens_until_compact == 160_101
        assert info.percentage_until_compact == pytest.approx(80.05, 0.01)
        assert not info.should_compact
        assert not info.needs_attention


class TestIntegrationWithSession:
    """Test integration with SessionAnalyzer."""

    def test_session_banner_includes_compact_info(self):
        """Session banner should show percentage until compact."""
        from claude_parser.domain.services.session_analyzer import (
            SessionAnalyzer,
            SessionStats,
        )

        analyzer = SessionAnalyzer()
        stats = SessionStats(
            total_tokens=150_000,
            context_limit=200_000,
            input_tokens=140_000,
            output_tokens=10_000,
            cache_hit_rate=0.85,
            cost_usd=1.23,
        )

        banner = analyzer.format_session_banner(stats)

        # Should include compact percentage
        assert "15% until compact" in banner
        assert "🟠" in banner  # Orange emoji at 75%
        assert "75% used" in banner
