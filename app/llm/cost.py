class CostCalculator:


    def __init__(
        self,
        input_price: float = 0,
        output_price: float = 0,
    ):

        self.input_price = input_price

        self.output_price = output_price



    def calculate(
        self,
        *,
        input_tokens:int,
        output_tokens:int,
    ):


        input_cost = (
            input_tokens
            *
            self.input_price
        )


        output_cost = (
            output_tokens
            *
            self.output_price
        )


        return {

            "input_cost":
                input_cost,

            "output_cost":
                output_cost,

            "total_cost":
                input_cost
                +
                output_cost,
        }