#pylint: skip-file
import sys
import pulp
from pulp import PULP_CBC_CMD

def main():
    data = sys.stdin.read().splitlines()
    
    n, m, t = map(int, data[0].split()) # n - num factories, m - num countries, t - num children

    # Used to check if the problem has a solution
    country_stock = [0] * (m + 1)

    # Parse info regarding each of the n factories
    factories = {}
    for i in range(1, n + 1):
        factory_info = list(map(int, data[i].split()))
        if factory_info[2] > 0: # Only if the factory has stock > 0
            factories[factory_info[0]] = factory_info # {id_fab: [id_fab, id_country, stock]}
            country_stock[factory_info[1]] += factory_info[2]

    # Parse info regarding each of the m countries
    countries = {}
    min_required_toys = 0
    for i in range(n + 1, n + m + 1):
        country_info = list(map(int, data[i].split()))
        if country_info[1] > 0 and country_info[2] > 0:  # Only if the country has an export limit > 0 and min_toys_required > 0
            countries[country_info[0]] = country_info # {id_country: [id_country, export_limit, min_toys_required]}
            min_required_toys += country_info[2]
    
    if sum(country_stock) < min_required_toys: # Early exit if the problem can't be solved
        print("-1")
        return

    # Parse the requests of t children
    requests = []    
    for i in range(n + m + 1, n + m + t + 1):
        request_info = list(map(int, data[i].split()))
        valid_factories = [factory for factory in request_info[2:] if factory in factories]
        if valid_factories: # Only consider requests with valid factories
            requests.append([request_info[0], request_info[1], valid_factories]) # [id_child, id_country, fab_ids]

    n = len(factories)
    m = len(countries)
    t = len(requests)

    factories_per_country = {} # Factories for each country {country_id: {factory_ids}}
    requests_per_country = {} # Request indices for each country {country_id: {request_indices}}

    for j in countries.keys():
        factories_per_country[j] = set(i for i in factories.keys() if factories[i][1] == j)
        requests_per_country[j] = set(k for k in range(t) if requests[k][1] == j)
    
    valid_factories = {k: set(requests[k][2]) for k in range(t)} # Ensure that children only receive gifts from requested factories

    problem = pulp.LpProblem(sense=pulp.LpMaximize)
    
    # Binary decision variables: happy[k][i] is 1 if child k receives a gift from factory i, 0 otherwise
    happy = pulp.LpVariable.dicts("happy", ((k, i) for k in range(t) for i in valid_factories[k]), cat='Binary')

    # Maximize the number of fulfilled requests
    problem += pulp.lpSum(happy[k,i] for k in range(t) for i in valid_factories[k])

    # Constraints
    # Each child can receive at most one gift
    for k in range(t):
        problem += pulp.lpSum(happy[k,i] for i in valid_factories[k]) <= 1

    # A factory cannot give more gifts than it has in stock
    for i in factories.keys():
        problem += pulp.lpSum(happy[k,i] for k in range(t) if i in valid_factories[k]) <= factories[i][2]

    # A country cannot export more gifts than its export limit
    for j in countries.keys():
        problem += pulp.lpSum(happy[k,i] for k in range(t) for i in factories_per_country[j] if i in valid_factories[k] and requests[k][1] != j) <= countries[j][1]
        
        # Each country must receive at least its minimum required gifts
        problem += pulp.lpSum(happy[k,i] for k in requests_per_country[j] for i in valid_factories[k]) >= countries[j][2]

    # Solve the problem and check if it has an optimal solution
    if problem.solve(PULP_CBC_CMD(msg=False, threads=2, warmStart=True)) != pulp.LpStatusOptimal:
        print("-1")
        return

    # Get the number of satisfied requests
    print(int(pulp.value(problem.objective)))

if __name__ == "__main__":
    main()
