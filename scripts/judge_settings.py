"""Independent judge settings and explicit compatible transport options."""
from dataclasses import dataclass
from capstone_agent.config import LLMConfig,ConfigurationError


@dataclass(frozen=True)
class JudgeConfig(LLMConfig):
    thinking_format:str='flag'

    def __post_init__(self):
        super().__post_init__()
        if self.thinking_format not in {'flag','type_object'}:
            raise ConfigurationError('INVALID_JUDGE_THINKING_FORMAT')

    def public_settings(self):
        return {**super().public_settings(),'thinking_format':self.thinking_format}


def configured_judge(app,env):
    thinking=env.get('JUDGE_ENABLE_THINKING','').strip().lower()
    if thinking not in {'','true','false'}:raise ConfigurationError('INVALID_JUDGE_THINKING')
    return JudgeConfig(base_url=env.get('JUDGE_BASE_URL',''),model=env.get('JUDGE_MODEL',''),api_key=env.get('JUDGE_API_KEY',''),
        timeout_seconds=float(env.get('JUDGE_TIMEOUT_SECONDS','60')),
        max_completion_tokens=int(env.get('JUDGE_MAX_COMPLETION_TOKENS','2400')),
        max_retries=0,temperature=0,response_format=env.get('JUDGE_RESPONSE_FORMAT','json_object'),
        enable_thinking=None if not thinking else thinking=='true',
        thinking_format=env.get('JUDGE_THINKING_FORMAT','flag').strip())


def configure_transport(client,config):
    # Select a request dialect explicitly; endpoint identity is not a dialect.
    # Omitted thinking never sends a toggle, irrespective of selected format.
    if config.enable_thinking is not None and getattr(config,'thinking_format','flag')=='type_object':
        client.chat.extra_body={'thinking':{'type':'enabled' if config.enable_thinking else 'disabled'}}
    return client
