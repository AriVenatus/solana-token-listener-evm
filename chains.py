"""Shared blockchain/chain-config definitions and helpers used by main.py and token_tracker.py."""
import os
import re
import shutil
from pathlib import Path

SOLANA_CA_PATTERN = r'[1-9A-HJ-NP-Za-km-z]{32,44}'   # base58, no 0/O/I/l
EVM_CA_PATTERN = r'0x[a-fA-F0-9]{40}'

# Preset EVM chains. `chain_id` is display-only. `dexscreener_slug` and
# `geckoterminal_network` are best-effort / not fully verified for brand-new
# chains (e.g. Robinhood Chain) - code must degrade gracefully if wrong
# (see get_evm_link_patterns / TokenTracker._get_current_mcap_evm).
EVM_CHAINS = {
    'robinhood': {
        'name': 'Robinhood Chain', 'chain_id': 4663,
        'explorer': 'https://robinhoodchain.blockscout.com',
        'dexscreener_slug': 'robinhood',        # confirmed via dexscreener.com/robinhood listing page
        'geckoterminal_network': None,          # unknown/likely unsupported yet - GeckoTerminal backup skipped
    },
    'ethereum': {
        'name': 'Ethereum', 'chain_id': 1,
        'explorer': 'https://etherscan.io',
        'dexscreener_slug': 'ethereum',
        'geckoterminal_network': 'eth',
    },
    'base': {
        'name': 'Base', 'chain_id': 8453,
        'explorer': 'https://basescan.org',
        'dexscreener_slug': 'base',
        'geckoterminal_network': 'base',
    },
    'arbitrum': {
        'name': 'Arbitrum One', 'chain_id': 42161,
        'explorer': 'https://arbiscan.io',
        'dexscreener_slug': 'arbitrum',
        'geckoterminal_network': 'arbitrum',
    },
    'bsc': {
        'name': 'BNB Chain', 'chain_id': 56,
        'explorer': 'https://bscscan.com',
        'dexscreener_slug': 'bsc',
        'geckoterminal_network': 'bsc',
    },
}

DEFAULT_CHAIN_CONFIG = {
    'chain_type': 'solana',
    'evm_chain_key': None,
    'evm_chain': None,
}


def get_ca_pattern(chain_type: str) -> str:
    """The single 'which address alphabet applies' switch used everywhere."""
    return EVM_CA_PATTERN if chain_type == 'evm' else SOLANA_CA_PATTERN


def chain_state_filename(base_name: str, chain_type: str) -> str:
    """Per-chain filename for a persisted-state file, e.g.
    chain_state_filename('processed_tokens', 'evm') -> 'processed_tokens_evm.json'.
    Solana and EVM each keep their own processed/tracked/sold-token history,
    since they're two independent forwarding pipelines."""
    suffix = 'evm' if chain_type == 'evm' else 'solana'
    return f"{base_name}_{suffix}.json"


def migrate_legacy_state_file(legacy_path, new_path, chain_type: str) -> None:
    """Seed a newly-introduced per-chain state file from the old pre-multi-chain
    shared file, the first time it's needed. Only applies to Solana - all data
    in the legacy file predates EVM support, so it's safe to treat as Solana
    history. No-op if the new file already exists or there's nothing to migrate."""
    legacy_path = Path(legacy_path)
    new_path = Path(new_path)
    if chain_type != 'solana' or new_path.exists() or not legacy_path.exists():
        return
    try:
        shutil.copy(legacy_path, new_path)
    except Exception:
        pass


def target_chat_env_var(chain_type: str) -> str:
    """Which .env variable holds the forwarding target chat for this chain
    type - Solana and EVM each forward to their own bot/chat."""
    return 'TARGET_CHAT_EVM' if chain_type == 'evm' else 'TARGET_CHAT_SOLANA'


def resolve_target_chat(chain_type: str) -> str:
    """Read + clean the appropriate TARGET_CHAT_* env var for the given chain
    type. Returns None if it isn't set."""
    value = os.getenv(target_chat_env_var(chain_type))
    if not value:
        return None
    return value.lstrip('@').strip()


def normalize_address(address: str, chain_type: str) -> str:
    """EVM checksum-case carries no address identity (unlike Solana base58,
    where case IS meaningful character data) - lowercase EVM addresses at the
    extraction boundary so dict keys / dedupe sets stay consistent regardless
    of which checksum casing a given message happened to use."""
    if not address:
        return address
    return address.lower() if chain_type == 'evm' else address


