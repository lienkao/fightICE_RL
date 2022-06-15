import torch
from torch import nn
import numpy as np
import torch.nn.functional as F
class Net(nn.Module):
    def __init__(self, n_states, n_actions, n_hidden):
        super(Net, self).__init__()

        # input layer to hidden layer 1
        self.fc1 = nn.Linear(n_states, n_hidden)
        self.fc1.weight.data.normal_(0, 0.1)
        # hidden layer 1 to hidden layer 2
        self.fc2 = nn.Linear(n_hidden, n_hidden)
        self.fc2.weight.data.normal_(0, 0.1)
        # hidden layer 2 to hidden layer 3
        self.fc3 = nn.Linear(n_hidden, n_hidden)
        self.fc3.weight.data.normal_(0, 0.1)
        # hidden layer 3 to output layer
        self.out = nn.Linear(n_hidden, n_actions)
        self.out.weight.data.normal_(0, 0.1)
        print(self.fc1)
        print(self.fc2)
        print(self.fc3)
        print(self.out)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x) # ReLU activation
        x = self.fc2(x)
        x = F.relu(x)
        x = self.fc3(x)
        x = F.relu(x)
        actions_value = self.out(x)
        return actions_value
class DQN(object):
    def __init__(self, n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity, version):
        self.eval_net, self.target_net = Net(n_states, n_actions, n_hidden), Net(n_states, n_actions, n_hidden)
        self.version = version
        self.memory = np.zeros((memory_capacity, n_states * 2 + 2)) # 每個 memory 中的 experience 大小為 (state + next state + reward + action)
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=lr)
        self.loss_func = nn.MSELoss()
        self.memory_counter = 0
        self.learn_step_counter = 0 # 讓 target network 知道什麼時候要更新

        self.n_states = n_states
        self.n_actions = n_actions
        self.n_hidden = n_hidden
        self.batch_size = batch_size
        self.lr = lr
        self.epsilon = epsilon
        self.gamma = gamma
        self.target_replace_iter = target_replace_iter
        self.memory_capacity = memory_capacity
    def save_params(self):
        # print(self.version)
        torch.save(self.eval_net.state_dict(), './DRL/net/{}/eval_net_params.pkl'.format(self.version)) 
        torch.save(self.target_net.state_dict(), './DRL/net/{}/target_net_params.pkl'.format(self.version))

    def restore_params(self):
        print(self.version)
        try: 
            # copy saved params to net
            self.eval_net.load_state_dict(torch.load('./DRL/net/{}/eval_net_params.pkl'.format(self.version)))
            self.target_net.load_state_dict(torch.load('./DRL/net/{}/target_net_params.pkl'.format(self.version)))
        except:
            print("New net")
            torch.save(self.eval_net.state_dict(), './DRL/net/{}/eval_net_params.pkl'.format(self.version)) 
            torch.save(self.target_net.state_dict(), './DRL/net/{}/target_net_params.pkl'.format(self.version))

    def choose_action(self, state):
        x = torch.unsqueeze(torch.FloatTensor(state), 0)

        # epsilon-greedy
        if np.random.uniform() < self.epsilon: # 隨機
            # print("random choice")
            action = np.random.randint(0, self.n_actions)
        else: # 根據現有 policy 做最好的選擇
            # print("policy choice")
            actions_value = self.eval_net.forward(x) # 以現有 eval net 得出各個 action 的分數
            action = int(torch.max(actions_value, 1)[1].data.numpy()[0]) # 挑選最高分的 action
    
        return action

    def store_transition(self, state, action, reward, new_state):
        # 打包 experience
        transition = np.hstack((state, [action, reward], new_state))
        # 存進 memory；舊 memory 可能會被覆蓋
        index = self.memory_counter % self.memory_capacity
        self.memory[index, :] = transition
        self.memory_counter += 1


    def learn(self):
        # 隨機取樣 batch_size 個 experience
        sample_index = np.random.choice(self.memory_capacity, self.batch_size)
        b_memory = self.memory[sample_index, :]
        # A torch.Tensor is a multi-dimensional matrix containing elements of a single data type.
        b_state = torch.FloatTensor(b_memory[:, :self.n_states])
        b_action = torch.LongTensor(b_memory[:, self.n_states:self.n_states+1].astype(int))
        b_reward = torch.FloatTensor(b_memory[:, self.n_states+1:self.n_states+2])
        b_next_state = torch.FloatTensor(b_memory[:, -self.n_states:])

        # 計算現有 eval net 和 target net 得出 Q value 的落差
        q_eval = self.eval_net(b_state).gather(1, b_action) # 重新計算這些 experience 當下 eval net 所得出的 Q value
        q_next = self.target_net(b_next_state).detach() # detach 才不會訓練到 target net
        q_target = b_reward + self.gamma * q_next.max(1)[0].view(self.batch_size, 1) # 計算這些 experience 當下 target net 所得出的 Q value
        loss = self.loss_func(q_eval, q_target)

        # 誤差反向傳播
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 每隔一段時間 (target_replace_iter), 更新 target net，即複製 eval net 到 target net
        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_replace_iter == 0:
            self.target_net.load_state_dict(self.eval_net.state_dict())
    