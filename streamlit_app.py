"""Local Python UI; framework orchestration lives in the application modules."""

import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

from capstone_agent.baseline_agent import respond as baseline_respond
from capstone_agent.config import LLMConfig, show_deferred_ui
from capstone_agent.langchain_client import LangChainChatClient
from capstone_agent.llm_agent import respond
from capstone_agent.observability.langsmith_tracing import ObservabilityConfig
from capstone_agent.safety.redaction import sanitize

ROOT = Path(__file__).resolve().parent
TODAY = datetime.now(ZoneInfo("America/New_York")).date()
st.set_page_config(page_title="Support desk", page_icon="◈", layout="wide")
st.title("Support desk")
st.caption("Synthetic e-commerce support · clear answers, cited evidence, human review when needed")
deferred = show_deferred_ui(ROOT / ".env")
tabs = st.tabs(["Chat", "Evaluation", "Traces"] + (["Knowledge", "Delivery estimate"] if deferred else []))
chat, evaluation, traces = tabs[:3]
if deferred:
    knowledge, delivery = tabs[3:]
    from capstone_agent.domain.delivery_estimate import DeliveryFacts, estimate_delivery
    from capstone_agent.retrieval.knowledge_graph import KnowledgeGraph
    from capstone_agent.tools.external_facts import route_distance, weather_alerts

with chat:
    mode = st.radio("Answer mode", ["Rule baseline", "LLM experiment"], horizontal=True)
    variant = "C"
    if mode == "LLM experiment":
        with st.expander("Experiment settings"):
            variant = st.selectbox("Experimental prompt", ["C", "B", "A"], help="v3 selects C for development; final safety gates remain open.")
    with st.form("question_form"):
        message = st.text_area("How can we help?", placeholder="Can I return order O-1001?", max_chars=2000)
        submitted = st.form_submit_button("Get answer", type="primary")
    if submitted and message.strip():
        try:
            if mode == "Rule baseline":
                result = baseline_respond(message, today=date(2026, 10, 12))
                # Minimize before rendering; no transcript persistence or caching.
                st.write(sanitize(result.response))
                st.caption(f"{result.intent} · {result.latency_ms} ms")
            else:
                config = LLMConfig.from_env(ROOT / ".env")
                obs = ObservabilityConfig.from_env(ROOT / ".env")
                with st.spinner("Reviewing your question…"), LangChainChatClient(config) as client:
                    result = respond(message, client, variant=variant,
                                     today=date(2026, 10, 12), secrets=(config.api_key, obs.api_key), observability=obs)
                if result.response:
                    st.write(result.response["response"])
                    if result.response["uncertainty"]:
                        st.info(result.response["uncertainty"])
                    st.caption(f"{result.response['status']} · {result.latency_ms / 1000:.1f}s")
                    with st.expander("Sources and request status"):
                        st.write("No verified evidence available in the Phase 3 experiment.")
                        st.write("Request ID: " + result.request_id)
                        st.write("Workflow: " + " → ".join(result.graph_steps or []))
                else:
                    st.error("The answer could not be verified. Please try again later.")
        except Exception:
            st.error("Configuration or service unavailable. Check the local settings; no action was performed.")

with evaluation:
    st.subheader("Recorded experiments")
    runs = sorted([p for p in (ROOT / "artifacts/prompt_runs").glob("*") if (p / "summary.json").exists()], reverse=True)
    if runs:
        selected = st.selectbox("Run", runs, format_func=lambda p: p.name)
        summary = json.loads((selected / "summary.json").read_text())
        st.json(summary)
        report = selected / "deepeval_results.json"
        if report.exists():
            metrics = json.loads(report.read_text())
            st.caption("DeepEval checks; semantic quality and hard safety gates remain separate.")
            st.dataframe([{"case": row["case_id"], "prompt": row["prompt"], "metric": metric["name"],
                           "score": metric["score"], "pass": metric["pass"]}
                          for row in metrics["results"] for metric in row["metrics"]], width="stretch")
    else:
        st.info("No experiments recorded yet.")

