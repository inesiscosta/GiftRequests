#pylint: skip-file
import sys
from pulp import GLPK, LpMaximize, LpProblem, LpStatusOptimal, LpVariable, lpSum, value

class Factory:
  def __init__(self, id, country, stock):
    self.id = id
    self.country = country
    self.stock = stock
    self.requests = []

class Country:
  def __init__(self, id, export_limit, min_gifts):
    self.id = id
    self.export_limit = export_limit
    self.min_gifts = min_gifts
    self.exports = []
    self.chosen_factories = []
    self.num_country_requests = 0

class Child:
  def __init__(self, id, factories):
    self.id = id
    self.factories = factories

def main():
  data = sys.stdin.read().splitlines()
  num_factories, num_countries, num_children = map(int, data[0].split())

  factories = {}
  countries = {}
  children = {}

  for line in range(1, num_factories + 1):
    factory_id, country_id, stock = map(int, data[line].split())
    if stock > 0:
      countries.setdefault(country_id, Country(country_id, 0, 0))
      factories[factory_id] = Factory(factory_id, countries[country_id], stock)

  for line in range(num_factories + 1, num_factories + num_countries + 1):
    country_id, export_limit, min_gifts = map(int, data[line].split())
    if country_id not in countries:
      countries[country_id] = Country(country_id, export_limit, min_gifts)
    else:
      countries[country_id].export_limit = export_limit
      countries[country_id].min_gifts = min_gifts

  for line in range(num_factories + num_countries + 1, num_factories + num_countries + num_children + 1):
    child_id, country_id, *requested_factories = map(int, data[line].split())
    valid_factories = [factories[factory_id] for factory_id in requested_factories if factory_id in factories]
    children[child_id] = Child(child_id, valid_factories)
    for factory in valid_factories:
      countries[country_id].chosen_factories.append((child_id, factory.id))
      if factory.country.id != country_id:
        countries[factory.country.id].exports.append((children[child_id].id, factory.id))
      factory.requests.append(children[child_id])
      countries[country_id].num_country_requests += 1

  # Create LP problem
  problem = LpProblem(sense=LpMaximize)

  happy = LpVariable.dicts("happy", ((child.id, factory.id) for child in children.values() for factory in child.factories), cat='Binary')

  problem += lpSum(happy[child.id, factory.id] for child in children.values() for factory in child.factories)

  # Constraints

  # Each child can receive at most one gift
  for child in children.values():
    problem += lpSum(happy[child.id, factory.id] for factory in child.factories) <= 1

  # A factory cannot distribute more gifts than it has in stock.
  for factory in factories.values():
    problem += lpSum(happy[child.id, factory.id] for child in factory.requests) <= factory.stock

  for country in countries.values():
    # A country must receive at least its minimum number of gifts.
    problem += lpSum(happy[child_id, factory_id] for (child_id, factory_id) in country.chosen_factories) >= country.min_gifts

    # A country cannot export more gifts than its export limit.
    problem += lpSum(happy[child_id, factory_id] for (child_id, factory_id) in country.exports) <= country.export_limit

  # Solve the problem and check if it has an optimal solution.
  if problem.solve(GLPK(msg=False)) == LpStatusOptimal:
    print(int(value(problem.objective)))
  else:
    print("-1")

if __name__ == "__main__":
  main()
