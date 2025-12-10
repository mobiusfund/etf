import argparse
import sys
from ETF.core.constants import INDEX_IDS, INDEX_LABEL


def add_proxy(subtensor, coldkey: str, wallet, proxy_type: str):
    """Add a proxy delegate to enable staking in an index."""
    add_proxy_call = subtensor.substrate.compose_call(
        call_module="Proxy",
        call_function="add_proxy",
        call_params={"delegate": coldkey, "proxy_type": proxy_type, "delay": 0},
    )

    extrinsic = subtensor.substrate.create_signed_extrinsic(call=add_proxy_call, keypair=wallet.coldkey)
    extrinsic_response = subtensor.substrate.submit_extrinsic(
        extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )
    return extrinsic_response


def remove_proxy(subtensor, coldkey: str, wallet, proxy_type: str):
    """Remove a proxy delegate to stop staking in an index."""
    remove_proxy_call = subtensor.substrate.compose_call(
        call_module="Proxy",
        call_function="remove_proxy",
        call_params={"delegate": coldkey, "proxy_type": proxy_type, "delay": 0},
    )

    extrinsic = subtensor.substrate.create_signed_extrinsic(call=remove_proxy_call, keypair=wallet.coldkey)
    extrinsic_response = subtensor.substrate.submit_extrinsic(
        extrinsic, wait_for_inclusion=True, wait_for_finalization=False
    )
    return extrinsic_response


def list_indexes():
    """Display available indexes."""
    print("\n" + "=" * 60)
    print("Available TrustedStake Indexes")
    print("=" * 60)
    for i, (label, address) in enumerate(zip(INDEX_LABEL, INDEX_IDS)):
        print(f"\nIndex {i}: {label}")
        print(f"Address: {address}")
    print("\n" + "=" * 60)


def delegate_to_index(args):
    """Delegate to an index by adding it as a proxy."""
    try:
        # Import bittensor here to avoid config conflicts
        import bittensor as bt

        # Validate index
        if args.index < 0 or args.index >= len(INDEX_IDS):
            print(f"❌ Error: Invalid index. Must be between 0 and {len(INDEX_IDS) - 1}")
            list_indexes()
            return False

        index_address = INDEX_IDS[args.index]
        index_name = INDEX_LABEL[args.index]

        print(f"\n🔄 Delegating to Index {args.index}: {index_name}")
        print(f"Address: {index_address}")

        # Initialize wallet and subtensor
        wallet = bt.wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        subtensor = bt.subtensor(network=args.network)

        print(f"\n📝 Wallet: {args.wallet_name}")
        print(f"Coldkey: {wallet.coldkeypub.ss58_address}")

        # Confirm action
        if not args.yes:
            confirm = input(f"\n⚠️  This will add {index_name} as a proxy delegate. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Cancelled")
                return False

        # Add proxy
        print("\n⏳ Adding proxy delegate...")
        print("Proxy type: Staking")
        proxy_type = "Staking"
        response = add_proxy(subtensor, index_address, wallet, proxy_type)

        if response.is_success:
            print(f"\n✅ Successfully delegated to {index_name}!")
            print(f"Block hash: {response.block_hash}")
            print(f"\n💡 Note: ~0.1 TAO has been locked as a proxy reserve.")
            print("This will be refunded when you undelegate.")
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
        # Import bittensor here to avoid config conflicts
        import bittensor as bt

        # Validate index
        if args.index < 0 or args.index >= len(INDEX_IDS):
            print(f"❌ Error: Invalid index. Must be between 0 and {len(INDEX_IDS) - 1}")
            list_indexes()
            return False

        index_address = INDEX_IDS[args.index]
        index_name = INDEX_LABEL[args.index]

        print(f"\n🔄 Undelegating from Index {args.index}: {index_name}")
        print(f"Address: {index_address}")

        # Initialize wallet and subtensor
        wallet = bt.wallet(name=args.wallet_name, hotkey=args.wallet_hotkey)
        subtensor = bt.subtensor(network=args.network)

        print(f"\n📝 Wallet: {args.wallet_name}")
        print(f"Coldkey: {wallet.coldkeypub.ss58_address}")

        # Confirm action
        if not args.yes:
            confirm = input(f"\n⚠️  This will remove {index_name} as a proxy delegate. Continue? (y/N): ")
            if confirm.lower() != 'y':
                print("❌ Cancelled")
                return False

        # Remove proxy
        print("\n⏳ Removing proxy delegate...")
        print("Proxy type: Staking")
        proxy_type = "Staking"
        response = remove_proxy(subtensor, index_address, wallet, proxy_type)

        if response.is_success:
            print(f"\n✅ Successfully undelegated from {index_name}!")
            print(f"Block hash: {response.block_hash}")
            print(f"\n💡 Note: The ~0.1 TAO proxy reserve has been refunded.")
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


