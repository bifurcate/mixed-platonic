from base import (
    Sqr,
    Tri,
)

from construction import Cusp

from env import create_env


def build_s913(env_path):
    cusp = Cusp()

    ## COMPONENT 1

    # 0
    cusp.pair(
        Sqr(0),
        (2, 3),
        Sqr(1),
        (1, 4),
    )

    # 1
    cusp.pair(
        Sqr(1),
        (2, 3),
        Tri(1),
        (1, 3),
    )

    # 2
    cusp.pair(
        Tri(1),
        (1, 2),
        Tri(0),
        (1, 3),
    )

    # 3
    cusp.pair(
        Tri(0),
        (2, 3),
        Sqr(0),
        (1, 4),
    )

    # 4
    cusp.pair(
        Sqr(0),
        (3, 4),
        Sqr(2),
        (2, 1),
    )

    # 5
    cusp.pair(
        Sqr(1),
        (3, 4),
        Sqr(3),
        (2, 1),
    )

    # 6
    cusp.pair(
        Tri(1),
        (2, 3),
        Tri(2),
        (2, 1),
    )

    # 7
    cusp.pair(
        Sqr(2),
        (2, 3),
        Sqr(3),
        (1, 4),
    )

    # 8
    cusp.pair(
        Sqr(3),
        (2, 3),
        Tri(3),
        (1, 3),
    )

    # 9
    cusp.pair(
        Tri(3),
        (1, 2),
        Tri(2),
        (1, 3),
    )

    # 10
    cusp.pair(
        Tri(2),
        (2, 3),
        Sqr(2),
        (1, 4),
    )

    # 11
    cusp.pair(
        Sqr(2),
        (3, 4),
        Tri(4),
        (2, 1),
    )

    # 12
    cusp.pair(
        Sqr(3),
        (3, 4),
        Tri(6),
        (2, 1),
    )

    # 13
    cusp.pair(
        Tri(3),
        (2, 3),
        Sqr(4),
        (2, 1),
    )

    # 14
    cusp.pair(
        Tri(4),
        (2, 3),
        Tri(5),
        (2, 1),
    )

    # 15
    cusp.pair(
        Tri(5),
        (2, 3),
        Tri(6),
        (1, 3),
    )

    # 16
    cusp.pair(
        Tri(6),
        (2, 3),
        Tri(7),
        (2, 1),
    )

    # 17
    cusp.pair(
        Tri(7),
        (2, 3),
        Sqr(4),
        (1, 4),
    )

    # 18
    cusp.pair(
        Sqr(4),
        (2, 3),
        Tri(4),
        (1, 3),
    )

    # 19
    cusp.pair(
        Tri(5),
        (1, 3),
        Sqr(0),
        (1, 2),
    )

    # 20
    cusp.pair(
        Tri(7),
        (1, 3),
        Sqr(1),
        (1, 2),
    )

    # 21
    cusp.pair(
        Sqr(4),
        (3, 4),
        Tri(0),
        (2, 1),
    )

    ## COMPONENT 2

    # 22
    cusp.pair(
        Sqr(5),
        (2, 3),
        Sqr(5),
        (1, 4),
    )

    # 23
    cusp.pair(
        Sqr(5),
        (3, 4),
        Sqr(5),
        (2, 1),
    )

    traversal = [
        Sqr(5),
        Sqr(0),
        Sqr(1),
        Tri(1),
        Tri(0),
        Sqr(2),
        Sqr(3),
        Tri(3),
        Tri(2),
        Tri(4),
        Tri(5),
        Tri(6),
        Tri(7),
        Sqr(4),
    ]

    create_env(env_path, 2, 1, cusp, traversal)