with traces:
    st.subheader("Recorded request traces")
    st.caption("Phase 3 has a single-agent workflow. v3 supervisor/specialist/tool traces arrive in Phase 5.")
    if runs and (selected / "outputs.jsonl").exists():
        records = [json.loads(line) for line in (selected / "outputs.jsonl").read_text().splitlines()]
        st.dataframe([{"request_id": row["request_id"], "case": row["case_id"],
                       "prompt": row["prompt_variant"], "status": row["outcome"],
                       "model_calls": row["model_calls"], "latency_ms": row["latency_ms"],
                       "steps": " → ".join(row.get("graph_steps") or []),
                       "error": row.get("error_category")} for row in records], width="stretch")
    else:
        st.info("No request traces recorded yet.")

if deferred:
    with knowledge:
        graph = KnowledgeGraph.from_fixtures()
        st.subheader("Products and categories")
        selected = st.selectbox("Product", [p for p in graph.nodes if graph.nodes[p]["kind"] == "product"],
                                format_func=lambda p: graph.nodes[p]["label"])
        st.json(graph.neighborhood(selected))
        st.caption("Graph relationships retain source/version provenance. Policy passages will be linked after ingestion.")

    with delivery:
        st.subheader("Rule-based delivery estimate")
        st.caption("Demo rules: 1,000 miles ≈ 3 calendar days; storm/snow adds 2 days. Estimates are not guarantees.")
        use_api = st.radio("Distance and weather source", ["Manual demo", "Public API facts"], horizontal=True) == "Public API facts"
        with st.form("delivery_form"):
            if use_api:
                st.caption("Submitting sends these city-centre coordinates to OSRM and NWS. Avoid personal addresses.")
                origin_lat = st.number_input("Origin latitude", min_value=-90.0, max_value=90.0, value=40.7128, format="%.4f")
                origin_lon = st.number_input("Origin longitude", min_value=-180.0, max_value=180.0, value=-74.0060, format="%.4f")
                dest_lat = st.number_input("Destination latitude", min_value=-90.0, max_value=90.0, value=39.7392, format="%.4f")
                dest_lon = st.number_input("Destination longitude", min_value=-180.0, max_value=180.0, value=-104.9903, format="%.4f")
            destination = st.text_input("Destination city or postal code", "Denver, CO", max_chars=100)
            distance, weather = None, "unknown"
            if not use_api:
                distance = st.number_input("Sourced route distance (miles)", min_value=0.0, max_value=25000.0, value=1000.0)
                weather = st.selectbox("Sourced weather condition", ["clear", "storm", "snow", "storm_and_snow", "unknown"])
            dispatched = st.date_input("Dispatch date", value=date(2026, 10, 12))
            calculate = st.form_submit_button("Estimate delivery", type="primary")
        if calculate:
            try:
                distance_source = "manual synthetic demo"
                weather_source = "manual synthetic demo" if weather != "unknown" else None
                if use_api:
                    route = route_distance(origin_lat, origin_lon, dest_lat, dest_lon)
                    alerts = weather_alerts(dest_lat, dest_lon)
                    distance, distance_source = route["distance_miles"], route["source"]
                    weather, weather_source = alerts["weather"], alerts["source"]
                facts = DeliveryFacts(destination=destination, dispatch_date=dispatched, distance_miles=distance,
                                      weather=weather, distance_source=distance_source,
                                      weather_source=weather_source,
                                      observed_on=TODAY)
                estimate = estimate_delivery(facts, today=TODAY)
                if estimate["status"] == "estimated":
                    st.success(f"Estimated arrival: {estimate['earliest']} to {estimate['latest']}")
                else:
                    st.warning(estimate["reason"])
                with st.expander("Estimate basis"):
                    st.json(estimate)
            except ValueError:
                st.error("Check the destination, dispatch date, and source facts.")