def prompt_for_arguments(args, command_type):
    """Prompt user for missing required arguments."""
    # Prompt for index if missing
    if not hasattr(args, 'index') or args.index is None:
        list_indexes()
        while True:
            try:
                index_input = input(f"\nEnter index number (0-{len(INDEX_IDS)-1}): ").strip()
                index = int(index_input)
                if 0 <= index < len(INDEX_IDS):
                    args.index = index
                    break
                else:
                    print(f"❌ Invalid index. Must be between 0 and {len(INDEX_IDS)-1}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    # Prompt for wallet name if missing
    if not hasattr(args, 'wallet_name') or args.wallet_name is None:
        wallet_name = input("\nEnter wallet name (coldkey): ").strip()
        if not wallet_name:
            print("❌ Wallet name is required")
            sys.exit(1)
        args.wallet_name = wallet_name
    
    # Prompt for wallet hotkey if missing
    if not hasattr(args, 'wallet_hotkey') or args.wallet_hotkey is None:
        wallet_hotkey = input("Enter wallet hotkey: ").strip()
        if not wallet_hotkey:
            print("❌ Wallet hotkey is required")
            sys.exit(1)
        args.wallet_hotkey = wallet_hotkey
    
    # Set defaults for optional arguments
    if not hasattr(args, 'network') or args.network is None:
        args.network = "finney"
    
    if not hasattr(args, 'yes'):
        args.yes = False
    
    return args


def main():
    parser = argparse.ArgumentParser(
        description="HODL ETF Subnet - Miner Delegation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available indexes
  python miner_cli.py list

  # Delegate to TSBCSI (Index 0)
  python miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default

  # Undelegate from Top 10 (Index 1)
  python miner_cli.py undelegate --index 1 --wallet.name default --wallet.hotkey default

  # Delegate without confirmation prompt
  python miner_cli.py delegate --index 2 --wallet.name default --wallet.hotkey default --yes
  
  # Interactive mode (prompts for missing arguments)
  python miner_cli.py delegate
  python miner_cli.py undelegate
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List available indexes")

    # Delegate command
    delegate_parser = subparsers.add_parser("delegate", help="Delegate to an index")
    delegate_parser.add_argument(
        "--index", type=int, required=False, help="Index number to delegate to (0-4)"
    )
    delegate_parser.add_argument(
        "--wallet.name", dest="wallet_name", type=str, required=False, help="Wallet name"
    )
    delegate_parser.add_argument(
        "--wallet.hotkey", dest="wallet_hotkey", type=str, required=False, help="Wallet hotkey"
    )
    delegate_parser.add_argument(
        "--network",
        type=str,
        default="finney",
        choices=["finney", "test", "local"],
        help="Bittensor network (default: finney)",
    )
    delegate_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )

    # Undelegate command
    undelegate_parser = subparsers.add_parser("undelegate", help="Undelegate from an index")
    undelegate_parser.add_argument(
        "--index", type=int, required=False, help="Index number to undelegate from (0-4)"
    )
    undelegate_parser.add_argument(
        "--wallet.name", dest="wallet_name", type=str, required=False, help="Wallet name"
    )
    undelegate_parser.add_argument(
        "--wallet.hotkey", dest="wallet_hotkey", type=str, required=False, help="Wallet hotkey"
    )
    undelegate_parser.add_argument(
        "--network",
        type=str,
        default="finney",
        choices=["finney", "test", "local"],
        help="Bittensor network (default: finney)",
    )
    undelegate_parser.add_argument(
        "--yes", "-y", action="store_true", help="Skip confirmation prompt"
    )

    args = parser.parse_args()

    if args.command == "list":
        list_indexes()
    elif args.command == "delegate":
        args = prompt_for_arguments(args, "delegate")
        success = delegate_to_index(args)
        sys.exit(0 if success else 1)
    elif args.command == "undelegate":
        args = prompt_for_arguments(args, "undelegate")
        success = undelegate_from_index(args)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
