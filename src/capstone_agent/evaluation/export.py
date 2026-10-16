"""Minimize textual evidence before serialization, preserving numeric JSON types."""
import json
from capstone_agent.support.privacy import minimize


def minimized_json(value, secrets=()):
    def clean(item):
        if isinstance(item,str):return minimize(item,secrets)
        if isinstance(item,list):return [clean(part) for part in item]
        if isinstance(item,dict):return {minimize(key,secrets):clean(part) for key,part in item.items()}
        return item
    return json.dumps(clean(value),allow_nan=False)
