from solana.rpc.api import Client
from solana.rpc.types import TxOpts

from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # type: ignore
from solders.keypair import Keypair  # type: ignore
from solders.message import MessageV0  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore

from spl.token.instructions import (
    AuthorityType,
    SetAuthorityParams,
    set_authority,
)

from token_utils import  load_token_settings, build_create_v1_ix, build_mint_ix, confirm_txn, TOKEN_PROGRAM_ID

def create_token(sim: bool=False):
    token_settings = load_token_settings("token.json")

    rpc_url = token_settings.rpc_url
    
    payer_priv = token_settings.payer_priv
    mint_priv = token_settings.mint_priv
    
    token_supply = token_settings.token_supply
    mint_decimal = token_settings.decimal
    
    name = token_settings.name
    symbol = token_settings.symbol
    uri = token_settings.uri
    
    client = Client(rpc_url)
    payer_keypair = Keypair.from_base58_string(payer_priv)

    mint_keypair = Keypair.from_base58_string(mint_priv)
    mint_pubkey = mint_keypair.pubkey()

    token_supply_lamports = int(token_supply * 10**mint_decimal)

    instructions = [set_compute_unit_limit(200_000), set_compute_unit_price(500_000)]

    instructions.append(
        build_create_v1_ix(
            name,
            symbol,
            uri,
            payer_keypair.pubkey(),
            mint_decimal,
            mint_pubkey,
        )
    )
    
    instructions.append(
        build_mint_ix(
            payer_keypair.pubkey(), 
            mint_pubkey, 
            token_supply_lamports
        )
    )

    instructions.append(
        set_authority(
            SetAuthorityParams(
                program_id=TOKEN_PROGRAM_ID,
                account=mint_keypair.pubkey(),
                authority=AuthorityType.MINT_TOKENS,
                current_authority=payer_keypair.pubkey(),
            )
        )
    )

    instructions.append(
        set_authority(
            SetAuthorityParams(
                program_id=TOKEN_PROGRAM_ID,
                account=mint_keypair.pubkey(),
                authority=AuthorityType.FREEZE_ACCOUNT,
                current_authority=payer_keypair.pubkey(),
            )
        )
    )

    print("Compiling transaction message...")
    compiled_message = MessageV0.try_compile(
        payer_keypair.pubkey(),
        instructions,
        [],
        client.get_latest_blockhash().value.blockhash,
    )

    if sim:
        res = client.simulate_transaction(txn=VersionedTransaction(compiled_message, [payer_keypair, mint_keypair]))
        print(res)
    else:
        print("Sending transaction...")
        txn_sig = client.send_transaction(
            txn=VersionedTransaction(compiled_message, [payer_keypair, mint_keypair]),
            opts=TxOpts(skip_preflight=False),
        ).value
        print("Transaction Signature:", txn_sig)

        print("Confirming transaction...")
        confirmed = confirm_txn(client, txn_sig)

        print("Transaction confirmed:", confirmed)
        return confirmed

