#!/bin/bash
# Research the best libraries for navigation using the research tool

# Load environment variables from .env file
export $(cat .env | grep -v '^#' | xargs)

python library_research.py -t "Best Python libraries for conversation navigation and message history operations" \
  -q "What is the 95/5 library solution for navigating parent-child relationships in message threads? Compare NetworkX vs pandas vs SQLite for conversation trees" \
  -q "Should I use pandas DataFrame or stay with Python dicts for O(1) UUID lookups in conversation history with 10000+ messages?" \
  -q "What's the best practice for timestamp range queries in conversation data - pandas DatetimeIndex vs bisect vs custom implementation?" \
  -q "Are there specialized libraries for chat/conversation history navigation like langchain ChatMessageHistory that I should use instead of general-purpose tools?" \
  -q "What do production chat applications like Discord, Slack, or WhatsApp use for message history navigation and search?"