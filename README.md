# create-token

Create an SPL token with Metaplex.

Configure `token.json` with your info and run `main.py`.

**Config Options**  
- `rpc_url`: Solana RPC endpoint URL  
- `payer_priv`: Base58-encoded payer private key  
- `mint_priv`: Base58-encoded mint private key  
- `token_supply`: Total supply in normal units (not lamports)  
- `decimal`: Number of decimals (e.g., `6` means the base unit is 10⁻⁶)  
- `name`: Token name  
- `symbol`: Token symbol (ticker)  
- `uri`: Token metadata URI (use IPFS services like Pinata or QuickNode)

```json
{
    "rpc_url": "",
    "payer_priv": "",
    "mint_priv": "",
    "token_supply": 1000000000,
    "decimal": 6,
    "name": "",
    "symbol": "",
    "uri": ""
}
