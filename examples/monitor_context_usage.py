#!/usr/bin/env python3
"""
Example: Monitor Claude Context Usage Programmatically

This demonstrates how to monitor context usage without watching the Claude Code UI.
Perfect for automation, alerts, and workflow integration.

Usage:
    python monitor_context_usage.py /path/to/conversation.jsonl
"""

import sys
from pathlib import Path
from claude_parser import load
from claude_parser.domain.services import ContextWindowManager, SessionAnalyzer


def monitor_context(jsonl_path: str):
    """Monitor context usage for a Claude conversation."""
    
    # Load conversation
    print(f"Loading: {jsonl_path}")
    conv = load(jsonl_path)
    
    # Analyze current session
    analyzer = SessionAnalyzer()
    stats = analyzer.analyze_current_session(conv)
    
    # Get context window status
    context_manager = ContextWindowManager()
    context_info = context_manager.analyze(stats.total_tokens)
    
    # Display comprehensive status
    print("\n" + "="*60)
    print("CLAUDE CONTEXT MONITOR")
    print("="*60)
    
    # Basic info
    print(f"\nConversation: {conv.session_id}")
    print(f"Messages: {len(conv.messages)}")
    print(f"Model: {stats.model}")
    
    # Context usage visualization
    print(f"\n{context_manager.format_cli_status(stats.total_tokens)}")
    
    # Detailed metrics
    print("\n📊 TOKEN BREAKDOWN:")
    print(f"   Input tokens:       {stats.input_tokens:>10,}")
    print(f"   Output tokens:      {stats.output_tokens:>10,}")
    print(f"   Cache read tokens:  {stats.cache_read_tokens:>10,}")
    print(f"   Cache created:      {stats.cache_created_tokens:>10,}")
    print(f"   ─────────────────────────────────")
    print(f"   TOTAL:             {stats.total_tokens:>10,}")
    
    # Financial info
    print(f"\n💰 COST: ${stats.cost_usd:.2f}")
    print(f"   Cache hit rate: {stats.cache_hit_rate:.0%}")
    
    # Alert status
    print(f"\n🚨 ALERT STATUS:")
    if context_info.is_critical:
        print(f"   ⚠️ CRITICAL: {context_info.message}")
    elif context_info.needs_attention:
        print(f"   ⚠️ WARNING: {context_info.message}")
    else:
        print(f"   ✅ {context_info.message}")
    
    # Automation hooks
    print(f"\n🔧 AUTOMATION DATA:")
    print(f"   Status: {context_info.status.value}")
    print(f"   Should alert: {context_manager.should_alert(stats.total_tokens)}")
    print(f"   Should compact: {context_info.should_compact}")
    print(f"   Percent until compact: {context_info.percentage_until_compact:.1f}%")
    print(f"   Tokens until compact: {context_info.tokens_until_compact:,}")
    
    # Webhook example
    if context_info.needs_attention:
        print(f"\n📨 WEBHOOK PAYLOAD (example):")
        webhook = context_manager.get_webhook_payload(stats.total_tokens)
        print(f"   POST https://your-webhook.com/claude-alert")
        print(f"   {webhook}")
    
    print("\n" + "="*60)
    
    # Return status for scripting
    return {
        "needs_attention": context_info.needs_attention,
        "is_critical": context_info.is_critical,
        "should_compact": context_info.should_compact,
        "percentage_used": context_info.percentage_used,
        "percentage_until_compact": context_info.percentage_until_compact
    }


def main():
    """CLI entry point."""
    if len(sys.argv) != 2:
        print("Usage: python monitor_context_usage.py <jsonl_file>")
        sys.exit(1)
    
    jsonl_path = Path(sys.argv[1])
    if not jsonl_path.exists():
        print(f"Error: File not found: {jsonl_path}")
        sys.exit(1)
    
    # Monitor and get status
    status = monitor_context(jsonl_path)
    
    # Exit with appropriate code for automation
    if status["is_critical"]:
        sys.exit(2)  # Critical status
    elif status["needs_attention"]:
        sys.exit(1)  # Warning status
    else:
        sys.exit(0)  # OK status


if __name__ == "__main__":
    main()