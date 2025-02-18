from core_db.BaseService import BaseService
from core_db.models.p2p_transaction import P2Ptransaction


class P2PtransactionService(BaseService):
    def __init__(self) -> None:
        super().__init__(P2Ptransaction)