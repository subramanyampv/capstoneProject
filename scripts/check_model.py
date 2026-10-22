"""Credential-safe provider preflight before an expensive evaluation run."""
import argparse
import asyncio
import json
from pathlib import Path
from langchain_core.messages import HumanMessage
from capstone_agent.config import LLMConfig,ConfigurationError,load_environment
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.model_client import ModelError
from capstone_agent.support.model import Gateway,model_error_code

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path)
    parser.add_argument('--judge',action='store_true')
    args=parser.parse_args()
    try:
        config=LLMConfig.from_env(ROOT/'.env')
        if args.judge:
            from judge_settings import configured_judge
            config=configured_judge(config,load_environment(ROOT/'.env'))
        with LangChainChatClient(config) as client:
            if args.judge:
                from judge_settings import configure_transport
                configure_transport(client,config)
            reply=asyncio.run(Gateway(client.chat,timeout=min(config.timeout_seconds+1,30)).invoke(
                [HumanMessage(content='Reply with the single word ready.')]))
        report={'model_preflight':'passed','tokens':(reply.usage_metadata or {}).get('total_tokens',0)}
    except ModelError as exc:
        report={'model_preflight':'failed','category':model_error_code('MODEL',exc),
            'retryable':exc.retryable,'http_status':getattr(exc,'status_code',None)}
    except (ConfigurationError,ValueError):
        report={'model_preflight':'failed','category':'CONFIGURATION_INVALID','retryable':False}
    encoded=json.dumps(report,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(encoded)
    print(encoded,end='')
    return 0 if report['model_preflight']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
