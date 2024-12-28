#pylint: skip-file
import pulp
from pulp import PULP_CBC_CMD

def main():
    n, m, t = map(int, input().split()) # n - num factories, m - num countries, t - num children

    # Parse info regarding each of the n factories
    factories = []
    for _ in range(n):
        factory_info = list(map(int, input().split()))
        factories.append(factory_info) # [id_fab, id_country, stock]

    # Parse info regarding each of the m countries
    countries = []
    for _ in range(m):
        country_info = list(map(int, input().split()))
        countries.append(country_info) # [id_country, export_limit, min_toys_required]

    # Parse the requests of t children
    requests = []
    for _ in range(t):
        request_info = list(map(int, input().split()))
        requests.append(request_info) # [id_child, id_country, fab_ids, ...]

    problem = pulp.LpProblem(sense=pulp.LpMaximize)
    
    # Binary decision variables: happy[k][i] is 1 if child k receives a gift from factory i, 0 otherwise
    happy = pulp.LpVariable.dicts("happy", (range(t), range(n)), cat='Binary')

    # Maximize the number of fulfilled requests
    problem += pulp.lpSum(happy[k][i] for k in range(t) for i in range(n))

    # Constraints
    # Each child can receive at most one gift
    for k in range(t):
        problem += pulp.lpSum(happy[k][i] for i in range(n)) <= 1

    # A factory cannot give more gifts than it has in stock
    for i in range(n):
        problem += pulp.lpSum(happy[k][i] for k in range(t)) <= factories[i][2]

    # A country cannot export more gifts than its export limit
    for j in range(m):
        problem += pulp.lpSum(happy[k][i] for k in range(t) for i in range(n) if factories[i][1] == j + 1) <= countries[j][1]

    # Each country must receive at least its minimum required gifts
    for j in range(m):
        problem += pulp.lpSum(happy[k][i] for k in range(t) if requests[k][1] == j + 1 for i in range(n)) >= countries[j][2]

    # Ensure that children only receive gifts from requested factories
    for k in range(t):
        for i in range(n):
            if i + 1 not in requests[k][2:]:
                problem += happy[k][i] == 0

    # Solve the problem
    problem.solve(PULP_CBC_CMD(msg=False))

    # Check if the problem has an optimal solution
    if pulp.LpStatus[problem.status] != 'Optimal':
        print(-1)
        return

    # Calculate the number of satisfied requests
    satisfied_requests = sum(1 for k in range(t) for i in range(n) if pulp.value(happy[k][i]) == 1)
    print(satisfied_requests)

if __name__ == "__main__":
    main()
