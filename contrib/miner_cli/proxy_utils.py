"""Shared utilities for TrustedStake proxy and RealPaysFee chain operations."""

import importlib.metadata as metadata
import json
import sys
import time

from substrateinterface import SubstrateInterface

NETWORKS = {
    "finney": "wss://finney.opentensor.ai:443",
    "main": "wss://finney.opentensor.ai:443",
    "test": "wss://test.finney.opentensor.ai:443",
    "local": "ws://127.0.0.1:9944",
}

TRUSTEDSTAKE_DELEGATES = {
    "5ECnjZ16u9CgLzDL7WM97dwuWepazQmPo5s5njkhz4ExDPxU",
    "5DmcwEMXrSxoGp6NKraDJHXxw4E6ZwmuMrpeggCvQqS5PLEe",
    "5E4jSB8funwmZWAWvVHmc3ZERvXfqpreFMNFVzxeke15Scy5",
    "5EtWFC6Rkb1t7RDuhPBx1BdmnKDoGBvNzvVoZ1S2oA9G6DQe",
    "5E24XT6U2jvSNZe6gyZdgEGQkvNy59SY6ptDprMisrY8Dvsd",
    "5GsiHAb2Z8WThiicAShmWTMB8GYmQ3R8nNvSFeuweNSpiron",
    "5EEVPwQiF3FqcazAeEvbM8CjJB4Q6K5iGHZFg4gDVPKLPsdk",
    "5CiuGG5SYi4tkZRRHSBkDe85S38dEerofhBhohvFDsGCTYJh",
    "5CeJG2T47NxUAAc42q2zoU7qV1YFy4khL3ogHxooVjNKxUuw",
    "5FQ9Pe6qvWpDYhazyBHtN4uYDGgWa3kbatDUExgd2SendTzU",
    "5GbmbuYcd4qGFWyfXmc1gyMfCmzcri7wm4JdKUjPW6P9FZut",
    "5DotNcrAQwCrmv6bEzyhEpgczHUsWyRc9yY4PCGM7u2G6yYE",
    "5CAVRN3GLNRzg34hZ2BzADSoDH2h8gAHXdE3NAecgX7FTGhA",
    "5GszgaeaXibKysxroMQVZ8GaTnTytaHRC73wX2zWnajTDgwk",
    "5CqtC8DXBedhugh8jyCbrEyKybDYhxxsCM9vT8NJmPXaYTiz",
    "5GGWsfGf1U7FWNxLpVigkiF7MBVNrdeNfRNkE421dr11y72N",
    "5Gmy86KGx9KzaiDmj9eJ9cEWaCP54qdiDCFCsvwCZjG3KDgE",
    "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr",
}

BAD_WALLET_VERSIONS = {"4.0.2"}
BAD_BTCLI_VERSIONS = {"9.18.2"}


def get_pkg_version(pkg: str):
    """Get installed package version, or None if not installed.

    Args:
        pkg (str): Package name to look up.

    Returns:
        str | None: Version string or None.
    """
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None


def check_versions():
    """Hard-fail if known vulnerable bittensor packages are installed.

    Prints detected versions and exits with code 1 if a bad version is found.
    """
    wallet_ver = get_pkg_version("bittensor-wallet")
    btcli_ver = get_pkg_version("bittensor-cli")

    print("Detected packages:")
    print("  bittensor-wallet:", wallet_ver or "not installed")
    print("  bittensor-cli:   ", btcli_ver or "not installed")

    if wallet_ver in BAD_WALLET_VERSIONS or btcli_ver in BAD_BTCLI_VERSIONS:
        print("\n❌ ERROR: Known vulnerable bittensor package version detected.")
        print("Remediate with:")
        print("  pip uninstall -y bittensor-cli bittensor-wallet")
        print("  pip cache purge")
        print('  pip install --force-reinstall "bittensor-wallet==4.0.1"')
        print('  pip install --force-reinstall "bittensor-cli==9.18.1"')
        sys.exit(1)


