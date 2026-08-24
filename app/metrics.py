from prometheus_client import Counter



REQUEST_COUNT = Counter(

"api_request_total",

"Total requests"

)