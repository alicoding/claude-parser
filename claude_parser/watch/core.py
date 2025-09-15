"""
Watch Module - 100% Framework Delegation
"""
from watchfiles import watch as watchfiles_watch
from ..main import load_session


def watch(file_path, on_assistant=None, callback=None):
    """100% watchfiles + DIP: Watch file, emit assistant events"""
    for changes in watchfiles_watch(file_path):
        session = load_session(file_path)  # DIP: use existing interface
        if session and session.messages:
            # Check for assistant messages using new public API
            assistant_messages = list(session.filter_by_type('assistant'))
            if assistant_messages and on_assistant:
                on_assistant(session.get_latest_message())  # Use public navigation API
            if callback:
                callback(session)