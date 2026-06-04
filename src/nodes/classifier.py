from ..graph import GraphState
from ..llm import get_llm
from ..loader import CLASSIFIER_PROMPT
from ..utils import parse_llm_json
import time
from ..usg import print_token_usage


def classify_question(state: GraphState) -> GraphState:
    start_time = time.time()
    print(f"\n--- [NODE: CLASSIFIER] ---")
    print(f"Question: {state.get('question')}")    
    llm = get_llm()

    conversation_context = state.get("conversation_context", {"history": []})

    if conversation_context["history"]:
        context_str = str(conversation_context)
    else:
        context_str = "None"

    prompt = CLASSIFIER_PROMPT.format(
        schema_context=state["schema_context"],
        conversation_context=context_str,
        question=state["question"]
    )

    response = llm.invoke(prompt)
    print_token_usage(response)
    content = response.content

    if isinstance(content, list):

        content = "\n".join(
            str(item)
            for item in content
        )

    content = str(content)



    result = parse_llm_json(content)

    state["classification"] = result

    if result["classification"] == "ambiguous":
        state["clarifying_question"] = result["clarifying_question"]

    if result["classification"] == "out_of_scope":
        state["error"] = result["out_of_scope_reason"]

    end_time = time.time()
    print(f"Classification Time: {end_time - start_time:.2f} seconds")

    return state