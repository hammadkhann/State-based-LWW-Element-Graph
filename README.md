## What even is a CRDT?

Conflict-Free Replicated Data Types (CRDTs) are data structures that power real-time collaborative applications in
distributed systems. CRDTs can be replicated across systems, they can be updated independently and concurrently
without coordination between the replicas, and it is always mathematically possible to resolve inconsistencies that
might result.

## LWW-Element-Set (Last-Writer-Wins-Element-Set):

> LLW Element Set is a kind of Conflict-free replicated data type (abv. CRDT). It allows multiple copies to finally sync up and agree with each other at the end. LWW-Element-Set is similar to 2P-Set in that it consists of an "add set" and a "remove set", with a timestamp for each element. Elements are added to an LWW-Element-Set by inserting the element into the add set, with a timestamp. 

> Elements are removed from the LWW-Element-Set by being added to the remove set, again with a timestamp. An element is a member of the LWW-Element-Set if it is in the add set, and either not in the remove set, or in the remove set but with an earlier timestamp than the latest timestamp in the add set. 

> Merging two replicas of the LWW-Element-Set consists of taking the union of the add sets and the union of the remove sets. When timestamps are equal, the "bias" of the LWW-Element-Set comes into play. A LWW-Element-Set can be biased towards adds or removals. The advantage of LWW-Element-Set over 2P-Set is that, unlike 2P-Set, LWW-Element-Set allows an element to be reinserted after having been removed.

Most implementations are either a) state based or b) operation based. These create two forms of CRDT: Convergent Replicated Data-Types, as in state-based replication; and Commutative Replicated Data-Types, as in ops-based replication.

#### State-based CRDT:

 - Have a partial order to the values.
 - "Monotonically increase" in state, meaning a new state only ever succeeds the current state in the value's ordering.
 - Define a merge function ("least upper bound") which is idempotent and order-independent.

#### Operation based CRDT:

 - Have a partial order to the operations.
 - Have a reliable broadcast channel which guarantees that operations are delivered in the partial order.
 - Define the operation such that concurrent ops commute, meaning they can yield a predictable result without clear precedence.

With these semantics, updates from nodes can converge deterministically.

#### Relation between the two approaches

> State-based mechanisms (CvRDTs) are simple to reason about, since all necessary information is captured by the state. They require weak channel assumptions, allowing for unknown numbers of replicas. However, sending state may be inefficient for large objects; this can be tackled by shipping deltas, but this requires mechanisms similar to the op-based approach. Historically, the state-based approach is used in file systems such as NFS, AFS, Coda, and in key-value stores such as Dynamo and Riak.

> Specifying operation-based objects (CmRDTs) can be more complex since it requires reasoning about history, but conversely they have greater expressive power. The payload can be simpler since some state is effectively offloaded to the channel. Op-based replication is more demanding of the channel, since it requires reliable broadcast, which in general requires tracking group membership. Historically, op-based approaches have been used in cooperative systems such as Bayou, Rover, IceCube, Telex.

## LWW-Element-Graph

#### Graph

> In computer science, a graph is an abstract data type that is meant to implement the undirected graph and directed graph concepts from the field of graph theory within mathematics. A graph data structure consists of a finite (and possibly mutable) set of vertices (also called nodes or points), together with a set of unordered pairs of these vertices for an undirected graph or a set of ordered pairs for a directed graph. These pairs are known as edges (also called links or lines), and for a directed graph are also known as edges but also sometimes arrows or arcs. The vertices may be part of the graph structure, or may be external entities represented by integer indices or references.

LWW Element Graph is an algorithm under Conflict-free replicated data type(CRDT) and generalisation of LWW-element-set, this is the Python implementation.

This repository implements state based LWW-Element-Graph CRDT in python.

#### Methods (check the code for more details)

