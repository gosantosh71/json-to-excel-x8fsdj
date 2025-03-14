"""
Unit tests for the progress bar component of the CLI interface.
This file contains test cases to verify the functionality of the ProgressBar, 
IndeterminateProgressBar, and ProgressTracker classes, ensuring they correctly 
display and update progress information during JSON to Excel conversion operations.
"""

import pytest  # v: 7.3.0+
import unittest.mock as mock  # v: built-in
import time  # v: built-in

from ../../progress_bar import (
    ProgressBar,
    IndeterminateProgressBar,
    ProgressTracker,
    calculate_eta,
    format_progress_stats
)
from ../../utils.console_utils import update_progress_bar
from ../../utils.time_utils import Timer


class MockTimer:
    """
    A mock implementation of the Timer class for testing purposes.
    """
    
    def __init__(self):
        """
        Initializes a new MockTimer instance.
        """
        self._elapsed = 0.0
        self._started = False
    
    def start(self):
        """
        Simulates starting the timer.
        
        Returns:
            MockTimer: Self reference for method chaining
        """
        self._started = True
        return self
    
    def elapsed(self):
        """
        Returns a predefined elapsed time for testing.
        
        Returns:
            float: Predefined elapsed time
        """
        return self._elapsed
    
    def set_elapsed(self, seconds):
        """
        Sets the elapsed time for testing purposes.
        
        Args:
            seconds (float): The elapsed time to set
        """
        self._elapsed = seconds


def test_progress_bar_initialization():
    """
    Tests that the ProgressBar class initializes with the correct default values.
    """
    progress_bar = ProgressBar(total=100)
    
    assert progress_bar._current == 0.0
    assert not progress_bar.is_active()
    assert progress_bar._total == 100
    assert progress_bar._prefix == "Progress:"
    assert progress_bar._suffix == ""


def test_progress_bar_start():
    """
    Tests that the ProgressBar start method correctly initializes the progress display.
    """
    with mock.patch('src.cli.utils.console_utils.clear_line'), \
         mock.patch('builtins.print') as mock_print:
        progress_bar = ProgressBar(total=100)
        progress_bar.start()
        
        assert progress_bar.is_active()
        mock_print.assert_called_once()
        assert progress_bar._start_time is not None


def test_progress_bar_update():
    """
    Tests that the ProgressBar update method correctly updates the progress display.
    """
    with mock.patch('src.cli.utils.console_utils.clear_line'), \
         mock.patch('builtins.print') as mock_print:
        progress_bar = ProgressBar(total=100)
        progress_bar.start()
        mock_print.reset_mock()  # Clear the call from start()
        
        progress_bar.update(50)
        
        mock_print.assert_called_once()
        assert progress_bar._current == 50


def test_progress_bar_finish():
    """
    Tests that the ProgressBar finish method correctly completes the progress display.
    """
    with mock.patch('src.cli.utils.console_utils.clear_line'), \
         mock.patch('builtins.print') as mock_print:
        progress_bar = ProgressBar(total=100)
        progress_bar.start()
        mock_print.reset_mock()  # Clear the call from start()
        
        progress_bar.finish()
        
        # Two print calls: one for the final progress bar and one for the newline
        assert mock_print.call_count == 2
        assert not progress_bar.is_active()


def test_progress_bar_update_with_suffix():
    """
    Tests that the ProgressBar update method correctly handles suffix updates.
    """
    with mock.patch('src.cli.utils.console_utils.clear_line'), \
         mock.patch('builtins.print'):
        progress_bar = ProgressBar(total=100)
        progress_bar.start()
        
        new_suffix = "Processing file..."
        progress_bar.update(50, suffix=new_suffix)
        
        assert progress_bar._suffix == new_suffix


def test_indeterminate_progress_bar_initialization():
    """
    Tests that the IndeterminateProgressBar class initializes correctly.
    """
    spinner = IndeterminateProgressBar(message="Processing...")
    
    assert spinner._message == "Processing..."
    assert not spinner.is_active()
    assert spinner._frames is not None and len(spinner._frames) > 0


def test_indeterminate_progress_bar_start_stop():
    """
    Tests that the IndeterminateProgressBar start and stop methods work correctly.
    """
    with mock.patch('threading.Thread') as mock_thread:
        instance = mock_thread.return_value
        instance.start.return_value = None
        instance.join.return_value = None
        
        spinner = IndeterminateProgressBar()
        spinner.start()
        
        assert spinner.is_active()
        mock_thread.assert_called_once()
        
        # Mock for clear_line in stop method
        with mock.patch('src.cli.utils.console_utils.clear_line'):
            spinner.stop()
            assert not spinner.is_active()
            assert spinner._stop_event.is_set()


def test_indeterminate_progress_bar_update_message():
    """
    Tests that the IndeterminateProgressBar update_message method correctly updates the message.
    """
    spinner = IndeterminateProgressBar(message="Initial message")
    new_message = "Updated message"
    spinner.update_message(new_message)
    
    assert spinner._message == new_message


def test_progress_tracker_initialization():
    """
    Tests that the ProgressTracker class initializes correctly.
    """
    tracker = ProgressTracker()
    
    assert hasattr(tracker, '_stages')
    assert len(tracker._stages) == 0
    assert tracker._total_weight == 0
    assert tracker._current_stage is None
    assert tracker.get_overall_progress() == 0


