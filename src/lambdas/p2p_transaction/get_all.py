from aws_lambda_powertools import Logger, Tracer
from core_db.services.p2p_transaction import P2PtransactionService
from core_http.BaseController import index

logger = Logger()
tracer = Tracer()

#@logger.inject_lambda_context(log_event=True)
#@tracer.capture_lambda_handler
def lambda_handler(event, context):
    return index(P2PtransactionService(), event)

