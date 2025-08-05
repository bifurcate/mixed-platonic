import pytest
import time

from bracelets import (
  generate_2_bracelets,
  foo,
)

# def test_generate_bracelets():
  
#   start_time1 = time.perf_counter()
#   X = [(i, len(list(generate_2_bracelets(6*i)))) for i in range(1,4)]
#   end_time1 = time.perf_counter()

#   total1 = end_time1 - start_time1

#   start_time2 = time.perf_counter()
#   Y = [(i, len(list(foo(6*i)))) for i in range(1,4)]
#   end_time2 = time.perf_counter()
  
#   total2 = end_time2 - start_time2

#   breakpoint()