def connect_substrate(network: str, retries: int = 3, delay: float = 1.5) -> SubstrateInterface:
    """Create a direct SubstrateInterface connection with the correct type registry.

    Args:
        network (str): Network name ("finney", "test", "local").
        retries (int): Number of connection attempts.
        delay (float): Seconds between retries.

    Returns:
        SubstrateInterface: Connected instance.
    """
    ws_url = NETWORKS.get(network)
    if not ws_url:
        print(f"❌ Unknown network '{network}'. Use: {', '.join(NETWORKS.keys())}")
        sys.exit(1)

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            substrate = SubstrateInterface(
                url=ws_url,
                ss58_format=42,
                type_registry_preset="substrate-node-template",
            )
            _ = substrate.get_chain_head()
            return substrate
        except Exception as e:
            last_err = e
            if attempt < retries:
                print(f"Connection attempt {attempt} failed, retrying...")
                time.sleep(delay)

    print(f"\n❌ Could not connect to {ws_url}: {last_err}")
    print("Recommended: use Python 3.12 or 3.13 and try again.")
    sys.exit(1)


def safe_query(substrate: SubstrateInterface, module: str, storage_fn: str, params: list):
    """Query chain state with JSON decode error handling.

    Args:
        substrate (SubstrateInterface): Connected instance.
        module (str): Pallet name.
        storage_fn (str): Storage function name.
        params (list): Query parameters.

    Returns:
        QueryResult: The substrate query result.
    """
    try:
        return substrate.query(module, storage_fn, params)
    except json.JSONDecodeError as e:
        print(f"\n❌ Websocket returned invalid JSON querying {module}.{storage_fn}: {e}")
        print("Recommended: use Python 3.12 or 3.13 and retry.")
        sys.exit(1)


def get_staking_proxies(substrate, real_ss58: str) -> list:
    """Query on-chain Staking proxies for a given address.

    Args:
        substrate: SubstrateInterface instance.
        real_ss58 (str): SS58 address of the real (proxied) account.

    Returns:
        list: Proxy dicts where proxy_type == "Staking".
    """
    q = safe_query(substrate, "Proxy", "Proxies", [real_ss58])
    val = q.value
    if not val or len(val) != 2:
        return []
    proxies, _deposit = val
    return [p for p in proxies if isinstance(p, dict) and p.get("proxy_type") == "Staking"]


def is_real_pays_fee_enabled(substrate, real_ss58: str, delegate_ss58: str) -> bool:
    """Check if RealPaysFee is enabled for a (real, delegate) pair.

    Args:
        substrate: SubstrateInterface instance.
        real_ss58 (str): SS58 address of the real account.
        delegate_ss58 (str): SS58 address of the delegate.

    Returns:
        bool: True if RealPaysFee is set on-chain.
    """
    q = safe_query(substrate, "Proxy", "RealPaysFee", [real_ss58, delegate_ss58])
    return q.value is not None


def submit_real_pays_fee(substrate, coldkey, delegate_ss58: str):
    """Submit Proxy.set_real_pays_fee(delegate, true) signed by the real account.

    Args:
        substrate: SubstrateInterface instance.
        coldkey: Unlocked keypair for signing (wallet.coldkey).
        delegate_ss58 (str): SS58 address of the delegate.

    Returns:
        ExtrinsicReceipt: Transaction receipt from chain inclusion.
    """
    call = substrate.compose_call(
        call_module="Proxy",
        call_function="set_real_pays_fee",
        call_params={"delegate": delegate_ss58, "pays_fee": True},
    )
    extrinsic = substrate.create_signed_extrinsic(call=call, keypair=coldkey)
    return substrate.submit_extrinsic(extrinsic, wait_for_inclusion=True)


def select_delegate(staking_proxies: list):
    """Pick the best delegate from a list of staking proxies using the TrustedStake allowlist.

    Rules:
      - Exactly one known TrustedStake delegate -> use it.
      - Multiple known -> fail (ambiguous).
      - No known but exactly one proxy -> use it with warning.
      - No known and multiple proxies -> fail (ambiguous).

    Args:
        staking_proxies (list): Proxy dicts from get_staking_proxies().

    Returns:
        tuple: (selected_ss58_or_list, status_string).
    """
    if not staking_proxies:
        return None, "NO_STAKING_PROXY"

    known = [p for p in staking_proxies if p.get("delegate") in TRUSTEDSTAKE_DELEGATES]

    if len(known) == 1:
        return known[0]["delegate"], "KNOWN_TRUSTEDSTAKE_DELEGATE"
    if len(known) > 1:
        return [p["delegate"] for p in known], "MULTIPLE_KNOWN"
    if len(staking_proxies) == 1:
        return staking_proxies[0]["delegate"], "SINGLE_UNKNOWN"
    return [p["delegate"] for p in staking_proxies], "MULTIPLE_UNKNOWN"
