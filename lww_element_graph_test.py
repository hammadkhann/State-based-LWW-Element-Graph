import unittest
from lww_element_graph import LWW_Element_Graph
import time


class Test_LWW_Element_Graph(unittest.TestCase):

    def test_for_vertex_add_operation_idempotence(self):
        """
        This method tests idempotence of CRDT for vertex addition in the graph.
        This test case is also explained in the table in readme.md file.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        self.assertFalse(graph.add_vertex(1, current_timestamp - 1))
        self.assertFalse(graph.add_vertex(1, current_timestamp + 1))
        self.assertFalse(graph.add_vertex(1, current_timestamp + 2))
        expected_arr: list = [1]
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_for_vertex_remove_operation_idempotence(self):
        """
        This method tests idempotence of CRDT for vertex removal from the graph.
        This test case is also explained in the table in readme.md file.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.remove_vertex(1, current_timestamp)
        self.assertFalse(graph.remove_vertex(1, current_timestamp - 1))
        self.assertFalse(graph.remove_vertex(1, current_timestamp + 1))
        self.assertFalse(graph.remove_vertex(1, current_timestamp + 2))
        expected_arr: list = []
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_for_vertex_commutativity(self):
        """
        This method tests commutativity of CRDT with vertex addition and removal
        using different timestamps this test case is also explained in the table
        in readme.md file.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.remove_vertex(1, current_timestamp)
        expected_arr: list = [1]
        self.assertEqual(graph.get_vertices(), expected_arr)
        graph = LWW_Element_Graph({})
        graph.remove_vertex(1, current_timestamp)
        graph.add_vertex(1, current_timestamp)
        expected_arr: list = [1]
        self.assertEqual(graph.get_vertices(), expected_arr)
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp + 1)
        graph.remove_vertex(1, current_timestamp-1)
        expected_arr: list = [1]
        self.assertEqual(graph.get_vertices(), expected_arr)
        graph = LWW_Element_Graph({})
        graph.remove_vertex(1, current_timestamp-1)
        graph.add_vertex(1, current_timestamp+1)
        expected_arr: list = [1]
        self.assertEqual(graph.get_vertices(), expected_arr)
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp+1)
        graph.remove_vertex(1, current_timestamp+2)
        expected_arr: list = []
        self.assertEqual(graph.get_vertices(), expected_arr)
        graph = LWW_Element_Graph({})
        graph.remove_vertex(1, current_timestamp + 2)
        graph.add_vertex(1, current_timestamp + 1)
        expected_arr: list = []
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_add_remove_vertex(self):
        """
        This method tests add and remove operation of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        self.assertFalse(graph.check_vertex_exists(2))
        graph.add_vertex(2, current_timestamp)
        graph.remove_vertex(1, current_timestamp + 10)
        self.assertTrue(graph.check_vertex_exists(2))
        self.assertFalse(graph.check_vertex_exists(1))
        expected_arr: list = [2]
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_add_remove_edge(self):
        """
        This method tests add and remove operation of edge in the graph.
        """
        graph = LWW_Element_Graph({})
        current_timestamp = time.time()
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp + 10)
        graph.add_vertex(3, current_timestamp + 20)
        graph.add_edge((2, 3), current_timestamp)
        self.assertTrue(graph.check_edge_exists((2, 3)))
        graph.remove_edge((2, 3), current_timestamp + 10)
        self.assertFalse(graph.check_edge_exists((2, 3)))

    def test_merge_lww_graph(self):
        """
        This method tests merge operation of two lww element graphs.
        """
        graph_a = LWW_Element_Graph({})
        graph_b = LWW_Element_Graph({})
        graph_a.add_vertex(6, time.time())
        graph_a.add_vertex(2, time.time())
        graph_a.add_vertex(3, time.time())
        graph_a.add_edge((3, 2), time.time())
        graph_b.add_vertex(1, time.time())
        graph_b.add_vertex(0, time.time())
        graph_b.add_vertex(3, time.time())
        graph_b.add_edge((3, 0), time.time())
        merged = graph_a.merge(graph_b)
        assert {0, 1, 2, 3, 6}.issubset(merged.add_vertex_set.keys())
        assert {(3, 2), (3, 0)}.issubset(merged.add_edge_set.keys())

    def test_add_remove_add_vertex(self):
        """
        This method tests add->remove->add operations of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        graph.remove_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        graph.remove_vertex(1, current_timestamp + 100)
        self.assertFalse(graph.check_vertex_exists(1))
        graph.add_vertex(1, current_timestamp + 120)
        self.assertTrue(graph.check_vertex_exists(1))

    def test_remove_add_vertex(self):
        """
        This method tests remove->add operations of vertex in the graph.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        self.assertFalse(graph.remove_vertex(1, current_timestamp))
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))

    def test_add_edge_remove_vertex_bias(self):
        """
        This method tests concurrent operations of add_edge & remove_vertex
        this is a deadlock so my implementation is biased towards remove vertex.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp + 10)
        graph.remove_vertex(2, current_timestamp + 10)
        self.assertTrue(graph.check_vertex_exists(1))
        self.assertFalse(graph.check_edge_exists((1, 2)))

    def test_add_remove_add_edge(self):
        """
        This method tests add->remove->edge operations on edge in the graph.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        self.assertTrue(graph.check_edge_exists((1, 2)))
        graph.remove_edge((1, 2), current_timestamp)
        self.assertTrue(graph.check_edge_exists((1, 2)))
        graph.remove_edge((1, 2), current_timestamp + 100)
        self.assertFalse(graph.check_edge_exists((1, 2)))
        graph.add_edge((1, 2), current_timestamp + 100)
        self.assertTrue(graph.check_edge_exists((1, 2)))

    def test_remove_vertex_twice_in_reverse_order(self):
        """
        This method tests applying remove operation twice on vertex
        in reverse order of timestamps means first bigger timestamp then small.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        graph.remove_vertex(1, current_timestamp + 10)
        self.assertFalse(graph.check_vertex_exists(1))
        graph.remove_vertex(1, current_timestamp)
        self.assertFalse(graph.check_vertex_exists(1))
        expected_arr: list = []
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_check_vertex_exists(self):
        """
        This method tests check_vertex_exists method of the graph.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(1))
        self.assertFalse(graph.check_vertex_exists(2))
        graph.add_vertex(2, current_timestamp)
        self.assertTrue(graph.check_vertex_exists(2))
        expected_arr: list = [1, 2]
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_query_vertices(self):
        """
        This method tests query_vertices method of the graph.
        It will check whether the return vertices are correct or not for a given vertex.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        graph.add_edge((3, 1), current_timestamp)
        graph.add_edge((3, 2), current_timestamp)
        expected_arr: list = [2, 3]
        self.assertEqual(graph.query_vertices(1), expected_arr)
        expected_arr: list = [1, 3]
        self.assertEqual(graph.query_vertices(2), expected_arr)
        expected_arr: list = [1, 2]
        self.assertEqual(graph.query_vertices(3), expected_arr)

    def test_find_path(self):
        """
        This method will test the find_path function of the graph in which
        we are finding path between two vertices.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_vertex(3, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        graph.add_edge((3, 2), current_timestamp)
        expected_arr: list = [1, 2, 3]
        self.assertEqual(graph.find_path(1, 3), expected_arr)
        expected_arr: list = [1, 2]
        self.assertEqual(graph.find_path(1, 2), expected_arr)

    def test_empty_lookup(self):
        """
        This method checks empty lookup of the graph.
        """
        graph = LWW_Element_Graph({})
        expected_arr: list = []
        self.assertEqual(graph.get_vertices(), expected_arr)

    def test_vertex_already_exists(self):
        """
        This method tests if we add already existing
        vertex again in the graph is it added or not.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        self.assertEqual(graph.add_vertex(1, current_timestamp + 10), False)

    def test_edge_already_exists(self):
        """
        This method tests if we add already existing
        EDGE again in the graph is it added or not.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        graph.add_vertex(1, current_timestamp)
        graph.add_vertex(2, current_timestamp)
        graph.add_edge((1, 2), current_timestamp)
        self.assertEqual(graph.add_edge((1, 2), current_timestamp + 10), False)

    def test_add_vertex_exception(self):
        """
        This method tests the exception handling of unhashable type
        in add_vertex function.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        self.assertEqual(graph.add_vertex([1, 2, 3], current_timestamp), None)

    def test_remove_vertex_exception(self):
        """
        This method tests the exception handling of unhashable type
        in remove_vertex function.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        self.assertEqual(graph.remove_vertex([1, 2, 3], current_timestamp), None)

    def test_add_edge_exception(self):
        """
        This method tests the exception handling of unhashable type
        in add_edge function.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        self.assertEqual(graph.add_edge([1, 2, 3], current_timestamp), False)

    def test_remove_edge_exception(self):
        """
        This method tests the exception handling of unhashable type
        in remove_edge function.
        """
        current_timestamp = time.time()
        graph = LWW_Element_Graph({})
        self.assertEqual(graph.remove_edge([1, 2, 3], current_timestamp), None)


if __name__ == '__main__':
    unittest.main(verbosity=2)