def get_evm_link_patterns(evm_chain: dict) -> list:
    """Regex patterns (one capture group each) for a CA embedded in a
    dexscreener or block-explorer link, given the configured evm_chain
    preset/custom dict. Missing fields are silently skipped - callers append
    a raw 0x... fallback themselves."""
    evm_chain = evm_chain or {}
    addr = EVM_CA_PATTERN
    patterns = []
    slug = evm_chain.get('dexscreener_slug')
    if slug:
        patterns.append(rf'dexscreener\.com/{re.escape(slug)}/({addr})')
    explorer = evm_chain.get('explorer')
    if explorer:
        host = explorer.split('//', 1)[-1].rstrip('/')
        patterns.append(rf'{re.escape(host)}/(?:token|address)/({addr})')
    return patterns


def build_notification_links(address: str, chain_type: str, evm_chain: dict = None) -> str:
    """Quick-links block used in TokenTracker's 'Token Multiple Alert' messages."""
    if chain_type != 'evm':
        return (
            f"• Birdeye: https://birdeye.so/token/{address}\n"
            f"• DexScreener: https://dexscreener.com/solana/{address}\n"
            f"• Solscan: https://solscan.io/token/{address}"
        )
    evm_chain = evm_chain or {}
    slug = evm_chain.get('dexscreener_slug') or 'unknown'
    explorer = (evm_chain.get('explorer') or '').rstrip('/')
    lines = [f"• DexScreener: https://dexscreener.com/{slug}/{address}"]
    if explorer:
        lines.append(f"• {evm_chain.get('name', 'Explorer')}: {explorer}/token/{address}")
    return "\n".join(lines)


def describe_chain_config(chain_config: dict) -> str:
    """Human-readable label, e.g. for menus/logs."""
    if not chain_config or chain_config.get('chain_type') != 'evm':
        return "Solana"
    evm_chain = chain_config.get('evm_chain') or {}
    return f"{evm_chain.get('name', 'EVM Chain')} (chainId {evm_chain.get('chain_id', '?')})"


def prompt_chain_selection() -> dict:
    """Interactive CLI menu (blocking input(), matches the style already used
    throughout main.py, e.g. display_chat_selection/display_user_filter_menu).
    Returns a fresh chain_config dict. Re-resolves preset EVM chains from the
    live EVM_CHAINS dict rather than trusting any stale caller-supplied copy,
    so future slug/explorer fixes apply automatically to existing configs."""
    keys = list(EVM_CHAINS.keys())
    print("\n🔗 Select Blockchain to Monitor")
    print("=" * 50)
    print("1. Solana")
    for i, key in enumerate(keys, start=2):
        print(f"{i}. {EVM_CHAINS[key]['name']} (EVM)")
    custom_idx = len(keys) + 2
    print(f"{custom_idx}. Custom EVM chain...")

    while True:
        choice = input(f"\nEnter your choice (1-{custom_idx}): ").strip()
        if choice == "1":
            return {'chain_type': 'solana', 'evm_chain_key': None, 'evm_chain': None}
        if choice.isdigit() and 2 <= int(choice) <= custom_idx - 1:
            key = keys[int(choice) - 2]
            return {'chain_type': 'evm', 'evm_chain_key': key, 'evm_chain': EVM_CHAINS[key]}
        if choice == str(custom_idx):
            print("\nCustom EVM Chain Setup")
            name = input("Chain name (display only): ").strip() or "Custom EVM Chain"
            chain_id_raw = input("Chain ID (integer, optional - display only): ").strip()
            chain_id = int(chain_id_raw) if chain_id_raw.isdigit() else None
            explorer = input("Block explorer base URL (e.g. https://etherscan.io): ").strip().rstrip('/')
            slug = input("DexScreener chain slug (e.g. 'ethereum' - leave blank if unknown): ").strip() or None
            gt = input("GeckoTerminal network slug (optional, leave blank if unknown): ").strip() or None
            evm_chain = {
                'name': name, 'chain_id': chain_id, 'explorer': explorer,
                'dexscreener_slug': slug, 'geckoterminal_network': gt,
            }
            return {'chain_type': 'evm', 'evm_chain_key': 'custom', 'evm_chain': evm_chain}
        print("❌ Invalid choice, please try again.")
