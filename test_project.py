"""Tests for snake game"""
import project
import pygame

# Changing these will break the test.
project.CELL_NUMBER = 10
project.CELL = 10
project.AREA = project.CELL * project.CELL_NUMBER
total_cell_number = project.CELL_NUMBER * (project.CELL_NUMBER - 1)

project.START_SPEED = 150
project.SPEED_INTERVAL = 1
project.SPEED_LIMIT = 50


def test_randomize():
    project.random.seed(9)
    parts = [project.randomize([])]
    # Test that it gives correct Rect
    assert parts[0] == pygame.Rect(70, 50, 10, 10)
    # Test that it will not appear in occupied cell
    project.random.seed(9)
    assert project.randomize(parts) != pygame.Rect(70, 50, 10, 10)
    # Test so that every cell can be populated with unique Rectangles.
    parts.clear()
    [parts.append(project.randomize(parts)) for _ in range(total_cell_number)]
    unique_parts = {(part.x, part.y) for part in parts}
    assert len(unique_parts) == total_cell_number


def test_speed():
    assert project.speed(0) == 150
    assert project.speed(90) == 60
    assert project.speed(200) == 50


def test_warp_on_borders():
    assert project.warp_on_borders(0, 0) == (0, 0)
    assert project.warp_on_borders(100, 0) == (0, 0)
    assert project.warp_on_borders(0, 90) == (0, 0)
    assert project.warp_on_borders(0, 80) == (0, 80)
    assert project.warp_on_borders(0, -10) == (0, 80)
    assert project.warp_on_borders(-10, 0) == (90, 0)
