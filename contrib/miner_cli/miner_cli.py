import argparse
import sys
from ETF.core.constants import INDEX_IDS, INDEX_LABEL
from proxy_utils import (
    TRUSTEDSTAKE_DELEGATES,
    check_versions,
    connect_substrate,
    get_staking_proxies,
    is_real_pays_fee_enabled,
    submit_real_pays_fee,
    select_delegate,
)


# ---------------------------------------------------------------------------
# Low-level proxy extrinsics
# ---------------------------------------------------------------------------

def add_proxy(subtensor, coldkey: str, wallet, proxy_type: str):
    """Submit Proxy.add_proxy extrinsic to add a delegate."""
    call = subtensor.substrate.compose_call(
        call_module="Proxy",
        call_function="add_proxy",
        call_params={"delegate": coldkey, "proxy_type": proxy_type, "delay": 0},
    )
    extrinsic = subtensor.substrate.create_signed_extrinsic(call=call, keypair=wallet.coldkey)
    return subtensor.substrate.submit_extrinsic(
        extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )


def remove_proxy(subtensor, coldkey: str, wallet, proxy_type: str):
    """Submit Proxy.remove_proxy extrinsic to remove a delegate."""
    call = subtensor.substrate.compose_call(
        call_module="Proxy",
        call_function="remove_proxy",
        call_params={"delegate": coldkey, "proxy_type": proxy_type, "delay": 0},
    )
    extrinsic = subtensor.substrate.create_signed_extrinsic(call=call, keypair=wallet.coldkey)
    return subtensor.substrate.submit_extrinsic(
        extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )


# ---------------------------------------------------------------------------
# Auto-enable helper (called after proxy creation / switch)
# ---------------------------------------------------------------------------

def _try_enable_real_pays_fee(network: str, wallet, delegate_ss58: str, real_ss58: str):
    """Best-effort enable RealPaysFee after proxy creation. Non-fatal on failure."""
    try:
        substrate = connect_substrate(network)

        try:
            substrate.get_metadata_call_function("Proxy", "set_real_pays_fee")
        except Exception:
            print("\n⚠️  RealPaysFee: not available on this chain yet (Proxy.set_real_pays_fee not found)")
            return

        if is_real_pays_fee_enabled(substrate, real_ss58, delegate_ss58):
            print("\n✅ RealPaysFee: already enabled for this proxy")
            return
        print("\n⏳ Enabling RealPaysFee for this proxy...")
        receipt = submit_real_pays_fee(substrate, wallet.coldkey, delegate_ss58)
        if receipt.is_success:
            print("✅ RealPaysFee: enabled successfully")
        else:
            print(f"⚠️  RealPaysFee: could not enable ({receipt.error_message})")
            print("   You can enable it later: python miner_cli.py enable-real-pays-fee ...")
    except Exception as e:
        print(f"⚠️  RealPaysFee: could not enable ({e})")
        print("   You can enable it later: python miner_cli.py enable-real-pays-fee ...")


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def list_indexes():
    """Display available TrustedStake indexes."""
    print("\n" + "=" * 60)
    print("Available TrustedStake Indexes")
    print("=" * 60)
    for i, (label, address) in enumerate(zip(INDEX_LABEL, INDEX_IDS)):
        print(f"\nIndex {i}: {label}")
        print(f"Address: {address}")
    print("\n" + "=" * 60)


