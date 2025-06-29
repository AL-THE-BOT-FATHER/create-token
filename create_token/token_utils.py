import json
import time
from dataclasses import dataclass
from solana.rpc.api import Client
from solders.signature import  Signature # type: ignore
from solders.pubkey import Pubkey  # type: ignore

from solders.pubkey import Pubkey  # type: ignore
from solders.instruction import AccountMeta, Instruction  # type: ignore

from spl.token.instructions import (
    get_associated_token_address,
    Instruction,
)

from layouts import CREATE_V1_LAYOUT, METAPLEX_MINT_LAYOUT

METAPLEX_PROGRAM = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
SYSVAR_INSTRUCTIONS = Pubkey.from_string("Sysvar1nstructions1111111111111111111111111")
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

@dataclass
class TokenSettings:
    rpc_url: str
    payer_priv: str
    mint_priv: str
    token_supply: int
    decimal: int
    name: str
    symbol: str
    uri: str


def load_token_settings(file_path: str) -> TokenSettings:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return TokenSettings(**data)


def build_create_v1_ix(
    name: str,
    symbol: str,
    uri: str,
    creator: Pubkey,
    decimals: int,
    mint: Pubkey,
) -> Instruction:

    data = {
        "discriminator": 42,
        "createV1Discriminator": 0,
        "name": name,
        "symbol": symbol,
        "uri": uri,
        "sellerFeeBasisPoints": 0,
        "creators": [
            {
                "address": bytes(creator),
                "verified": True,
                "share": 100,
            }
        ],
        "primarySaleHappened": False,
        "isMutable": True,
        "tokenStandard": 2,
        "collection": None,
        "uses": None,
        "collectionDetails": None,
        "ruleSet": None,
        "decimals": decimals,
        "printSupply": None,
    }

    data_bytes = CREATE_V1_LAYOUT.build(data)

    metadata_pda, _ = Pubkey.find_program_address(
        [b"metadata", bytes(METAPLEX_PROGRAM), bytes(mint)],
        METAPLEX_PROGRAM,
    )

    accounts = [
        AccountMeta(pubkey=metadata_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=True, is_writable=True),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_INSTRUCTIONS, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
    ]

    return Instruction(
        program_id=METAPLEX_PROGRAM,
        accounts=accounts,
        data=bytes(data_bytes),
    )


def build_mint_ix(creator: Pubkey, mint: Pubkey, amount_lamports: int) -> Instruction:
    
    token_account = get_associated_token_address(creator, mint)

    metadata_pda, _ = Pubkey.find_program_address(
        [b"metadata", bytes(METAPLEX_PROGRAM), bytes(mint)],
        METAPLEX_PROGRAM,
    )

    accounts = [
        AccountMeta(pubkey=token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=metadata_pda, is_signer=False, is_writable=True),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=mint, is_signer=True, is_writable=True),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=creator, is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYSVAR_INSTRUCTIONS, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ATA_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False),
        AccountMeta(pubkey=METAPLEX_PROGRAM, is_signer=False, is_writable=False)
    ]

    data = {
        "discriminator": 43,
        "mintArgs": {
            "type": 0,
            "data": {
                "amount": amount_lamports,
                "authorizationData": None,
            },
        },
    }

    data_bytes = METAPLEX_MINT_LAYOUT.build(data)

    return Instruction(
        program_id=METAPLEX_PROGRAM,
        accounts=accounts,
        data=bytes(data_bytes),
    )


def confirm_txn(client: Client, txn_sig: Signature, max_retries: int = 20, retry_interval: int = 3) -> bool:
    retries = 1
    
    while retries < max_retries:
        try:
            txn_res = client.get_transaction(txn_sig, encoding="json", commitment="confirmed", max_supported_transaction_version=0)
            txn_json = json.loads(txn_res.value.transaction.meta.to_json())
            
            if txn_json['err'] is None:
                print("Transaction confirmed... try count:", retries)
                return True
            
            print("Error: Transaction not confirmed. Retrying...")
            if txn_json['err']:
                print("Transaction failed.")
                return False
        except Exception as e:
            print("Awaiting confirmation... try count:", retries)
            retries += 1
            time.sleep(retry_interval)
    
    print("Max retries reached. Transaction confirmation failed.")
    return None