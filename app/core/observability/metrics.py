class TokenUsage:


    def __init__(self):

        self.input_tokens = 0

        self.output_tokens = 0



    def record(
        self,
        input_tokens,
        output_tokens,
    ):


        self.input_tokens += (
            input_tokens
        )


        self.output_tokens += (
            output_tokens
        )



    def total(self):

        return {

            "input":
            self.input_tokens,


            "output":
            self.output_tokens,

        }