class ToolCallLogger:


    def log(
        self,
        tool_name,
        args,
        result,
    ):


        print(

            {
                "tool":
                tool_name,

                "args":
                args,

                "result":
                result,

            }

        )