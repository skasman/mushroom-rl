from dm_control import suite

from gym import spaces as gym_spaces
from mushroom.environments import Environment, MDPInfo
from mushroom.utils.spaces import *
from mushroom.utils.viewer import ImageViewer


class Mujoco(Environment):
    """
    Interface for dm_control Mujoco environments. It makes it possible to use
    every dm_control Mujoco environment just providing the necessary
    information.

    """
    def __init__(self, domain_name, task_name, horizon, gamma, dt=.01,
                 width_screen=480, height_screen=480, camera_id=0):
        """
        Constructor.

        Args:
             domain_name (str): name of the environment;
             task_name (str): name of the task of the environment;
             horizon (int): the horizon;
             gamma (float): the discount factor;
             dt (float, .01): duration of a control step;
             width_screen (int, 480): width of the screen;
             height_screen (int, 480): height of the screen;
             camera_id (int, 0): position of camera to render the environment;

        """
        # MDP creation
        self.env = suite.load(domain_name, task_name)

        # MDP properties
        action_space = self._convert_action_space(self.env.action_spec())
        observation_space = self._convert_observation_space(self.env.observation_spec())
        mdp_info = MDPInfo(observation_space, action_space, gamma, horizon)

        self._viewer = ImageViewer((width_screen, height_screen), dt)
        self._camera_id = camera_id

        super().__init__(mdp_info)

    def reset(self, state=None):
        if state is None:
            self._state = self._convert_observation(self.env.reset().observation)
        else:
            raise NotImplementedError

        return self._state

    def step(self, action):
        step = self.env.step(action)

        reward = step.reward
        self._state = self._convert_observation(step.observation)
        absorbing = step.last()

        return self._state, reward, absorbing, {}

    def render(self):
        img = self.env.physics.render(self._viewer.size[1],
                                      self._viewer.size[0],
                                      self._camera_id)
        self._viewer.display(img)

    def stop(self):
        pass

    @staticmethod
    def _convert_observation_space(observation_space):
        observation_shape = 0
        for i in observation_space:
            observation_shape += observation_space[i].shape[0]

        return Box(low=-np.inf, high=np.inf, shape=(observation_shape,))

    @staticmethod
    def _convert_action_space(action_space):
        low = action_space.minimum
        high = action_space.maximum

        return Box(low=np.array(low), high=np.array(high))

    @staticmethod
    def _convert_observation(observation):
        obs = list()
        for i in observation:
            obs.append(observation[i])

        return np.concatenate(obs)