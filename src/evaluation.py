import random
import json
from deap import base, creator, tools

from Read import Route, Constraints, Data, get_data


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

		# zamiast jednej populacji może być ew. kilka
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

		self.toolbox.register("mate", tools.cxPartialyMatched)  # PartialyMatched lub Ordered
		self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)

		# self.toolbox.decorate("mate", checkBounds(MIN, MAX)) #oczywiscie inna postac funkcji!
		# self.toolbox.decorate("mutate", checkBounds(MIN, MAX)) #j.w.

		self.toolbox.register("select", tools.selTournament, tournsize=3)
		self.toolbox.register("evaluate", self.evaluate)
		# w przykladzie jest to rozdzielone, we wczytywaniu jedna funkcj liczy koszt+kare
		# self.toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 7.0, distance))

	def evaluate(self, individual):
		#print('individual: {}\n'.format(individual))
		no_of_cities = self.IND_SIZE // 2
		if individual[0] <= no_of_cities: #tymczasowe likwidowanie zlych permutacji
			return float('inf'),
		else:
			routes = []
			destinations = []
			current_vehicle = -1
			for e in individual:
				if e > no_of_cities:
					print('e: {}'.format(e))
					if current_vehicle != -1:
						route_description = {
							'vehicle': current_vehicle,
							'route': destinations
						}
						routes.append(route_description)
					current_vehicle = e
					destinations = []
				else:
					destinations.append(e)

			all_cost = 0
			for r in routes:
				route = Route(self.constraints, r['vehicle'], r['route'], self.data)
				all_cost += route.count_cost(self.data)['cost']

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
		CXPB, MUTPB, NGEN = 0.5, 0.2, 100

		#Evaluate the entire pop
		fitnesses = map(self.toolbox.evaluate, pop)
		for ind, fit in zip(pop, fitnesses):
			ind.fitness.values = fit

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

		for p in pop:
			print (p) 
			print (' ')

data = get_data()
a = Algorithm(data=data)
a.getVPRTW()