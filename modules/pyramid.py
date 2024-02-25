import random

from loguru import logger

from config import PYRAMID_CONTRACT, PYRAMID_ABI, STARKNET_TOKENS
from utils.gas_checker import check_gas
from utils.helpers import retry
from . import Starknet


class Pyramid(Starknet):
    def __init__(self, _id: int, private_key: str, type_account: str, proxy=None) -> None:
        super().__init__(_id=_id, private_key=private_key, type_account=type_account, proxy=proxy)
        self.contract = self.get_contract(PYRAMID_CONTRACT, PYRAMID_ABI)

    async def get_mint_cost(self):
        fee = await self.contract.functions["returnMintCost"].call(block_number="latest")

        return fee.cost

    @retry
    @check_gas("starknet")
    async def mint(self):
        logger.info(f"[{self._id}][{hex(self.address)}] Mint NFT on Pyramid")

        mint_id = random.randint(11111111111111111111, 999999999999999999999)
        fee_cost = await self.get_mint_cost()

        approve_contract = self.get_contract(STARKNET_TOKENS["ETH"])

        approve_call = approve_contract.functions["approve"].prepare_invoke_v1(
            PYRAMID_CONTRACT,
            fee_cost
        )

        mint_call = self.contract.functions["mint"].prepare_invoke_v1(
            mint_id
        )

        transaction = await self.sign_transaction([approve_call, mint_call])

        transaction_response = await self.send_transaction(transaction)

        await self.wait_until_tx_finished(transaction_response.transaction_hash)
