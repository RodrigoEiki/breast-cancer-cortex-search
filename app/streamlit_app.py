from typing import Dict, List

import streamlit as st
from snowflake.snowpark.context import get_active_session

from src.snowflake.cortex import (
    build_filter,
    generate_answer,
    search_context,
    source_label,
)


DEFAULT_MODEL = "mistral-large2"
DEFAULT_CHUNK_LIMIT = 8

DOCUMENT_TYPE_LABELS = {
    "Clinical guidelines": "clinical_guidance",
    "Screening recommendations": "screening_recommendation",
    "Statistics": "statistics",
    "Clinical trials": "clinical_trial",
    "Research studies": "research_abstract",
}

TOPIC_LABELS = {
    "General overview": "overview",
    "Treatment": "treatment",
    "Screening": "screening",
    "Prevention": "prevention",
    "Genetics": "genetics",
    "Statistics & trends": "epidemiology",
    "Clinical trials": "clinical_trials",
    "Latest research": "research",
}

SOURCE_TIER_LABELS = {
    "Authoritative (NCI, USPSTF, SEER)": 1,
    "Supplementary (PubMed)": 2,
}


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


@st.cache_resource
def active_session():
    return get_active_session()


def render_sources(results: List[Dict]) -> None:
    st.subheader("Sources")
    for index, result in enumerate(results, start=1):
        with st.expander(source_label(result, index)):
            url = result.get("SOURCE_URL")
            if url:
                st.link_button("Open source", url)
            st.caption(
                " | ".join(
                    value
                    for value in [
                        result.get("SOURCE_NAME"),
                        result.get("DOCUMENT_TYPE"),
                        result.get("TOPIC"),
                        f"Tier {result.get('SOURCE_TIER')}" if result.get("SOURCE_TIER") else None,
                    ]
                    if value
                )
            )
            st.write(result.get("CONTENT", ""))


def sidebar_controls():
    with st.sidebar:
        st.header("Filters")

        selected_types = st.multiselect(
            "Type of evidence",
            list(DOCUMENT_TYPE_LABELS.keys()),
            help="Narrow results to specific kinds of sources.",
        )
        selected_topics = st.multiselect(
            "Focus area",
            list(TOPIC_LABELS.keys()),
            help="Limit results to a particular medical topic.",
        )
        selected_tiers = st.multiselect(
            "Source quality",
            list(SOURCE_TIER_LABELS.keys()),
            help="Authoritative sources are official guidelines; supplementary includes journals and societies.",
        )

        st.divider()
        st.caption("This app is for research and evidence exploration. It is not medical advice.")
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()

    document_types = [DOCUMENT_TYPE_LABELS[label] for label in selected_types]
    topics = [TOPIC_LABELS[label] for label in selected_topics]
    source_tiers = [SOURCE_TIER_LABELS[label] for label in selected_tiers]
    return DEFAULT_MODEL, DEFAULT_CHUNK_LIMIT, build_filter(document_types, topics, source_tiers)


def main() -> None:
    st.set_page_config(page_title="Breast Cancer Evidence Search", layout="wide")
    init_state()
    session = active_session()
    model, result_limit, filters = sidebar_controls()

    st.title("Breast Cancer Evidence Search")
    st.caption("Ask questions across NCI/PDQ, USPSTF, SEER, ClinicalTrials.gov, and PubMed.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("sources"):
                render_sources(message["sources"])

    question = st.chat_input("Ask about breast cancer evidence, trials, screening, or research")
    if not question:
        return

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching indexed sources"):
            results, fallback_error = search_context(session, question, result_limit, filters)
            if fallback_error:
                st.caption(f"Using SQL search preview fallback: {fallback_error}")

        if not results:
            answer = "I did not find relevant indexed context for that question."
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": []})
            return

        with st.spinner("Generating grounded answer"):
            answer = generate_answer(session, model, question, results)

        st.write(answer)
        render_sources(results)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": results}
        )


if __name__ == "__main__":
    main()
