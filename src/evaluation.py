import random
import json
from deap import base, creator, tools
import numpy as np
import matplotlib.pyplot as plt
from Read import Route, Constraints, Data, get_data, Solution

class Algorithm(object):
	def __init__(self, data = Data(), constraints = Constraints(25, 100)):
		self.data = data
		self.constraints = constraints

		creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
		creator.create("Individual", list, fitness=creator.FitnessMin)

		self.IND_SIZE = (len(self.data)-1)*2
		self.toolbox = base.Toolbox()
		self.toolbox.register("indices", random.sample, range(self.IND_SIZE), self.IND_SIZE)
		self.toolbox.register("individual", tools.initIterate, creator.Individual,
						 self.toolbox.indices)

		# zamiast jednej populacji moze byc ew. kilka
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)


		self.toolbox.register("mate", tools.cxOrdered)  # PartialyMatched lub Ordered
		self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)

		# self.toolbox.decorate("mate", checkBounds(MIN, MAX)) #oczywiscie inna postac funkcji!
		# self.toolbox.decorate("mutate", checkBounds(MIN, MAX)) #j.w.

		self.toolbox.register("select", tools.selTournament, tournsize=20)
		self.toolbox.register("evaluate", self.evaluate)
		# w przykladzie jest to rozdzielone, we wczytywaniu jedna funkcj liczy koszt+kare
		#self.toolbox.decorate("evaluate", tools.DeltaPenalty(check_feasability, 10000.0, count_cost)

	def evaluate(self, individual):
		#print('individual: {}\n'.format(individual))
		print('INF EVALUATE')
		no_of_cities = self.IND_SIZE // 2
		print("no_of_cities: {}".format(no_of_cities))
		all_cost = 0
		if individual[0] < no_of_cities: #tymczasowe likwidowanie zlych permutacji
			return float('inf'),
		else:
			routes = []
			destinations = []
			current_vehicle = -1
			for e in individual:
				if e >= no_of_cities:
					if current_vehicle != -1:
						route = Route(self.constraints, current_vehicle, destinations, self.data)
						routes.append(route)
						print('added route: {}'.format(route))
					current_vehicle = e
					destinations = []
				else:
					destinations.append(e)
#			routes = get_routes_from_individual(individual, no_of_cities)

			is_overload = False
			for r in routes:
				if r.feasable == "overload":
					is_overload = True

			if is_overload:
				print("is_overload!!!!!!")
				solution = Solution(routes)
				solution.change_vehicles_load(self.data)

			for r in routes:
				#route = Route(self.constraints, r['vehicle'], r['route'], self.data)
				if r.feasable == "overtime":
					print('route before amending: {}'.format(r))
					r.make_feasible(self.data)
					print('route after amending: {}'.format(r))
				r.feasable = r.check_feasability(self.data)
				if (r.count_cost(self.data)['cost'] !=0):
					print(r)
				all_cost += r.cost
				print('all_cost: {}'.format(all_cost))
		return all_cost,


	# def feasible(self, individual):
	# 	"""Feasibility function for the individual. Returns True if feasible False
	# 	otherwise."""
	# 	#j.w.
	# 	route = Route(Constraints(25, 200), 0, [0,3,6], Data())
	# 	if route.feasable:
	# 		return True
	# 	return False
	#
	# def distance(self, individual):
	# 	"""A distance function to the feasibility region."""
	# 	#j.w.
	# 	route = Route(Constraints(25, 200), 0, [0,3,6], Data())
	# 	return

	# def checkBounds(self, min, max):
	#     def decorator(func):
	#         def wrapper(*args, **kargs):
	#             offspring = func(*args, **kargs)
	#             for child in offspring: #zmienic petle!
	#                 # for i in xrange(len(child)):
	#                 #     if child[i] > max:
	#                 #         child[i] = max
	#                 #     elif child[i] < min:
	#                 #         child[i] = min
	#             return offspring
	#         return wrapper
	#     return decorator


	def getVPRTW(self):

		pop = self.toolbox.population(n=10)
		# probabilities as parameters
		CXPB, MUTPB, NGEN = 0.5, 0.2, 200

		#Evaluate the entire pop
		fitnesses = map(self.toolbox.evaluate, pop)
		for ind, fit in zip(pop, fitnesses):
			ind.fitness.values = fit
			print(ind)
			print(fit)
		for g in range(NGEN):
			#Select the next generation individuals
			selected = self.toolbox.select(pop, len(pop))
			#Clone the selected indiv
			offspring = [self.toolbox.clone(s) for s in selected]

			#Apply crossover and mutation on the offspring
			for child1, child2 in zip(offspring[::2], offspring[1::2]):
				if random.random() < CXPB:
					self.toolbox.mate(child1, child2)
					del child1.fitness.values
					del child2.fitness.values

			for mutant in offspring:
				if random.random() < MUTPB:
					self.toolbox.mutate(mutant)
					del mutant.fitness.values

			#Eval the indiv with an invalid fitness
			invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
			fitnesses = self.toolbox.map(self.toolbox.evaluate, invalid_ind)

			for ind, fit in zip(invalid_ind, fitnesses):
				ind.fitness.values = fit

			#The population is entirely replaces by offspring
			pop[:] = offspring

		plot_results(pop, self.IND_SIZE // 2, self.data,self.constraints)
		for p in pop:
			print (p)
			print (p.fitness.values)
			print (' ')




	def check_feasibility(individual):
		pass

def get_routes_from_individual(individual, no_of_cities):
	routes = []
	destinations = []
	current_vehicle = -1
	for e in individual:
		elem = e + 1
		if elem > no_of_cities:
			# print('e: {}'.format(e))
			if current_vehicle != -1:
				route_description = {
					'vehicle': current_vehicle,
					'route': destinations
				}
				routes.append(route_description)
			current_vehicle = elem
			destinations = []
		else:
			destinations.append(elem)
	return routes

def plot_results(population, no_of_cities, data, constraints):
	"""

	:type population: object
	"""
	cities = []
	for d in data:
		cities.append((d.x_coord, d.y_coord))
	max_x = max(data, key=lambda x: x.x_coord)
	min_x = min(data, key=lambda x: x.x_coord)
	#space = np.linspace(0, max_x, 100)
	#space = np.linspace(0, max_x, 100)
	max_y = max(data, key=lambda x: x.y_coord)
	min_y = min(data, key=lambda x: x.y_coord)
	ind_id = 0
	f, plots = plt.subplots(len(population) // 3 + 1, 3, sharex='col', sharey='row')
	for individual in population:
		i = 1

		routes = get_routes_from_individual(individual, no_of_cities)
		for r in routes:
			route = Route(constraints, r['vehicle'], r['route'], data)
			custom_data = [(data[i].x_coord, data[i].y_coord) for i in route.seq]
			plots[ind_id // 3 ][ind_id % 3].plot(list(map(lambda x: x[0], custom_data)),
					 list(map(lambda x: x[1], custom_data)), zorder=i)

			i += 1
		ind_id += 1
	plt.show()


	plt.figure()
	plt.subplot(211)
	plt.plot(list(map(lambda x: x.x_coord, data)),
			 list(map(lambda x: x.y_coord, data)))
	plt.show()




data = get_data()
a = Algorithm(data=data)
a.getVPRTW()
