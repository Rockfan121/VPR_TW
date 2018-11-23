import random
import json
from deap import base, creator, tools
from Read import Data, Route, Constraints

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin) 

def initIndividual(ind_size):
	customers = random.sample(range(ind_size), ind_size)
	vehicles = customers.copy()
	for x in range(ind_size):
		vehicles[x] += 100
	result = customers.extend(vehicles)
	return shuffle(result[1:])
	

IND_SIZE = 25
toolbox = base.Toolbox()
toolbox.register("individual", initIndividual, IND_SIZE)

#zamiast jednej populacji może być ew. kilka
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
	#tzreba bedzie przeparsowac individual i tworzyc Route z rzeczywistymi danymi
    route = Route(Constraints(25, 200), 0, [0,3,6], Data())
    return route.count_cost

def feasible(individual):
    """Feasibility function for the individual. Returns True if feasible False
    otherwise."""
    #j.w.
    route = Route(Constraints(25, 200), 0, [0,3,6], Data())
    if route.feasable:
        return True
    return False

def distance(individual):
    """A distance function to the feasibility region."""
    #j.w.
    route = Route(Constraints(25, 200), 0, [0,3,6], Data())
    return 

# def checkBounds(min, max):
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

toolbox.register("mate", tools.cxPartialMatched) #inny algorytm!
toolbox.register("mutate", tools.mutShuffleIndexes, indpb =0.1)

# toolbox.decorate("mate", checkBounds(MIN, MAX)) #oczywiscie inna postac funkcji!
# toolbox.decorate("mutate", checkBounds(MIN, MAX)) #j.w.

toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate)
#w przykladzie jest to rozdzielone, we wczytywaniu jedna funkcj liczy koszt+kare
# toolbox.decorate("evaluate", tools.DeltaPenalty(feasible, 7.0, distance))

def main():
	
	pop = toolbox.population(n=10)
	CXPB, MUTPB, NGEN = 0.5, 0.2, 40

	#Evaluate the entire pop
	fitnesses = map(toolbox.evaluate, pop)
	for ind, fit in zip(pop, fitnesses):
		ind.fitness.values = fit

	for g in range(NGEN):
		#Select the next generation individuals
		selected = toolbox.select(pop, len(pop))
		#Clone the selected indiv
		offspring = map(toolbox.clone, selected)

		#Apply crossover and mutation on the offspring
		for child1, child2 in zip(offspring[::2], offspring[1::2]):
			if random.random() < CXPB:
				toolbox.mate(child1, child2)
				del child1.fitness.values
				del child2.fitness.values

		for mutant in offspring:
			if random.random() < MUTB:
				toolbox.mutate(mutant)
				del mutant.fitness.values

		#Eval the indiv with an invalid fitness
		invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
		fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
		for ind, fit in zip(invalid_ind, fitnesses):
			ind.fitness.values = fit
		
		#The population is entirely replaces by offspring
		pop[:] = offspring

	print (pop)

main()