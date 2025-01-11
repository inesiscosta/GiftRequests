# GiftRequests
A gifts distribution optimizer based on linear programing using PULP and the GLPK solver for our Analysis and Synthesis of Algorithms class.
It determines the number of gift requests made by childern around the world that can be fulfilled this Christmas given constraints in the toy factories.

# Constraints

- Each factory produces a single type of toy and has a maximum stock limit.
- Each country has a minimum number of gifts that must be delivered.
- There are limits on the total exports from the factories in each country.
- Each child can request multiple toys but will receive at most one.

## Usage

### Input:

- The first line contains three integers: the number of factories `n`, the number of countries `m`, and the number of children `t`.

-  The next `n` lines each contain three integers: the factory ID `i`, the country ID `j` where the factory is located, and the maximum stock `f_maxi` of the factory.

- The next `m` lines each contain three integers: the country ID `j`, the maximum export limit `p_maxj`, and the minimum number of gifts `p_minj` to be delivered in that country.

- The next `t` lines each contain the child ID `k`, the country ID `j` where the child lives, and the IDs of the factories from which the child requests toys.

### Example input:

```
3 2 3
1 1 1
2 1 1
3 2 1
1 2 1
2 2 1
1 1 2 3
2 1 2 1
3 2 1
```

### Running the program:

```shell
python main.py < input_file.txt
```

### Running public test using pytest:

```shell
python -m pytest test_public.py
```