* `add_vertex` : Add vertex in the graph with the given timestamp.
* `add_edge` : Add edge in the graph with the given timestamp.
* `remove_vertex` : Removes vertex from the graph by following LWW methodology. This function is biased towards add operation.
* `remove_edge` : Removes edge from the graph by following LWW methodology. This function is biased towards add operation.
* `merge` : This method merges the given graph with current graph. For merging within a (add/remove) set, preference is given to latest timestamp
* `get_vertices` :  This method returns the list of vertices present in the graph.
* `find_path` : This method finds the path between two vertexes of the graph.
* `query_vertices` : This method queries the graph and return all vertices of the given vertex.
* `check_vertex_exists` : Checks if vertex exists in the graph.
* `check_edge_exists` : Checks if edge already exists in the graph.

### Testing

Implemented unit-tests to test the CRDT operations of LWW-Element-Graph.

#### Test for Idempotence
It is required that duplication or re-delivery of operations does not affect the final result.
The following tests attempt to repeat the "add_vertex" / "remove_vertex" operations with different timestamps.

A = add_vertex_set, R = remove_vertex_set

Test cases name :

- test_for_vertex_add_operation_idempotence
- test_for_vertex_remove_operation_idempotence

| Original state | Operation       | Resulting state | Final result |
|----------------|-----------------|-----------------|--------------|
| A(a,1) R()     | add(1,time)     | A(1,time+1) R() | [1]          |
| A(a,1) R()     | add(1,time+1)   | A(1,time+1) R() | [1]          |
| A(a,1) R()     | add(1,time+2)   | A(1,time+2) R() | [1]          |
| A() R(1,time+1)| remove(1,time-1)| A() R(1,time+1) | [ ]          |
| A() R(1,time+1)| remove(1,time+1)| A() R(1,time+1) | [ ]          |
| A() R(1,time+1)| remove(1,time+2)| A() R(1,time+2) | [ ]          |

#### Test for Commutativity
It is required that the order of operations does not affect the final result.
The following tests attempt to reverse the order of "add" and "remove" operations with different timestamps.

Test cases name :

- test_for_vertex_commutativity

| Original state  |  Operation       | Resulting state        | Final result|
|-----------------|------------------|------------------------|-------------|
| A(1,time+1) R() | remove(1,time+1) | A(1,time+1) R(1,time+1)| [1]         |
| A() R(1,time+1) | add(1,time+1)    | A(1,time+1) R(1,time+1)| [1]         |
| A(1,time+1) R() | remove(1,time+0) | A(1,time+1) R(1,time-1)| [1]         |
| A() R(1,time-1) | add(1,time+1)    | A(1,time+1) R(1,time-1)| [1]         |
| A(1,time+1) R() | remove(1,time+2) | A(1,time+1) R(1,time+2)| [ ]         |
| A() R(1,time+2) | add(1,time+1)    | A(1,time+1) R(1,time+2)| [ ]         |

#### Test for Associativity
It is required that the grouping of operations does not affect the final result.
In fact, proving full commutativity is sufficient for proving associativity, since grouping
in this context refers to re-ordering certain operations. The resulting state is just
a collection of all element operations.

Rest of the test cases can be found in `lww_element_graph_test.py` file, each test case is explained.

### To run the tests:

Follow these steps to run the code in **local environment**:

 1. Ensure python 3.5+ is installed
 2. Open terminal
 3. Go to project root directory
 4. Run command `pip install requirements.txt`
 5. Run command `sh run.sh` on linux or `bash run.sh` on windows
 6. Watch the magic.

### Limitations

- This implementation can only handle hashable types.
- Garbage collection : elements should be removed from the sets from time to time when they are no longer useful. In fact, only the most-recent operation (add/remove) is needed.
- Add more test cases.

### References
- https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type#LWW-Element-Set_(Last-Write-Wins-Element-Set)
- https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type
- https://github.com/pfrazee/crdt_notes
- https://hal.inria.fr/inria-00555588/PDF/techreport.pdf
- https://www.serverless.com/blog/crdt-explained-supercharge-serverless-at-edge
- https://github.com/ChloeLo27/LLW-Element-Set
- https://bartoszsypytkowski.com/the-state-of-a-state-based-crdts/
- https://github.com/graysonhyc/lww_elements_set_py/blob/master/README.md
