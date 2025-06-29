from solana.rpc.api import Client
from solders.keypair import Keypair # type: ignore
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey # type: ignore
from spl.token.instructions import burn, close_account, BurnParams, CloseAccountParams
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit # type: ignore

from solders.message import MessageV0  # type: ignore
from solders.pubkey import Pubkey  # type: ignore
from solders.transaction import VersionedTransaction # type: ignore
from spl.token.instructions import get_associated_token_address

from token_utils import load_token_settings  # type: ignore


def burn_and_close_account(client: Client, payer_keypair: Keypair, token_account: Pubkey):
    print("Token Account:", token_account)

    try:
        token_balance = int(client.get_token_account_balance(token_account).value.amount)
        print("Token Balance:", token_balance)
    except:
        token_balance = 0
        print("Token Balance:", token_balance)

    owner = payer_keypair.pubkey()
    instructions = []

    program_id = None
    mint = None 
    if token_balance > 0:
        data = client.get_account_info_json_parsed(token_account).value
        program_id = data.owner
        mint = Pubkey.from_string(data.data.parsed["info"]["mint"])
        burn_instruction = burn(
            BurnParams(
                program_id=program_id,
                account=token_account,
                mint=mint,
                owner=owner,
                amount=token_balance,
            )
        )

        instructions.append(burn_instruction)

    close_account_instruction = close_account(
        CloseAccountParams(
            program_id=program_id,
            account=token_account,
            dest=owner,
            owner=owner,
        )
    )
    instructions.append(set_compute_unit_price(100_000))
    instructions.append(set_compute_unit_limit(100_000))
    instructions.append(close_account_instruction)

    print("Compiling transaction message...")
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],
        client.get_latest_blockhash().value.blockhash,
    )

    txn = VersionedTransaction(compiled_message, [payer_keypair])

    print("Sending transaction...")
    txn_sig = client.send_transaction(txn=txn, opts=TxOpts(skip_preflight=True)).value
    print("Transaction Signature:", txn_sig)


if __name__ == "__main__":
    token_settings = load_token_settings("token.json")

    rpc_url = token_settings.rpc_url
    payer_priv = token_settings.payer_priv
    mint_priv = token_settings.mint_priv

    client = Client(rpc_url)
    payer_keypair = Keypair.from_base58_string(payer_priv)
    mint = Keypair.from_base58_string(mint_priv).pubkey()
    
    token_account = get_associated_token_address(payer_keypair.pubkey(), mint)
    burn_and_close_account(client, payer_keypair, token_account)