def test_progress_tracker_add_stage():
    """
    Tests that the ProgressTracker add_stage method correctly adds a processing stage.
    """
    tracker = ProgressTracker()
    tracker.add_stage("parsing", weight=1)
    
    assert "parsing" in tracker._stages
    assert tracker._stages["parsing"]["progress"] == 0
    assert tracker._stages["parsing"]["weight"] == 1
    assert tracker._total_weight == 1


def test_progress_tracker_start_progress():
    """
    Tests that the ProgressTracker start_progress method correctly initializes the progress bar.
    """
    with mock.patch('src.cli.progress_bar.ProgressBar') as mock_progress_bar:
        instance = mock_progress_bar.return_value
        instance.start.return_value = instance
        
        tracker = ProgressTracker()
        tracker.start_progress()
        
        mock_progress_bar.assert_called_once_with(total=100)
        instance.start.assert_called_once()
        assert tracker.get_overall_progress() == 0


def test_progress_tracker_start_stage():
    """
    Tests that the ProgressTracker start_stage method correctly starts a processing stage.
    """
    tracker = ProgressTracker()
    tracker.add_stage("parsing", weight=1)
    
    # Mock the progress bar for start_progress
    with mock.patch('src.cli.progress_bar.ProgressBar'):
        tracker.start_progress()
        tracker.start_stage("parsing")
        
        assert tracker._current_stage == "parsing"


def test_progress_tracker_update_stage_progress():
    """
    Tests that the ProgressTracker update_stage_progress method correctly updates stage and overall progress.
    """
    with mock.patch('src.cli.progress_bar.ProgressBar') as mock_progress_bar:
        instance = mock_progress_bar.return_value
        instance.start.return_value = instance
        instance.update.return_value = instance
        
        tracker = ProgressTracker()
        
        # Add two stages with different weights
        tracker.add_stage("parsing", weight=1)
        tracker.add_stage("transform", weight=2)
        
        # Start progress and the first stage
        tracker.start_progress()
        tracker.start_stage("parsing")
        
        # Update progress to 50%
        tracker.update_stage_progress(50)
        
        # Check that stage progress was updated
        assert tracker._stages["parsing"]["progress"] == 50
        
        # Check that overall progress was calculated correctly (50% of stage 1 weight is 1/3 of total)
        expected_overall = (50 * 1) / (1 + 2) * 100
        assert abs(tracker.get_overall_progress() - expected_overall) < 0.01
        
        # Check that progress bar was updated with correct percentage
        instance.update.assert_called_with(expected_overall)


def test_progress_tracker_complete_stage():
    """
    Tests that the ProgressTracker complete_stage method correctly marks a stage as complete.
    """
    with mock.patch('src.cli.progress_bar.ProgressBar') as mock_progress_bar:
        instance = mock_progress_bar.return_value
        instance.start.return_value = instance
        instance.update.return_value = instance
        
        tracker = ProgressTracker()
        
        # Add a stage
        tracker.add_stage("parsing", weight=1)
        
        # Start progress and the stage
        tracker.start_progress()
        tracker.start_stage("parsing")
        
        # Complete the stage
        tracker.complete_stage()
        
        # Check that stage progress is set to 100%
        assert tracker._stages["parsing"]["progress"] == 100
        
        # Check that progress bar was updated with correct percentage
        instance.update.assert_called_with(100)


def test_progress_tracker_finish_progress():
    """
    Tests that the ProgressTracker finish_progress method correctly finalizes the progress tracking.
    """
    with mock.patch('src.cli.progress_bar.ProgressBar') as mock_progress_bar:
        instance = mock_progress_bar.return_value
        instance.start.return_value = instance
        instance.finish.return_value = None
        
        tracker = ProgressTracker()
        
        # Start progress tracking
        tracker.start_progress()
        
        # Finish progress
        tracker.finish_progress()
        
        # Check that progress bar was finalized
        instance.finish.assert_called_once()
        
        # Check that state was reset
        assert tracker.get_overall_progress() == 0
        assert tracker._current_stage is None


def test_calculate_eta():
    """
    Tests that the calculate_eta function correctly estimates the remaining time.
    """
    # Test when current is 0
    assert calculate_eta(0, 100, 5.0) is None
    
    # Test when progress is 0
    assert calculate_eta(50, 100, 0.0) is None
    
    # Test normal case: If 50% took 10 seconds, remaining 50% should take 10 more seconds
    assert calculate_eta(50, 100, 10.0) == 10.0
    
    # More complex case
    assert calculate_eta(25, 100, 5.0) == 15.0  # 75% remaining should take 3x the time of 25%


def test_format_progress_stats():
    """
    Tests that the format_progress_stats function correctly formats progress statistics.
    """
    with mock.patch('src.cli.utils.time_utils.format_time') as mock_format_time:
        mock_format_time.side_effect = lambda x: f"{x:.1f}s"
        
        # Test with available ETA
        stats = format_progress_stats(50.0, 10.0, 10.0)
        assert "50.0%" in stats
        assert "10.0s" in stats  # Elapsed time
        assert "ETA: 10.0s" in stats
        
        # Test without ETA
        stats = format_progress_stats(75.0, 15.0, None)
        assert "75.0%" in stats
        assert "15.0s" in stats  # Elapsed time
        assert "calculating" in stats