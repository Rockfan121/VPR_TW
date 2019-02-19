import random
import json
from deap import base, creator, tools
import numpy as np
import matplotlib.pyplot as plt
from Read import Route, Constraints, Data, get_data, Solution
import sys

top_result = 1_000_000_000_000_000.0

POPULATION_SIZE = 25
class Algorithm(object):
	def __init__(self, data = Data(), constraints = Constraints(25, 100)):
		self.data = data
		self.constraints = constraints
		self.top_result = 1_000_000_000_000_000

		creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
		creator.create("Individual", list, fitness=creator.FitnessMin)

		self.IND_SIZE = (len(self.data)-1)*2
		self.toolbox = base.Toolbox()
		self.toolbox.register("indices", random.sample, range(self.IND_SIZE), self.IND_SIZE)
		self.toolbox.register("individual", tools.initIterate, creator.Individual,
						 self.toolbox.indices)

		# zamiast jednej populacji moze byc ew. kilka
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)


		self.toolbox.register("mate", tools.cxPartialyMatched)  # PartialyMatched lub Ordered
		self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)

		# self.toolbox.decorate("mate", checkBounds(MIN, MAX)) #oczywiscie inna postac funkcji!
		# self.toolbox.decorate("mutate", checkBounds(MIN, MAX)) #j.w.

		self.toolbox.register("select", tools.selTournament, tournsize=15)
		self.toolbox.register("evaluate", self.evaluate)
		# w przykladzie jest to rozdzielone, we wczytywaniu jedna funkcj liczy koszt+kare
		#self.toolbox.decorate("evaluate", tools.DeltaPenalty(check_feasability, 10000.0, count_cost)

	def evaluate(self, individual):
		verbose = False
		#print('individual: {}\n'.format(individual))
		# print('EVALUATE')
		no_of_cities = self.IND_SIZE // 2
		#print("no_of_cities: {}".format(no_of_cities))
		all_cost = 0
		if individual[0] < no_of_cities: #tymczasowe likwidowanie zlych permutacji
			first_city  = 0
			for e, i in zip(individual, range(self.IND_SIZE)):
				if e >= no_of_cities:
					first_city = i
			individual[0], individual[first_city] = individual[first_city], individual[0]

		routes = get_routes_from_individual(individual, no_of_cities, self.constraints, self.data)

		is_overload = False
		for r in routes:
			if r.feasable == "overload":
				is_overload = True

		if is_overload:
			#print("is_overload!!!!!!")
			solution = Solution(routes)
			solution.change_vehicles_load(self.data)

		for r in routes:
			#route = Route(self.constraints, r['vehicle'], r['route'], self.data)
			r.check_feasability(self.data)
			if r.feasable == "overtime":
				#print('route before amending: {}'.format(r))
				r.make_feasible(self.data)
				r.feasable = r.check_feasability(self.data)
				r.count_cost(self.data)
				#print('route after amending: {}'.format(r))
			r.feasable = r.check_feasability(self.data)
			if (r.count_cost(self.data)['cost'] !=0):
				if verbose:
					print(r)
			all_cost += r.cost
		if verbose: 
			print('all_cost: {}'.format(all_cost))
		if all_cost != 0 and all_cost < self.top_result:
			self.top_result = all_cost

		total_cities_here = sum([len(r.seq) for r in routes])
		if verbose:
			print("All cities: {}".format(total_cities_here))
			print("Individual: {}".format(individual))
		return all_cost,


	def getVPRTW(self, CXPB=0.3, MUTPB=0.35, NGEN=300, verbose=False):

		# probabilities as parameters
		pop = self.toolbox.population(n=POPULATION_SIZE)

		#Evaluate the entire pop
		fitnesses = map(self.toolbox.evaluate, pop)
		for ind, fit in zip(pop, fitnesses):
			ind.fitness.values = fit
			if verbose:
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
		verbose = True
		if verbose:
			plot_results(pop, self.IND_SIZE // 2, self.data,self.constraints)
			for p in pop:
				print (p)
				print (p.fitness.values)
				print (' ')

def get_routes_from_individual(individual, no_of_cities, constraints, data, verbose=False):
	routes = []
	destinations = []
	current_vehicle = -1
	last_idx = len(individual)-1
	for e in individual:
		if e >= no_of_cities:
			if current_vehicle != -1:
				route = Route(constraints, current_vehicle, destinations, data)
				routes.append(route)
				if verbose:
					print('added route: {}'.format(route))
			current_vehicle = e
			destinations = []
		elif e == individual[last_idx]:
			destinations.append(e)
			route = Route(constraints, current_vehicle, destinations, data)
			routes.append(route)
			if verbose:
				print('added route: {}'.format(route))
		else:
			destinations.append(e)
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
	f, plots = plt.subplots(1, 1, sharex='col', sharey='row')
	for individual in population:
		z = 1

		routes = get_routes_from_individual(individual, no_of_cities, constraints, data, verbose=True)
		total_cities_here = sum([len(r.seq) for r in routes])
		print("All cities: {}".format(total_cities_here))
		print("Individual: {}".format(ind_id))
		#print("Total cost: {}".format(sum(map(lambda x: x.cost, routes))))
		for r in routes:
			route = r
			r.check_feasability(data)

			# print(r)
			custom_data = [(data[i+1].x_coord, data[i+1].y_coord) for i in route.seq]
			custom_data = [(data[0].x_coord, data[0].y_coord)] + custom_data
			plots.plot(list(map(lambda x: x[0], custom_data)),
					 list(map(lambda x: x[1], custom_data)), zorder=z*2)
			#plots[ind_id // 3][ind_id % 3].title = route.__repr__()
			z += 1
			plots.plot(list(map(lambda x: x.x_coord, data)),
			 list(map(lambda x: x.y_coord, data)), zorder=0)
		ind_id += 1
		plt.show()
	# plots[0][0].plot(list(map(lambda x: x.x_coord, data)),
	# 		 list(map(lambda x: x.y_coord, data)), zorder=1)
	# plt.show()



c = Constraints(25,100)
data = get_data(sys.argv[1], c)
print(c.__dict__)
a = Algorithm(data=data, constraints=c)
SEARCH_PARAMS = False 
if not SEARCH_PARAMS:
	print("Filename {}".format(sys.argv[1]))
	a.getVPRTW(0.35, 0.58, 600)
	print("Best solution cost: {}".format(a.top_result))
else:
	probabilities = np.linspace(0.1, 0.9, 9) #17
	generations = [200, 250, 300] #generations = [100, 150, 200, 250, 300, 350]
	params = []
	best_params = []
	best_result = top_result
	for cxpb in probabilities:
		for mutpb in probabilities:
			for ngen in generations:
				for i in range(3):
					print("CXPB: {}, MUTPB: {}, NGEN: {}, I: {}".format(cxpb, mutpb, ngen, i))
					a.getVPRTW(cxpb, mutpb, ngen)
					print("Best solution cost: {}".format(a.top_result))
					params.append({'cxpb': cxpb, 'mutpb': mutpb, 'ngen': ngen, 'i': i, 'result': a.top_result})
					if best_result > a.top_result:
						best_params.append({'cxpb': cxpb, 'mutpb': mutpb, 'ngen': ngen, 'i': i, 'result': a.top_result})
						best_result = a.top_result
					a.top_result = 1_000_000_000_000_000
	print("ALL PARAMS AND RESULTS")
	print(params)

	print("BEST PARAMS AND RESULTS")
	print(best_params)



