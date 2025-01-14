"""ASA Project 3"""
import sys
from pulp import GLPK, LpMaximize, LpProblem, LpStatusOptimal, LpVariable, lpSum, value

def main():
    """
    If an optimal solution is found, the function prints the maximum number of happy children.
    Otherwise, it prints "-1".
    """
    data = sys.stdin.read().splitlines()
    num_factories, num_countries, num_children = map(int, data[0].split())

    factories = {}
    countries = {}
    children = {}

    for line in range(1, num_factories + 1):
        factory_id, country_id, stock = map(int, data[line].split())
        if stock > 0:
            factories[factory_id] = {'country_id': country_id,
            'stock': stock, 'requests': []}

    for line in range(num_factories + 1, num_factories + num_countries + 1):
        country_id, export_limit, min_gifts = map(int, data[line].split())
        countries[country_id] = {'export_limit': export_limit,
        'min_gifts': min_gifts, 'exports': [], 'chosen_factories': []}

    for line in range(num_factories + num_countries + 1,
    num_factories + num_countries + num_children + 1):
        child_id, country_id, *requested_factories = map(int, data[line].split())
        valid_factories = []
        for factory_id in requested_factories:
            if factory_id in factories:
                factory = factories[factory_id]
                valid_factories.append(factory_id)
                countries[country_id]['chosen_factories'].append((child_id, factory_id))
                if factory['country_id'] != country_id:
                    countries[factory['country_id']]['exports'].append((child_id, factory_id))
                factory['requests'].append(child_id)
        children[child_id] = {'id': child_id, 'factories': valid_factories}

    # Create LP problem
    problem = LpProblem(sense=LpMaximize)
    happy = LpVariable.dicts("happy", ((child_id, factory_id) for
    child_id, child in children.items() for factory_id in child['factories']), cat='Binary')

    problem += lpSum(happy[child_id, factory_id] for child_id, child
    in children.items() for factory_id in child['factories'])

    # Constraints

    # Each child can receive at most one gift
    for child_id, child in children.items():
        problem += lpSum(happy[child_id, factory_id] for factory_id
        in child['factories']) <= 1

    # A factory cannot distribute more gifts than it has in stock.
    for factory_id, factory in factories.items():
        problem += lpSum(happy[child_id, factory_id] for child_id
        in factory['requests']) <= factory['stock']

    for country_id, country in countries.items():
        # A country must receive at least its minimum number of gifts.
        problem += lpSum(happy[child_id, factory_id] for (child_id, factory_id)
        in country['chosen_factories']) >= country['min_gifts']

        # A country cannot export more gifts than its export limit.
        problem += lpSum(happy[child_id, factory_id] for (child_id, factory_id)
        in country['exports']) <= country['export_limit']

    # Solve the problem and check if it has an optimal solution.
    if problem.solve(GLPK(msg=False)) == LpStatusOptimal:
        print(int(value(problem.objective)))
    else:
        print("-1")

if __name__ == "__main__":
    main()
