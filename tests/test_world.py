import unittest
from game.world import GridMap, Projection

class WorldTests(unittest.TestCase):
    def test_bounds_and_obstacles(self):
        grid = GridMap(4, 3, {(1, 1)})
        self.assertTrue(grid.walkable((0, 0)))
        for cell in [(-1, 0), (4, 0), (0, 3), (1, 1)]:
            self.assertFalse(grid.walkable(cell))

    def test_projection_roundtrip_camera_negative_and_center(self):
        p = Projection(64, 32, (300, 40), (15, -12))
        self.assertEqual(p.project(0, 0), (285, 52))
        for cell in [(0, 0), (23, 15), (-2, -3)]:
            self.assertEqual(p.pick(*p.center(cell)), cell)
            self.assertEqual(p.inverse(*p.project(*cell)), cell)
        self.assertEqual(p.pick(*p.project(-.01, 0)), (-1, 0))

    def test_bfs_stable_four_neighbors_and_hostile_goal(self):
        grid = GridMap(5, 5, {(2, 1)})
        self.assertEqual(grid.neighbors((2, 2)), [(3, 2), (2, 3), (1, 2)])
        self.assertEqual(grid.find_path((1, 1), (3, 1)), [(1, 0), (2, 0), (3, 0), (3, 1)])
        self.assertEqual(grid.find_path((0, 0), (1, 0), {(1, 0)}), [])
        self.assertEqual(grid.find_path((0, 0), (1, 0), {(1, 0)}, True), [(1, 0)])
        self.assertEqual(grid.find_path((0, 0), (-1, 0)), [])
        self.assertEqual(grid.find_path((0, 0), (0, 0)), [])
