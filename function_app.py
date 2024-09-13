import json
import logging

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing?view=aspnetcore-8.0#route-templates
@app.route(
    route="log-cognigy-llm-request/{**path}",
    methods=["GET", "POST", "PATCH"],
)
# https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-expressions-patterns
@app.blob_output(
    arg_name="outblob",
    path="cognigy-llm-requests/{DateTime}.json",
    connection="AzureWebJobsStorage",
)
def log_cognigy_llm_request(
    req: func.HttpRequest, outblob: func.Out[str]
) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    body = None
    try:
        body = req.get_json()
        logging.info("Request body was JSON: %s.", type(body))
    except ValueError:
        body = req.get_body().decode("utf-8")
        logging.info("Request body was NOT JSON.")

    req_info = {
        "method": req.method,
        "headers": dict(req.headers.items()),
        "path": req.route_params.get("path"),
        "query_params": dict(req.params.items()),
        "body": body,
    }

    outblob.set(json.dumps(req_info, ensure_ascii=False, indent=2))
    return func.HttpResponse(
        json.dumps(req_info), headers={"content-type": "application/json"}
    )
