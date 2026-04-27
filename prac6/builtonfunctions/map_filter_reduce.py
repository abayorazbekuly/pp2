from functools import reduce

nums = [1, 2, 3, 4, 5]

# map
squared = list(map(lambda x: x*x, nums))
print("Squared:", squared)

# filter
even = list(filter(lambda x: x % 2 == 0, nums))
print("Even:", even)

# reduce
total = reduce(lambda a, b: a + b, nums)
print("Sum:", total)