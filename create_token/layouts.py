from borsh_construct import CStruct, U8, U16, U64, Bool, String, Option, Vec
from construct import Bytes as FixedBytes


CREATE_V1_LAYOUT = CStruct(
    "discriminator" / U8,
    "createV1Discriminator" / U8,
    "name" / String,
    "symbol" / String,
    "uri" / String,
    "sellerFeeBasisPoints" / U16,
    "creators"
    / Option(
        Vec(
            CStruct(
                "address" / FixedBytes(32),
                "verified" / Bool,
                "share" / U8,
            )
        )
    ),
    "primarySaleHappened" / Bool,
    "isMutable" / Bool,
    "tokenStandard" / U8,
    "collection"
    / Option(
        CStruct(
            "verified" / Bool,
            "key" / String,
        )
    ),
    "uses"
    / Option(
        CStruct(
            "useMethod" / String,
            "remaining" / U16,
            "total" / U16,
        )
    ),
    "collectionDetails" / Option(String),
    "ruleSet" / Option(FixedBytes(32)),
    "decimals" / Option(U8),
    "printSupply" / Option(U64),
)

METAPLEX_MINT_LAYOUT = CStruct(
"discriminator" / U8,
"mintArgs"     / CStruct(
    "type" / U8,
    "data" / CStruct(
        "amount"            / U64,
        "authorizationData" / Option(CStruct()),
        ),
    ),
)