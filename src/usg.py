def print_token_usage(response):

    print("\n=== TOKEN USAGE ===")

    usage = None

    if hasattr(response, "usage_metadata"):

        usage = response.usage_metadata

    elif hasattr(response, "response_metadata"):

        usage = response.response_metadata.get(
            "token_usage",
            {}
        )

    if not usage:

        print(
            "Token usage metadata "
            "not available."
        )

        return

    input_tokens = (
        usage.get("input_tokens")
        or usage.get("prompt_tokens")
        or usage.get("inputTokenCount")
        or 0
    )

    output_tokens = (
        usage.get("output_tokens")
        or usage.get("completion_tokens")
        or usage.get("outputTokenCount")
        or 0
    )

    total_tokens = (
        usage.get("total_tokens")
        or (
            input_tokens + output_tokens
        )
    )

    print(
        f"Input Tokens: "
        f"{input_tokens}"
    )

    print(
        f"Output Tokens: "
        f"{output_tokens}"
    )

    print(
        f"Total Tokens: "
        f"{total_tokens}"
    )
