#!/usr/bin/env python

"""
Code to load an expert policy and generate roll-out data for behavioral cloning.
Example usage:
    python run_expert.py experts/Humanoid-v1.pkl Humanoid-v1 --render \
            --num_rollouts 20
Author of this script and included expert policies: Jonathan Ho (hoj@openai.com)
"""
import os
import pickle
import tensorflow as tf
import numpy as np
import homework.hw1.tf_util as tf_util
import gym
from gym import wrappers
import BIRL.homework.hw1.load_policy as load_policy

def generate_all_rollout_data():
    d = os.getcwd() 
    print(d)
#    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/Ant-v2.pkl', 'Ant-v2', 250, False, 'data')
    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/HalfCheetah-v2.pkl', 'HalfCheetah-v2', 10, False, 'data')
#    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/Hopper-v2.pkl', 'Hopper-v2', 10, False, 'data')
#    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/Humanoid-v2.pkl', 'Humanoid-v2', 250, False, 'data')
#    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/Reacher-v2.pkl', 'Reacher-v2', 250, False, 'data')
#    generate_rollout_data('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/experts/Walker2d-v2.pkl', 'Walker2d-v2', 10, False, 'data') 


def generate_rollout_data(expert_policy_file, env_name, num_rollouts, render, output_dir=None, save=False, max_timesteps=None):
    print('loading and building expert policy')
    policy_fn = load_policy.load_policy(expert_policy_file)
    print('loaded and built')

    with tf.Session():
        tf_util.initialize()

        env = gym.make(env_name)
#        max_steps = max_timesteps or env.spec.timestep_limit
        max_steps = 1000

        if save:
            expert_results_dir = os.path.join(os.getcwd(), 'results', env_name, 'expert')
            env = wrappers.Monitor(env, expert_results_dir, force=True)
        
        returns = []
        observations = []
        actions = []
        for i in range(num_rollouts):
            print('iter', i)
            obs = env.reset()
            done = False
            totalr = 0.
            steps = 0
            while not done:
                action = policy_fn(obs[None,:])
                observations.append(obs)
                actions.append(action)
                obs, r, done, _ = env.step(action)
                totalr += r
                steps += 1
                if render:
                    env.render()
                if steps % 100 == 0: print("%i/%i"%(steps, max_steps))
                if steps >= max_steps:
                    break
            returns.append(totalr)

        print('returns', returns)
        print('mean return', np.mean(returns))
        print('std of return', np.std(returns))

        expert_data = {'observations': np.array(observations),
                       'actions': np.array(actions),
                       'mean_return': np.mean(returns),
                        'std_return': np.std(returns)}

        if output_dir is not 'None':
#            output_dir = os.path.join(os.getcwd(), output_dir)
            filename = '{}_data_{}_rollouts.pkl'.format(env_name, num_rollouts)
#            with open(output_dir + '/' + filename,'wb') as f:
            with open('/Users/torbensell/Dropbox (Cambridge University)/UNI/CAM/PhD/Programme/BIRL/homework/hw1/data/' + filename,'wb') as f:
                 pickle.dump(expert_data, f)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('expert_policy_file', type=str)
    parser.add_argument('envname', type=str)
    parser.add_argument("--max_timesteps", type=int)
    parser.add_argument('--num_rollouts', type=int, default=20,
                        help='Number of expert roll outs')
    parser.add_argument('--render', action='store_true')
    parser.add_argument("--output_dir", type=str, default='data')
    args = parser.parse_args()

    generate_rollout_data(args.expert_policy_file, args.envname, args.num_rollouts, args.render, args.max_timesteps)