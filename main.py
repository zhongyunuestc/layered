import os
import argparse
import numpy as np
from layered.problem import Problem
from layered.gradient import BatchBackprop
from layered.network import Network, Matrices
from layered.optimization import GradientDecent, Momentum, WeightDecay
from layered.utility import repeated, batched
from layered.evaluation import Evaluator
from layered.plot import Plot


def compute_costs(network, weights, cost, examples):
    prediction = [network.feed(weights, x.data) for x in examples]
    costs = [cost(x, y.target).mean() for x, y in zip(prediction, examples)]
    return list(costs)


if __name__ == '__main__':
    # The problem defines dataset, network and learning parameters
    parser = argparse.ArgumentParser('layered')
    parser.add_argument(
        'problem', nargs='?',
        help='path to the YAML problem definition')
    parser.add_argument(
        '-v', '--visual', action='store_true',
        help='show a diagram of training costs')
    args = parser.parse_args()
    print('Problem', os.path.split(args.problem)[1])
    problem = Problem(args.problem)

    # Define model and initialize weights
    network = Network(problem.layers)
    weights = Matrices(network.shapes)
    weights.flat = np.random.normal(0, problem.weight_scale, len(weights.flat))

    # Classes needed during training
    backprop = BatchBackprop(network, problem.cost)
    momentum = Momentum()
    decent = GradientDecent()
    decay = WeightDecay()
    if args.visual:
        plot = Plot()
    evaluator = Evaluator(
        network, problem.dataset.testing, problem.evaluate_every)

    # Train the model
    repeats = repeated(problem.dataset.training, problem.epochs)
    batches = batched(repeats, problem.batch_size)
    for index, batch in enumerate(batches):
        gradient = backprop(weights, batch)
        gradient = momentum(gradient, problem.momentum)
        weights = decent(weights, gradient, problem.learning_rate)
        weights = decay(weights, problem.weight_decay)
        # Show progress
        if args.visual:
            plot(compute_costs(network, weights, problem.cost, batch))
        evaluator(index * problem.batch_size, weights)
    print('Done')
