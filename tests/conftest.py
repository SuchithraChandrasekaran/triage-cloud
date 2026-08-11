"""
Shared setup for all test files in this folder. Adds event-pipeline/ to
the import path once, so individual test files don't need their own
sys.path.insert lines (which is fragile when combining test files).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "event-pipeline"))
