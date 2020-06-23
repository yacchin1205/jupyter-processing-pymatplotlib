from unittest.mock import Mock
import matplotlib.patches as patches
from processingpymat import drawing

def test_rect_buffer_with_stroke():
    axmock = Mock()
    cache = drawing.PatchCache(axmock)
    cache.begin()
    cache.add_rect(10, 20, 10, 10, {'linewidth': 1})
    cache.add_rect(10, 30, 10, 10, {'linewidth': 1})
    cache.flush()
    axmock.add_patch.assert_called()
    assert len(axmock.add_patch.call_args_list) == 2
    assert type(axmock.add_patch.call_args_list[0].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[0].args[0].get_x() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[0].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_height() == 10
    assert type(axmock.add_patch.call_args_list[1].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[1].args[0].get_x() == 10
    assert axmock.add_patch.call_args_list[1].args[0].get_y() == 30
    assert axmock.add_patch.call_args_list[1].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[1].args[0].get_height() == 10

def test_2rects_buffer_without_stroke():
    axmock = Mock()
    cache = drawing.PatchCache(axmock)
    cache.begin()
    cache.add_rect(10, 20, 10, 10, {'linewidth': 0})
    cache.add_rect(10, 30, 10, 10, {'linewidth': 0})
    cache.flush()
    axmock.add_patch.assert_called()
    assert len(axmock.add_patch.call_args_list) == 1
    assert type(axmock.add_patch.call_args.args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[0].args[0].get_x() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[0].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_height() == 20

def test_3rects_buffer_without_stroke_1():
    axmock = Mock()
    cache = drawing.PatchCache(axmock)
    cache.begin()
    cache.add_rect(10, 20, 10, 10, {'linewidth': 0})
    cache.add_rect(10, 30, 10, 10, {'linewidth': 0})
    cache.add_rect(20, 20, 10, 10, {'linewidth': 0})
    cache.flush()
    axmock.add_patch.assert_called()
    assert len(axmock.add_patch.call_args_list) == 2
    assert type(axmock.add_patch.call_args_list[0].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[0].args[0].get_x() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[0].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_height() == 20
    assert type(axmock.add_patch.call_args_list[1].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[1].args[0].get_x() == 20
    assert axmock.add_patch.call_args_list[1].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[1].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[1].args[0].get_height() == 10

def test_3rects_buffer_without_stroke_2():
    axmock = Mock()
    cache = drawing.PatchCache(axmock)
    cache.begin()
    cache.add_rect(10, 20, 10, 10, {'linewidth': 0})
    cache.add_rect(10, 30, 10, 10, {'linewidth': 0})
    cache.add_rect(21, 20, 10, 10, {'linewidth': 0})
    cache.flush()
    axmock.add_patch.assert_called()
    assert len(axmock.add_patch.call_args_list) == 2
    assert type(axmock.add_patch.call_args_list[0].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[0].args[0].get_x() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[0].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[0].args[0].get_height() == 20
    assert type(axmock.add_patch.call_args_list[1].args[0]) == patches.Rectangle
    assert axmock.add_patch.call_args_list[1].args[0].get_x() == 21
    assert axmock.add_patch.call_args_list[1].args[0].get_y() == 20
    assert axmock.add_patch.call_args_list[1].args[0].get_width() == 10
    assert axmock.add_patch.call_args_list[1].args[0].get_height() == 10
