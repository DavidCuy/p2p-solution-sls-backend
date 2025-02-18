from http import HTTPStatus

from core_api.responses import api_response
from core_decorators import requester_patch
from core_utils.utils import get_logger, get_body
from core_decorators.logs import lambda_logger
from playhouse.shortcuts import model_to_dict

from core_db.models import P2Ptransaction

requester_patch()
LOGGER = get_logger()


@lambda_logger(logger=LOGGER)
def lambda_handler(event: dict, _):
    records = event.get("Records")
    if records is None:
        LOGGER.info("No records founded")
        return {
            "error": True,
            "message": "No records founded"
        }
    
    trxs = []
    for record in records:
        body = get_body(record)
        LOGGER.info(f'{20 * '*'}  Processing banking request  {20 * '*'}')

        trx_reg = P2Ptransaction.get_by_id(body.get('id', None))
        LOGGER.info(trx_reg)
        if 'error' in body:
            return api_response({
                "error": True,
                "message": "Something goes wrong"
            }, HTTPStatus.OK)
        
        trx_reg.status = 'done'
        trx_reg.save()
        trxs.append(model_to_dict(trx_reg))
    return api_response({
                "message": "OK",
                "transactions": trxs
            }, HTTPStatus.OK)