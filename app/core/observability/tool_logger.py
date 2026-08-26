import logging

logger = logging.getLogger(__name__)


class ToolCallLogger:


    def log(
        self,
        tool_name,
        args,
        result,
    ):


        # Do not log raw arguments/results: they may contain customer or order PII.
        logger.info(
            "tool_call",
            extra={
                "tool": tool_name,
                "argument_keys": sorted(args.keys()) if isinstance(args, dict) else [],
                "result_type": type(result).__name__,
            },
        )