def delegate_to_index(args):
    """Delegate to an index by adding it as a proxy, then auto-enable RealPaysFee."""
    try:
        import bittensor as bt

        check_versions()

        if args.index < 0 or args.index >= len(INDEX_IDS):
            print(f"❌ Error: Invalid index. Must be between 0 and {len(INDEX_IDS) - 1}")
            list_indexes()
            return False

        index_address = INDEX_IDS[args.index]
        index_name = INDEX_LABEL[args.index]

        print(f"\n🔄 Delegating to Index {args.index}: {index_name}")
        print(f"Address: {index_address}")

        wallet = bt.Wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        subtensor = bt.Subtensor(network=args.network)

        real_ss58 = wallet.coldkeypub.ss58_address
        print(f"\n📝 Wallet: {args.wallet_name}")
        print(f"Coldkey: {real_ss58}")

        if not args.yes:
            confirm = input(f"\n⚠️  This will add {index_name} as a proxy delegate. Continue? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cancelled")
                return False

        print("\n⏳ Adding proxy delegate...")
        print("Proxy type: Staking")
        response = add_proxy(subtensor, index_address, wallet, "Staking")

        if response.is_success:
            print(f"\n✅ Successfully delegated to {index_name}!")
            print(f"Block hash: {response.block_hash}")
            print("\n💡 Note: ~0.1 TAO has been locked as a proxy reserve.")
            print("This will be refunded when you undelegate.")

            # Reason: auto-enable RealPaysFee so user pays normal network fees
            _try_enable_real_pays_fee(args.network, wallet, index_address, real_ss58)
            return True
        else:
            print(f"\n❌ Failed to delegate: {response.error_message}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def undelegate_from_index(args):
    """Undelegate from an index by removing it as a proxy."""
    try:
        import bittensor as bt

        check_versions()

        if args.index < 0 or args.index >= len(INDEX_IDS):
            print(f"❌ Error: Invalid index. Must be between 0 and {len(INDEX_IDS) - 1}")
            list_indexes()
            return False

        index_address = INDEX_IDS[args.index]
        index_name = INDEX_LABEL[args.index]

        print(f"\n🔄 Undelegating from Index {args.index}: {index_name}")
        print(f"Address: {index_address}")

        wallet = bt.Wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        subtensor = bt.Subtensor(network=args.network)

        print(f"\n📝 Wallet: {args.wallet_name}")
        print(f"Coldkey: {wallet.coldkeypub.ss58_address}")

        if not args.yes:
            confirm = input(f"\n⚠️  This will remove {index_name} as a proxy delegate. Continue? (y/N): ")
            if confirm.lower() != "y":
                print("❌ Cancelled")
                return False

        print("\n⏳ Removing proxy delegate...")
        print("Proxy type: Staking")
        response = remove_proxy(subtensor, index_address, wallet, "Staking")

        if response.is_success:
            print(f"\n✅ Successfully undelegated from {index_name}!")
            print(f"Block hash: {response.block_hash}")
            print("\n💡 Note: The ~0.1 TAO proxy reserve has been refunded.")
            print("⚠️  You may need to manually unstake your TAO from the underlying subnets.")
            return True
        else:
            print(f"\n❌ Failed to undelegate: {response.error_message}")
            return False

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def status_command(args):
    """Read-only check of proxy and RealPaysFee status. No signing, no wallet unlock."""
    try:
        import bittensor as bt

        check_versions()

        wallet = bt.Wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        substrate = connect_substrate(args.network)

        real_ss58 = wallet.coldkeypub.ss58_address
        print(f"\nWallet : {args.wallet_name}")
        print(f"Coldkey: {real_ss58}")
        print(f"Network: {args.network}")

        staking_proxies = get_staking_proxies(substrate, real_ss58)

        if not staking_proxies:
            print("\nNo Staking proxies found for this wallet.")
            return True

        print(f"\nStaking proxies ({len(staking_proxies)}):")
        print("-" * 70)
        for p in staking_proxies:
            delegate = p["delegate"]
            known = "TrustedStake" if delegate in TRUSTEDSTAKE_DELEGATES else "unknown"
            try:
                enabled = is_real_pays_fee_enabled(substrate, real_ss58, delegate)
                rpf_status = "ENABLED" if enabled else "NOT ENABLED"
            except Exception:
                rpf_status = "QUERY FAILED"
            print(f"  {delegate} [{known}] RealPaysFee -> {rpf_status}")

        print("\nDone.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def enable_real_pays_fee_command(args):
    """Enable RealPaysFee for an existing TrustedStake proxy. Auto-selects delegate via allowlist."""
    try:
        import bittensor as bt

        check_versions()

        wallet = bt.Wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        substrate = connect_substrate(args.network)

        real_ss58 = wallet.coldkeypub.ss58_address
        print("\nTrustedStake RealPaysFee Enable")
        print("-" * 40)
        print(f"Network: {args.network}")
        print(f"Wallet : {args.wallet_name}")
        print(f"Coldkey: {real_ss58}")

        try:
            substrate.get_metadata_call_function("Proxy", "set_real_pays_fee")
        except Exception:
            print("\n❌ This chain does not expose Proxy.set_real_pays_fee yet.")
            return False

        staking_proxies = get_staking_proxies(substrate, real_ss58)
        if not staking_proxies:
            print("\n❌ No Staking proxy found. This command requires an existing proxy.")
            return False

        print(f"\nDetected Staking proxies:")
        for i, p in enumerate(staking_proxies, 1):
            delegate = p.get("delegate")
            known = "known TrustedStake" if delegate in TRUSTEDSTAKE_DELEGATES else "unknown"
            print(f"  {i}. {delegate} ({known})")

        selected, status = select_delegate(staking_proxies)

        if status in ("MULTIPLE_KNOWN", "MULTIPLE_UNKNOWN"):
            print("\nMultiple Staking proxies detected. Please choose one:")
            for i, d in enumerate(selected, 1):
                known = "TrustedStake" if d in TRUSTEDSTAKE_DELEGATES else "unknown"
                print(f"  {i}. {d} [{known}]")
            while True:
                try:
                    choice = int(input(f"\nEnter number (1-{len(selected)}): ").strip())
                    if 1 <= choice <= len(selected):
                        delegate_ss58 = selected[choice - 1]
                        break
                    print(f"❌ Must be between 1 and {len(selected)}")
                except ValueError:
                    print("❌ Please enter a valid number")
        else:
            delegate_ss58 = selected

        print(f"\nSelected delegate: {delegate_ss58}")

        if status == "SINGLE_UNKNOWN":
            print("⚠️  WARNING: This delegate is not in the TrustedStake allowlist.")

        enabled_before = is_real_pays_fee_enabled(substrate, real_ss58, delegate_ss58)
        print(f"RealPaysFee currently: {'ENABLED' if enabled_before else 'NOT ENABLED'}")

        if enabled_before:
            print("\n✅ Nothing to do. RealPaysFee is already enabled.")
            return True

        if not args.yes:
            confirm = input("\nEnable RealPaysFee for this delegate? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("❌ Cancelled")
                return False

        print("\n⏳ Submitting Proxy.set_real_pays_fee...")
        receipt = submit_real_pays_fee(substrate, wallet.coldkey, delegate_ss58)

        print(f"Block hash: {receipt.block_hash}")
        print(f"Tx hash   : {receipt.extrinsic_hash}")
        print(f"Success   : {receipt.is_success}")

        if not receipt.is_success:
            print(f"\n❌ Transaction failed: {receipt.error_message}")
            return False

        enabled_after = is_real_pays_fee_enabled(substrate, real_ss58, delegate_ss58)
        print(f"RealPaysFee after tx: {'ENABLED' if enabled_after else 'NOT ENABLED'}")

        if not enabled_after:
            print("\n⚠️  Transaction included but RealPaysFee still appears unset.")
            return False

        print("\n✅ RealPaysFee is now enabled for your TrustedStake proxy.")
        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ---------------------------------------------------------------------------
# Argument helpers
# ---------------------------------------------------------------------------

def _add_wallet_args(parser):
    """Add common wallet/network/yes arguments to a subparser."""
    parser.add_argument("--wallet.name", dest="wallet_name", type=str, required=False, help="Wallet name")
    parser.add_argument("--wallet.hotkey", dest="wallet_hotkey", type=str, required=False, help="Wallet hotkey")
    parser.add_argument(
        "--network", type=str, default="finney",
        choices=["finney", "test", "local"],
        help="Bittensor network (default: finney)",
    )
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")


def prompt_for_arguments(args, command_type):
    """Prompt user for missing required arguments.

    Args:
        args: Parsed argparse Namespace.
        command_type (str): Command name (controls whether index is prompted).

    Returns:
        Namespace: args with missing values filled in.
    """
    needs_index = command_type in ("delegate", "undelegate")

    if needs_index and (not hasattr(args, "index") or args.index is None):
        list_indexes()
        while True:
            try:
                index_input = input(f"\nEnter index number (0-{len(INDEX_IDS)-1}): ").strip()
                index = int(index_input)
                if 0 <= index < len(INDEX_IDS):
                    args.index = index
                    break
                print(f"❌ Invalid index. Must be between 0 and {len(INDEX_IDS)-1}")
            except ValueError:
                print("❌ Please enter a valid number")

    if not hasattr(args, "wallet_name") or args.wallet_name is None:
        wallet_name = input("\nEnter wallet name (coldkey): ").strip()
        if not wallet_name:
            print("❌ Wallet name is required")
            sys.exit(1)
        args.wallet_name = wallet_name

    if not hasattr(args, "wallet_hotkey") or args.wallet_hotkey is None:
        wallet_hotkey = input("Enter wallet hotkey: ").strip()
        if not wallet_hotkey:
            print("❌ Wallet hotkey is required")
            sys.exit(1)
        args.wallet_hotkey = wallet_hotkey

    if not hasattr(args, "network") or args.network is None:
        args.network = "finney"
    if not hasattr(args, "yes"):
        args.yes = False

    return args


def prompt_for_wallet_args(args):
    """Prompt for wallet name/hotkey when missing (no index needed)."""
    return prompt_for_arguments(args, "status")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="HODL ETF Subnet - Miner Delegation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python miner_cli.py list
  python miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default
  python miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default --network test
  python miner_cli.py undelegate --index 1 --wallet.name default --wallet.hotkey default
  python miner_cli.py status --wallet.name default --wallet.hotkey default
  python miner_cli.py enable-real-pays-fee --wallet.name default --wallet.hotkey default
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list -------------------------------------------------------------------
    subparsers.add_parser("list", help="List available indexes")

    # delegate ---------------------------------------------------------------
    delegate_parser = subparsers.add_parser("delegate", help="Delegate to an index (auto-enables RealPaysFee)")
    delegate_parser.add_argument("--index", type=int, required=False, help="Index number (0-4)")
    _add_wallet_args(delegate_parser)

    # undelegate -------------------------------------------------------------
    undelegate_parser = subparsers.add_parser("undelegate", help="Undelegate from an index")
    undelegate_parser.add_argument("--index", type=int, required=False, help="Index number (0-4)")
    _add_wallet_args(undelegate_parser)

    # status -----------------------------------------------------------------
    status_parser = subparsers.add_parser("status", help="Check proxy & RealPaysFee status (read-only)")
    _add_wallet_args(status_parser)

    # enable-real-pays-fee ---------------------------------------------------
    rpf_parser = subparsers.add_parser(
        "enable-real-pays-fee",
        help="Enable RealPaysFee for an existing proxy",
    )
    _add_wallet_args(rpf_parser)

    args = parser.parse_args()

    if args.command == "list":
        list_indexes()
    elif args.command == "delegate":
        args = prompt_for_arguments(args, "delegate")
        sys.exit(0 if delegate_to_index(args) else 1)
    elif args.command == "undelegate":
        args = prompt_for_arguments(args, "undelegate")
        sys.exit(0 if undelegate_from_index(args) else 1)
    elif args.command == "status":
        args = prompt_for_wallet_args(args)
        sys.exit(0 if status_command(args) else 1)
    elif args.command == "enable-real-pays-fee":
        args = prompt_for_wallet_args(args)
        sys.exit(0 if enable_real_pays_fee_command(args) else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
