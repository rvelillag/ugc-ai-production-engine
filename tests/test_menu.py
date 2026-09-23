import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools import menu


def test_option_create_avatar_points_to_agent_guided_flow():
    source = inspect.getsource(menu.option_create_avatar)
    hint_idx = source.find("agente de código")
    first_input_idx = source.find("input(")
    assert hint_idx != -1, "option_create_avatar should mention the agent-guided flow"
    assert hint_idx < first_input_idx, "the hint must print before the first input() prompt"
