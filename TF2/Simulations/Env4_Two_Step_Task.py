import numpy as np
from Env_Model import *

# encoding of the higher stages
S_1 = 0
S_2 = 1
S_3 = 2
nb_states = 3

class Two_Step_Task(Env):
    def __init__(self):
        super().__init__(nb_actions=2, nb_obs=3)
        
        # start in S_1
        self.state = S_1
        
        # defines what is the stage with the highest expected reward. Initially random
        self.highest_reward_second_stage = np.random.choice([S_2,S_3])
        
        self.reset()
        
        # initialization of plotting variables
        common_prob = 0.8
        self.transitions = np.array([
            [common_prob, 1-common_prob],
            [1-common_prob, common_prob]
        ])
        self.transition_count = np.zeros((2,2,2))
        
        self.last_action = None
        self.last_state = None
    
    def get_state(self):
        one_hot_array = np.zeros((3),dtype=np.float32)
        one_hot_array[self.state] = 1.0
        return one_hot_array

    def possible_switch(self):
        if (np.random.uniform() < 0.025):
            # switches which of S_2 or S_3 has expected reward of 0.9
            self.highest_reward_second_stage = S_2 if (self.highest_reward_second_stage == S_3) else S_3
            
    def get_rprobs(self):
        """
        probability of reward of states S_2 and S_3, in the form [[p, 1-p], [1-p, p]]
        """
        if (self.highest_reward_second_stage == S_2):
            r_prob = 0.9
        else:
            r_prob = 0.1
        
        rewards = np.array([
            [r_prob, 1-r_prob],
            [1-r_prob, r_prob]
        ])
        return rewards
            
    def isCommon(self,action,state):
        if self.transitions[action][state] >= 1/2:
            return True
        return False
        
    def updateStateProb(self,action):
        if self.last_is_rewarded: #R
            if self.last_is_common: #C
                if self.last_action == action: #Rep
                    self.transition_count[0,0,0] += 1
                else: #URep
                    self.transition_count[0,0,1] += 1
            else: #UC
                if self.last_action == action: #Rep
                    self.transition_count[0,1,0] += 1
                else: #URep
                    self.transition_count[0,1,1] += 1
        else: #UR
            if self.last_is_common:
                if self.last_action == action:
                    self.transition_count[1,0,0] += 1
                else:
                    self.transition_count[1,0,1] += 1
            else:
                if self.last_action == action:
                    self.transition_count[1,1,0] += 1
                else:
                    self.transition_count[1,1,1] += 1
                    
        
    def stayProb(self):
        print(self.transition_count)
        row_sums = self.transition_count.sum(axis=-1)
        stay_prob = self.transition_count / row_sums[:,:,np.newaxis] 
       
        return stay_prob

    def reset(self):
        self.timestep = 0
        
        # for the two-step task plots
        self.last_is_common = None
        self.last_is_rewarded = None
        self.last_action = None
        self.last_state = None
        
        # come back to S_1 at the end of an episode
        self.state = S_1
        
        return self.get_state()
    
    def test_reset(self):
        return self.reset()
        
    def step(self,action):
        self.timestep += 1
        self.last_state = self.state
        
        # get next stage
        if (self.state == S_1):
            # get reward
            reward = 0
            # update stage
            self.state = S_2 if (np.random.uniform() < self.transitions[action][0]) else S_3
            # keep track of stay probability after first action
            if (self.last_action != None):    
                self.updateStateProb(action)
            self.last_action = action
            # book-keeping for plotting
            self.last_is_common = self.isCommon(action,self.state-1)
            
        else:# case S_2 or S_3
            # get probability of reward in stage
            r_prob = 0.9 if (self.highest_reward_second_stage == self.state) else 0.1
            # get reward
            reward = 1 if np.random.uniform() < r_prob else 0
            # update stage
            self.state = S_1
            # book-keeping for plotting
            self.last_is_rewarded = reward

        # new state after the decision
        new_state = self.get_state()
        if self.timestep >= 200: 
            done = True
        else: 
            done = False
        return new_state,reward,done,self.timestep
    
    def trial(self,action):
        if (self.state == S_1):
            self.possible_switch()
        # do one action in S_1, and keep track of the perceptually distinguishable state you arive in
        observation,_,_,_ = self.step(action)
        # do the same action in the resulting state (S_2 or S_3). The action doesn't matter, the reward does
        _,reward,done,_ = self.step(action)
        return observation,reward,done,self.timestep