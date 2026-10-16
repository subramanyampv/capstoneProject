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
    mode = st.radio("Answer mode", ["Rule baseline", "LLM experiment", "Support agent"], horizontal=True)
    variant = "C"
    if mode == "LLM experiment":
        with st.expander("Experiment settings"):
            variant = st.selectbox("Experimental prompt", ["C", "B", "A"], help="v3 selects C for development; final safety gates remain open.")
    if mode == "Support agent":
        from capstone_agent.support.registry import SessionIdentity
        from capstone_agent.support.runtime import MEMORY
        customer = st.selectbox("Synthetic account", ["C-100", "C-101", "C-102", "C-103"])
        st.caption("Test records only · demo date 12 Oct 2026. Handoffs create local mock tickets; refunds, returns and cancellations are not executed. Session context expires after 30 minutes of inactivity. Records are checked again for every answer.")
        if ("support_identity" not in st.session_state or st.session_state.support_identity.customer_id != customer):
            if 'support_identity' in st.session_state:MEMORY.reset(st.session_state.support_identity)
            st.session_state.pop('feedback_customer',None)
            st.session_state.support_identity = SessionIdentity(customer)
        if st.button("New support session"):
            MEMORY.reset(st.session_state.support_identity)
            st.session_state.pop("feedback_customer",None)
            st.session_state.support_identity = SessionIdentity(customer)
            st.info("New session started.")
        st.caption("Style learning is off until you enable it or submit feedback. Two matching signals in the recent ten can adjust length or format. Preferences persist locally per synthetic customer. Reset style and clear session memory are separate actions.")
        from capstone_agent.support.runtime import run_support
        with st.expander("Response style and feedback"):
            for label, command in [("Enable style learning", "/feedback enable"),
                                   ("Disable style learning", "/feedback disable"),
                                   ("Reset style", "/feedback reset_style"),
                                   ("Delete preferences", "/forget-preferences")]:
                if st.button(label):
                    try:
                        updated=run_support(command,identity=st.session_state.support_identity)
                        st.info(updated['response']['answer'])
                    except Exception:st.error("Style settings could not be updated. Please try again.")
    with st.form("question_form", clear_on_submit=True):
        message = st.text_area("How can we help?", placeholder="Can I return order O-1001?", max_chars=2000)
        submitted = st.form_submit_button("Get answer", type="primary")
    if submitted and message.strip():
        try:
            if mode == "Rule baseline":
                result = baseline_respond(message, today=date(2026, 10, 12))
                # Minimize before rendering; no transcript persistence or caching.
                st.write(sanitize(result.response))
                st.caption(f"{result.intent} · {result.latency_ms} ms")
            elif mode == "Support agent":
                st.session_state.pop("support_last",None)
                st.session_state.pop("feedback_customer",None)
                from capstone_agent.retrieval.embeddings_voyage import VoyageNanoEmbeddings
                from capstone_agent.retrieval.chroma_store import PolicySearch
                from capstone_agent.support.runtime import run_support
                @st.cache_resource
                def local_policy_search():
                    search = PolicySearch(VoyageNanoEmbeddings())
                    search.search('return policy')
                    return search
                with st.spinner("Checking records and policy evidence…"):
                    result = run_support(message, identity=st.session_state.support_identity, search=None if message.strip().startswith(("/reset","/feedback","/forget-preferences")) else local_policy_search())
                st.session_state.support_last={"session":st.session_state.support_identity.session_id,
                    "response":result['response'],"outcome":result['outcome'],"style":result.get('style',{})}
                if result["outcome"]!="COMMAND_HANDLED":st.session_state.feedback_customer=customer
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
            st.error("The answer could not be confirmed. Check the local settings or contact retailer support directly.")

    if mode=="Support agent":
        previous=st.session_state.get('support_last',{})
        if previous.get('session')==st.session_state.support_identity.session_id:
            result=previous
            draft = result["response"]
            st.write(draft["answer"])
            if draft["why"]:
                with st.expander("Why this answer?"):
                    for reason in draft["why"]: st.write(reason)
            if draft["citations"]:
                with st.expander("Sources"):
                    for ref in draft["citations"]:
                        st.write(f"{ref['source_id']} · {ref.get('section') or ''} · {ref.get('record_version') or ''}")
            for step in draft["next_steps"]: st.write(step)
            st.caption(result["outcome"].replace("_", " ").capitalize())
            if result.get('style'):
                st.caption(f"Style version {result['style'].get('version',0)} · {result['style'].get('verbosity','standard')} · {('step_by_step' if result['style'].get('format')=='step_by_step' else 'bullets' if result['style'].get('verbosity')=='concise' else result['style'].get('format','prose'))}")
    if mode=='Support agent' and st.session_state.get('feedback_customer') == customer:
        for label, signal in [("Too long", "too_long"), ("Too short", "too_short"),
                              ("Unclear", "unclear"), ("Helpful", "helpful"), ("Not helpful", "not_helpful")]:
            if st.button(label):
                try:
                    updated=run_support('/feedback '+signal,identity=st.session_state.support_identity)
                    st.info(updated['response']['answer'])
                except Exception:st.error("Feedback could not be saved. Please try again.")

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
    st.caption("Phase 3 experiment traces are below. Support-agent records contain a content-free node/model/tool hierarchy, counters and tool status. Hosted delivery receipts are shown when tracing is enabled.")
    export_log=ROOT/'data/runtime/trace_exports.jsonl'
    if export_log.exists():
        try:st.dataframe([json.loads(line) for line in export_log.read_text().splitlines()[-10:]],width='stretch')
        except (OSError,ValueError):st.info('Trace delivery status unavailable.')
    support_log = ROOT / "data/runtime/requests.jsonl"
    if support_log.exists():
        try:
            support_records = [json.loads(line) for line in support_log.read_text().splitlines()[-30:]]
            st.dataframe([{k: row.get(k) for k in ["request_ref", "outcome", "model_calls", "tool_calls", "latency_ms", "ticket_id"]} for row in support_records], width="stretch")
            with st.expander('Routing timeline (metadata only)'):
                scoped=[row for row in support_records if row.get('spans')]
                if scoped:
                    selected_trace=st.selectbox('Request trace',scoped,format_func=lambda row:row['request_ref'])
                    st.dataframe([{key:span.get(key) for key in ['name','run_type','id','parent_run_id','start_time','end_time','outputs']}
                        for span in selected_trace['spans']],width='stretch')
                else:st.info('No final-agent routing spans recorded yet.')
        except (OSError, ValueError):
            st.info("Local support records are unavailable.")
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
