from typing import Dict, Any


CHAINS: Dict[str, Dict[str, Any]] = {
    "ethereum": {
        "chain_id": 1,
        "dexscreener_id": "ethereum",
        "zerox_base": "https://api.0x.org",
        "tokens": {
            "ETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
            "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        },
    },
    "arbitrum": {
        "chain_id": 42161,
        "dexscreener_id": "arbitrum",
        "zerox_base": "https://arbitrum.api.0x.org",
        "tokens": {
            "ETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
            "WETH": "0x82af49447d8a07e3bd95bd0d56f35241523fbab1",
            "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
            "USDT": "0xFd086bC7CD5C481DCC9C85ebe478A1C0b69FCbb9",
            "DAI": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
        },
    },
    "polygon": {
        "chain_id": 137,
        "dexscreener_id": "polygon",
        "zerox_base": "https://polygon.api.0x.org",
        "tokens": {
            "ETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
            "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
            "USDC": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359",
            "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
            "DAI": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
        },
    },
}


def chain_cfg(chain: str) -> Dict[str, Any]:
    c = chain.lower()
    if c not in CHAINS:
        raise KeyError(f"Unsupported chain: {chain}")
    return CHAINS[c]


def resolve_token(chain: str, token: str) -> str:
    cfg = chain_cfg(chain)
    t = token.upper()
    if t in cfg["tokens"]:
        return cfg["tokens"][t]
    if token.startswith("0x") and len(token) == 42:
        return token
    raise KeyError(f"Unsupported token on {chain}: {token}")