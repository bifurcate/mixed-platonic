import itertools


def integrate(L, c):
    A = []
    n = len(L)
    val = c
    for i in range(n):
        A.append(val)
        val = (L[i] + val) % 2

    if val != c:
        print(A)
        raise ValueError("Unorientable String")

    return A


def differentiate(L):
    A = []
    n = len(L)
    for i in range(n):
        val = (L[i] + L[(i + 1) % n]) % 2
        A.append(val)
    return tuple(A)


def get_binary_tuples(n, k):
    """
    Generates all binary tuples of length n with exactly k ones (weight k).

    Args:
        n: The length of the binary tuples
        k: The number of ones (weight) in each tuple

    Returns:
        A list of tuples, each containing a binary tuple with exactly k ones
    """
    import itertools

    if k > n or k < 0:
        return []

    # Generate all combinations of k positions out of n
    tuples = []
    for positions in itertools.combinations(range(n), k):
        # Create a tuple with zeros, then set ones at the chosen positions
        binary_tuple = [0] * n
        for pos in positions:
            binary_tuple[pos] = 1
        tuples.append(tuple(binary_tuple))

    return tuples


def weight(binary_string):
    """
    Computes the weight (number of ones) in a binary string.

    Args:
        binary_string: A binary string, tuple, or list (e.g., "101", [1,0,1], (1,0,1))

    Returns:
        The count of ones in the binary string
    """
    return sum(binary_string)


def foo(x):
    count = 1
    parity = 0
    for i in range(1, len(x)):
        if x[i] == 1:
            parity = (parity + 1) % 2
        if parity == 0:
            count += 1
    return count


def get_vertex_degrees(adj_matrix):
    """
    Computes the degree of each vertex in a graph.

    Args:
        adj_matrix: An adjacency matrix (list of lists) where adj_matrix[i][j]
                    represents the multiplicity of edges between vertices i and j

    Returns:
        A list of degrees, where the index corresponds to the vertex number
    """
    degrees = []
    for row in adj_matrix:
        degrees.append(sum(row))
    return degrees


def get_nonisomorphic_multigraphs(v, e):
    """
    Generates all non-isomorphic loopless multigraphs with v vertices and e edges.

    A multigraph allows multiple edges between distinct vertices.
    This implementation uses graph invariants and permutation checking.

    Args:
        v: The number of vertices
        e: The total number of edges (counting multiplicity)

    Returns:
        A list of adjacency matrices (as lists of lists) representing non-isomorphic multigraphs.
        In the adjacency matrix, each entry is the multiplicity of edges between vertices.
    """
    from itertools import permutations

    # Generate all possible vertex pairs (no self-loops)
    pairs = [(i, j) for i in range(v) for j in range(i + 1, v)]
    num_pairs = len(pairs)

    if e < 0:
        return []

    def distribute_edges(num_edges, num_pairs_left):
        """Generate all ways to distribute num_edges among num_pairs_left pairs."""
        if num_pairs_left == 1:
            yield [num_edges]
        else:
            for i in range(num_edges + 1):
                for rest in distribute_edges(num_edges - i, num_pairs_left - 1):
                    yield [i] + rest

    def multigraph_to_adj_matrix(edge_multiplicities, num_vertices, pairs_list):
        """Convert edge multiplicities to adjacency matrix."""
        adj = [[0] * num_vertices for _ in range(num_vertices)]
        for (u, w), mult in zip(pairs_list, edge_multiplicities):
            adj[u][w] = mult
            adj[w][u] = mult
        return adj

    def get_degree_sequence(adj):
        """Get sorted degree sequence (sum of edge multiplicities)."""
        return tuple(sorted([sum(row) for row in adj]))

    def are_isomorphic(adj1, adj2):
        """Check if two multigraphs are isomorphic."""
        n = len(adj1)

        # Quick check: same degree sequence
        if get_degree_sequence(adj1) != get_degree_sequence(adj2):
            return False

        # For small graphs, try permutations
        if n <= 7:  # Practical limit due to factorial growth
            for perm in permutations(range(n)):
                match = True
                for i in range(n):
                    for j in range(n):
                        if adj1[i][j] != adj2[perm[i]][perm[j]]:
                            match = False
                            break
                    if not match:
                        break
                if match:
                    return True
            return False
        else:
            # For larger graphs, degree sequence is an approximation
            return False

    unique_graphs = []

    # Generate all ways to distribute e edges among the possible pairs
    for edge_multiplicities in distribute_edges(e, num_pairs):
        adj = multigraph_to_adj_matrix(edge_multiplicities, v, pairs)

        # Check if isomorphic to any existing multigraph
        is_new = True
        for existing_adj in unique_graphs:
            if are_isomorphic(adj, existing_adj):
                is_new = False
                break

        if is_new:
            unique_graphs.append(adj)

    return unique_graphs


D = {
    0: (0,),
    1: (3,),
    2: (4, 6),
    3: (3,),
    4: (0,),
}


def get_rank_spectrum(graphs):
    S = set()
    for G in graphs:
        degs = get_vertex_degrees(G)
        r = [D[d] for d in degs]
        X = itertools.product(*r)
        S = S.union([sum(x) for x in X])
    return list(S)


def has_rotational_symmetry(binary_string, n):
    """
    Checks if a binary string has a specific rotational symmetry.

    Args:
        binary_string: A binary string, tuple, or list (e.g., "101", [1,0,1], (1,0,1))
        n: The number of positions to right-shift

    Returns:
        True if the string is equivalent after right-shifting n places, False otherwise
    """
    length = len(binary_string)
    if length == 0:
        return True

    # Normalize n to be within the length
    n = n % length

    if n == 0:
        return True

    # Right shift: move last n elements to the front
    rotated = binary_string[-n:] + binary_string[:-n]

    return rotated == binary_string
