from Base.TLMN import _env as env
from Base.TLMN._render import Render
import warnings
warnings.filterwarnings("ignore")

getValidActions = env.getValidActions
getActionSize = env.getActionSize
getAgentSize = env.getAgentSize
getStateSize = env.getStateSize
getReward = env.getReward
numba_main_2 = env.numba_main_2

def render(Agent, per_data, level, *args):
    list_agent, list_data = env.load_agent(level, *args)
    
    _render = Render(list_agent, list_data)

    if type(Agent) == str and Agent.lower() == "human":
        pass
    else:
        _render.review_agent(Agent, per_data)
        pass

    return _render.display()