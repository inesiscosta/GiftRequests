#pylint: skip-file
import sys
from pulp import GLPK, LpMaximize, LpProblem, LpStatusOptimal, LpVariable, lpSum, value

def main():
  data = sys.stdin.read().splitlines()
    
  n, m, t = map(int, data[0].split())  # n - num factories, m - num countries, t - num children

  factories_per_country = {} # {id_country: factory_ids}
  requests_per_country = {} # {id_country: child_ids}

  # Parse info regarding each of the n factories.
  factories = {} # {id_factory: [id_country, stock]}
  for line in range(1, n + 1):
    factory_info = list(map(int, data[line].split())) # [id_factory, id_country, stock]
    if factory_info[2] > 0: # A factory is only relevant if its stock it > 0.
      factories[factory_info[0]] = factory_info[1:]
      factories_per_country.setdefault(factory_info[1], set()).add(factory_info[0])

  # Parse info regarding each of the m countries.
  countries = {} # {id_country: [export_limit, min_gifts_required]}
  for line in range(n + 1, n + m + 1):
    country_info = list(map(int, data[line].split())) # [id_country, export_limit, min_gifts_required]
    # A country is only relevant if its export limit and minimum number of gifts required are > 0
    if country_info[1] > 0 and country_info[2] > 0:
      countries[country_info[0]] = country_info[1:]

  # Parse info regarding the requests of each of the t children.
  requests = {}
  requested_factories = {}
  for line in range(n + m + 1, n + m + t + 1):
    request_info = list(map(int, data[line].split())) # [id_child, id_country, factory_ids]
    valid_factories = [factory for factory in request_info[2:] if factory in factories]
    if valid_factories: # Only consider requests with valid factories.
      requests[request_info[0]] = [request_info[1], valid_factories] # {id_child: [id_country, factory_ids]}
      requests_per_country.setdefault(request_info[1], set()).add(request_info[0])
      requested_factories[request_info[0]] = set(valid_factories)

  for country in countries:
    if len(requests_per_country[country]) < countries[country][1]:
      print(-1)
      return

  problem = LpProblem(sense=LpMaximize)
  
  # Binary decision variables: happy[id_child][id_factory] is 1 if the child identified through id_child receives a gift from factory identified with id_factory, 0 otherwise.
  happy = LpVariable.dicts("happy", ((id_child, id_factory) for id_child in requests for id_factory in requested_factories[id_child]), cat='Binary')

  # Maximize the number of fulfilled requests.
  problem += lpSum(happy[id_child, id_factory] for id_child in requests for id_factory in requested_factories[id_child])

  # Create data structs used to make the constraints for the LP solver.
  num_requests_per_factory = {id_factory: [] for id_factory in factories}
  country_exports = {id_country: [] for id_country in countries}
  children = []
  
  for id_child in requests:
    # Each child can receive at most one gift.
    children.append((id_child, requested_factories[id_child]))
    
    # A factory cannot distribute more gifts that it has in stock.
    for id_factory in requested_factories[id_child]:
      num_requests_per_factory[id_factory].append((id_child, id_factory))
    
    # Check if the factories don't exceed the maximum permitted exports for the country.
    for id_country in countries:
      for id_factory in factories_per_country[id_country]:
        if id_factory in requested_factories[id_child] and requests[id_child][0] != id_country:
          country_exports[id_country].append((id_child, id_factory))
  
  # Create the constraints using pre-calculated values.
  for id_child, valid_factories in children:
    problem += lpSum(happy[id_child, id_factory] for id_factory in valid_factories) <= 1
  
  # A factory cannot distribute more gifts than it has in stock.
  for id_factory in factories:
    problem += lpSum(happy[id_child, id_factory] for id_child, id_factory in num_requests_per_factory[id_factory]) <= factories[id_factory][1]
  
  for id_country in countries:
    # A country cannot export more gifts than its export limit.
    problem += lpSum(happy[id_child, id_factory] for id_child, id_factory in country_exports[id_country]) <= countries[id_country][0]

    # A country must receive at least its minimum number required gifts.
    problem += lpSum(happy[id_child, id_factory] for id_child in requests_per_country[id_country] for id_factory in requested_factories[id_child]) >= countries[id_country][1]

  # Solve the problem and check if it has an optimal solution.
  if problem.solve(GLPK(msg=False)) == LpStatusOptimal:
    print(int(value(problem.objective)))
  else:
    print("-1")

if __name__ == "__main__":
  main()
