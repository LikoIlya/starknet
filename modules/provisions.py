import decimal
import json
import os
import random
from typing import TypedDict

from regex import P

from loguru import logger

from utils.gas_checker import check_gas
from utils.helpers import retry
from utils.sleeping import sleep
from . import Starknet
from starknet_py.net.models import parse_address
from config import STARKNET_CLAIM_CONTRACT, STARKNET_CLAIM_ABI, STARKNET_TOKENS

class EligibilityData(TypedDict):
    identity: str
    amount: int


def retrieve_provisions():
    provisions: list[EligibilityData] = []

    for t in provisions.keys():
        folder_path = "../data/provisions"
        if os.path.exists(folder_path):
            files = os.listdir(folder_path)
            for file in files:
                if file.endswith(".json"):
                    with open(os.path.join(folder_path, file), "r") as f:
                        provision = json.load(f)
                        provisions += provision["eligibles"]

    return provisions

PROVISIONS = retrieve_provisions()

class StarkProvisions(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account)
        self.contract = self.get_contract(STARKNET_CLAIM_CONTRACT, STARKNET_CLAIM_ABI, cairo_version=1)

    @staticmethod
    def get_provision_balance(identity: int):
        balance = None
        decimals = 18
        try:
            balance = next(
                (
                    int(x["amount"] * (10)**decimals)
                    for data in PROVISIONS
                    for x in data
                    if parse_address(x["identity"]) == identity
                )
            )
        except StopIteration:
            logger.info(f"Identity {identity} not found in provisions")
        finally:
            return balance

    @retry
    @check_gas("starknet")
    async def claim_provision(self, index: int, mercle_path: list[int]):
        logger.info(f"[{self._id}][{hex(self.address)}] Claiming token with index {index}")

        claim_call = self.contract.functions["claim"].prepare(
            self.address,
            self.get_provision_balance(self.address),
            index,
            mercle_path,
        )

        transaction = await self.sign_transaction([claim_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
