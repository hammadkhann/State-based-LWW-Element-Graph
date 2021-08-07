"""
This module contains the (Last-Write-Wins)LWW-element-graph class from (Conflict-free Replicated Data Types) CRDT
"""
import time
import logging

logging.basicConfig(format='%(filename)s - %(levelname)s - %(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)


class LWW_Element_Graph:
    """
    Private class for the LWW element Graph
    """

    add_vertex_set = None
    add_edge_set = None
    remove_vertex_set = None
    remove_edge_set = None

    def __init__(self, adjacency_list):
        self.add_vertex_set = {}
        self.remove_vertex_set = {}
        self.add_edge_set = {}
        self.remove_edge_set = {}
        self.adjacency_list = adjacency_list

    def __str__(self):
        """
        :return: string -- returns adjacency list as a string.
        """
        string = ''
        for j in self.adjacency_list:
            string += str(j) + ':\t' + str(self.adjacency_list[j]) + '\n'
        return string

    def check_edge_exists(self, edge) -> bool:
        """
        Checks if edge already exists in the graph.
        :param edge: integer
        :return: boolean
        """
        if self.check_vertex_exists(edge[0]) and self.check_vertex_exists(edge[1]):
            if edge not in self.add_edge_set:
                # Element not in add_set
                return False
            elif edge not in self.remove_edge_set:
                # Element in add_set and not in remove_set
                return True
            elif self.remove_edge_set[edge] <= self.add_edge_set[edge]:
                # Element in both add_set and remove_set, but addition is after removal
                return True
            else:
                return False
        else:
            # Element in both add_set and remove_set, but addition is before removal
            return False

    def check_vertex_exists(self, vertex) -> bool:
        """
        Checks if vertex exists in the graph.
        :param vertex: integer
        :return: boolean
        """
        if vertex not in self.add_vertex_set:
            # Element not in add_set
            return False
        elif vertex not in self.remove_vertex_set:
            # Element in add_set and not in remove_set
            return True
        elif self.remove_vertex_set[vertex] < self.add_vertex_set[vertex]:
            # Element in both add_set and remove_set, but addition is after removal
            return True
        elif self.remove_vertex_set[vertex] == self.add_vertex_set[vertex]:
            # Element in both add_set and remove_set, but addition is equal to removal biased towards add
            return True
        else:
            # Element in both add_set and remove_set, but addition is before removal
            return False

    def add_vertex(self, vertex, timestamp):
        """
        Add vertex in the LWW-graph with the given timestamp.
        :param vertex: integer
        :param timestamp: string
        :return: True if success else False
        """
        try:
            current_timestamp = time.time()
            if self.check_vertex_exists(vertex):
                logging.info("vertex already exists")
                return False
            else:
                if vertex in self.remove_vertex_set:
                    if self.remove_vertex_set[vertex] <= timestamp:
                        if timestamp < current_timestamp:
                            timestamp = current_timestamp
                        self.add_vertex_set[vertex] = timestamp
                        self.adjacency_list[vertex] = []
                        return True
                else:
                    if timestamp < current_timestamp:
                        timestamp = current_timestamp
                    self.add_vertex_set[vertex] = timestamp
                    self.adjacency_list[vertex] = []
                    return True
        except TypeError as error:
            logging.error(str(error))

    def add_edge(self, pair_tuple, timestamp):
        """
        Add edge in the graph with the given timestamp.
        :param pair_tuple: tuple of vertex in between new edge will be added
        :param timestamp: timestamp of adding new edge
        :return: True if success else False
        """
        try:
            if self.check_vertex_exists(pair_tuple[0]) and self.check_vertex_exists(pair_tuple[1]):
                if not self.check_edge_exists(pair_tuple):
                    if pair_tuple in self.add_edge_set:
                        self.add_edge_set[pair_tuple] = timestamp
                        self.adjacency_list[pair_tuple[0]].append(pair_tuple[1])
                        self.adjacency_list[pair_tuple[1]].append(pair_tuple[0])
                        logging.info("edge added successfully.")
                        return True
                    else:
                        self.add_edge_set[pair_tuple] = timestamp
                        self.adjacency_list[pair_tuple[0]].append(pair_tuple[1])
                        self.adjacency_list[pair_tuple[1]].append(pair_tuple[0])
                        logging.info("edge added successfully.")
                        return True
                else:
                    logging.info("edge already exists.")
                    return False
            else:
                logging.info("invalid vertices.")
                return False
        except TypeError as error:
            logging.error(str(error))

    def remove_vertex(self, vertex, timestamp):
        """
        Removes vertex from the graph by following LWW methodology.
        This function is biased towards add operation.
        :param vertex: integer value of vertex.
        :param timestamp: timestamp of vertex removal from the graph.
        :return: True if success else False.
        """
        try:
            if self.check_vertex_exists(vertex):
                if vertex in self.remove_vertex_set:
                    if self.remove_vertex_set[vertex] < timestamp:
                        self.remove_vertex_set[vertex] = timestamp
                else:
                    self.remove_vertex_set[vertex] = timestamp
                if self.remove_vertex_set[vertex] > self.add_vertex_set[vertex]:
                    for j in self.adjacency_list:
                        if vertex in self.adjacency_list[j]:
                            self.adjacency_list[j].remove(vertex)
                    self.adjacency_list.pop(vertex)
                    logging.info("vertex removed successfully.")
                    return True
                else:
                    self.remove_vertex_set[vertex] = timestamp
                    logging.info("biased towards add.")
                    return False
            else:
                if vertex in self.remove_vertex_set:
                    if self.remove_vertex_set[vertex] < timestamp:
                        self.remove_vertex_set[vertex] = timestamp
                else:
                    self.remove_vertex_set[vertex] = timestamp
                logging.info("vertex does not exists.")
                return False
        except TypeError as error:
            logging.error(str(error))

    def remove_edge(self, edge, timestamp):
        """
        Removes edge from the graph by following LWW methodology.
        This function is biased towards add operation.
        :param edge:
        :param timestamp: timestamp of edge removal from the graph.
        :return: True if success else False.
        """
        try:
            if self.check_edge_exists(edge):
                if edge in self.remove_edge_set:
                    if self.remove_edge_set[edge] < timestamp:
                        self.remove_edge_set[edge] = timestamp
                else:
                    self.remove_edge_set[edge] = timestamp
                if self.remove_edge_set[edge] > self.add_edge_set[edge]:
                    self.adjacency_list[edge[0]].remove(edge[1])
                    self.adjacency_list[edge[1]].remove(edge[0])
                    logging.info("edge removed successfully.")
                    return True
                else:
                    logging.info('biased towards add.')
                    return False
            else:
                if edge in self.remove_edge_set:
                    if self.remove_edge_set[edge] < timestamp:
                        self.remove_edge_set[edge] = timestamp
                else:
                    self.remove_edge_set[edge] = timestamp
                logging.info("edge doesnt exist")
                return False
        except TypeError as error:
            logging.error(str(error))

    def get_vertices(self) -> list:
        """
        This method returns the list of vertices present in the graph.
        Biased towards add operation
        :return: list of vertices.
        """
        try:
            vertices = []
            for vertex in self.add_vertex_set:
                if (vertex not in self.remove_vertex_set) or \
                        (self.add_vertex_set[vertex] >= self.remove_vertex_set[vertex]):
                    vertices.append(vertex)
            return vertices
        except TypeError as error:
            logging.error(str(error))

    def query_vertices(self, vertex):
        """
        This method queries the graph and return all vertices of the given vertex.
        :param vertex: integer value of vertex.
        :return: all the vertices of the vertex if valid vertex is passed else None.
        """
        try:
            if self.check_vertex_exists(vertex):
                return self.adjacency_list[vertex]
            return None
        except TypeError as error:
            logging.error(str(error))

    def find_path(self, start, end, path=None):
        """
        This method finds the path between two vertexes of the graph.
        :param start: start vertex.
        :param end: end vertex.
        :param path: path list.
        :return: path between two vertices if it is found else None.
        """
        try:
            if path is None:
                path = []
            if self.check_vertex_exists(start) and self.check_vertex_exists(end):
                path = path + [start]
                if start == end:
                    return path
                if start not in self.adjacency_list:
                    return None
                for node in self.adjacency_list[start]:
                    if node not in path:
                        new_path = self.find_path(node, end, path)
                        if new_path:
                            return new_path
                return None
            return None
        except TypeError as error:
            logging.error(str(error))

    def merge(self, lww_element_graph):
        """
        This method merges the given graph with current graph.
        For merging within a (add/remove) set, preference is given to latest timestamp
        :param lww_element_graph {LWWElementGraph} -- set to merge with current graph.
        :return: merged [LWWElementGraph]
        """
        try:
            self.merge_sets(self.add_vertex_set, lww_element_graph.add_vertex_set)
            self.merge_sets(self.remove_vertex_set, lww_element_graph.remove_vertex_set)
            self.merge_sets(self.add_edge_set, lww_element_graph.add_edge_set)
            self.merge_sets(self.remove_edge_set, lww_element_graph.remove_edge_set)
            self.merge_sets(self.adjacency_list, lww_element_graph.adjacency_list)
            return self
        except TypeError as error:
            logging.error(str(error))

    @staticmethod
    def merge_sets(first, second):
        """
        This method merges two sets.
        :param first:
        :param second:
        :return: merged set.
        """
        try:
            for key in second:
                if key not in first:
                    first[key] = second[key]
                else:
                    if second[key] > first[key]:
                        first[key] = second[key]
        except TypeError as error:
            logging.error(str(error))

