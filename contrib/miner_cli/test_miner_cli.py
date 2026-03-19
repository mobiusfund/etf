#!/usr/bin/env python3
"""
Tests for miner_cli.py

Run with: python -m pytest test_miner_cli.py -v
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from argparse import Namespace
import io

from miner_cli import (
    add_proxy,
    remove_proxy,
    list_indexes,
    delegate_to_index,
    undelegate_from_index,
    prompt_for_arguments,
    prompt_for_wallet_args,
    status_command,
    enable_real_pays_fee_command,
    _try_enable_real_pays_fee,
)
from ETF.core.constants import INDEX_IDS, INDEX_LABEL


class TestProxyFunctions:
    """Test add_proxy and remove_proxy functions."""

    def test_add_proxy_success(self):
        mock_subtensor = Mock()
        mock_wallet = Mock()
        mock_wallet.coldkey = Mock()

        mock_call = Mock()
        mock_subtensor.substrate.compose_call.return_value = mock_call

        mock_extrinsic = Mock()
        mock_subtensor.substrate.create_signed_extrinsic.return_value = mock_extrinsic

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.block_hash = "0x123"
        mock_subtensor.substrate.submit_extrinsic.return_value = mock_response

        result = add_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")

        assert result.is_success is True
        assert result.block_hash == "0x123"
        mock_subtensor.substrate.compose_call.assert_called_once_with(
            call_module="Proxy",
            call_function="add_proxy",
            call_params={"delegate": "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", "proxy_type": "Staking", "delay": 0}
        )

    def test_add_proxy_with_staking_type(self):
        mock_subtensor = Mock()
        mock_wallet = Mock()
        mock_wallet.coldkey = Mock()
        mock_subtensor.substrate.compose_call.return_value = Mock()
        mock_subtensor.substrate.create_signed_extrinsic.return_value = Mock()
        mock_subtensor.substrate.submit_extrinsic.return_value = Mock()

        add_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")

        call_params = mock_subtensor.substrate.compose_call.call_args[1]["call_params"]
        assert call_params["proxy_type"] == "Staking"

    def test_remove_proxy_success(self):
        mock_subtensor = Mock()
        mock_wallet = Mock()
        mock_wallet.coldkey = Mock()

        mock_call = Mock()
        mock_subtensor.substrate.compose_call.return_value = mock_call

        mock_extrinsic = Mock()
        mock_subtensor.substrate.create_signed_extrinsic.return_value = mock_extrinsic

        mock_response = Mock()
        mock_response.is_success = True
        mock_response.block_hash = "0x456"
        mock_subtensor.substrate.submit_extrinsic.return_value = mock_response

        result = remove_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")

        assert result.is_success is True
        assert result.block_hash == "0x456"
        mock_subtensor.substrate.compose_call.assert_called_once_with(
            call_module="Proxy",
            call_function="remove_proxy",
            call_params={"delegate": "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", "proxy_type": "Staking", "delay": 0}
        )


class TestListIndexes:
    """Test list_indexes function."""

    def test_list_indexes_output(self, capsys):
        list_indexes()
        captured = capsys.readouterr()
        output = captured.out

        assert "Available TrustedStake Indexes" in output
        assert "=" * 60 in output

        for i, (label, address) in enumerate(zip(INDEX_LABEL, INDEX_IDS)):
            assert f"Index {i}: {label}" in output
            assert f"Address: {address}" in output

    def test_list_indexes_all_indexes_present(self, capsys):
        list_indexes()
        captured = capsys.readouterr()
        output = captured.out

        assert "Index 0: TSBCSI" in output
        assert "Index 1: Top 10" in output
        assert "Index 2: Full Stack" in output
        assert "Index 3: Fintech" in output
        assert "Index 4: Bittensor Universe" in output


class TestPromptForArguments:
    """Test prompt_for_arguments function."""

    @patch('builtins.input')
    def test_prompt_for_all_missing_arguments(self, mock_input):
        mock_input.side_effect = ['0', 'my-coldkey', 'my-hotkey']
        args = Namespace()
        result = prompt_for_arguments(args, "delegate")

        assert result.index == 0
        assert result.wallet_name == "my-coldkey"
        assert result.wallet_hotkey == "my-hotkey"
        assert result.network == "finney"
        assert result.yes is False

    @patch('builtins.input')
    def test_prompt_for_partial_arguments(self, mock_input):
        mock_input.side_effect = ['my-hotkey']
        args = Namespace(index=1, wallet_name="existing-coldkey", wallet_hotkey=None)
        result = prompt_for_arguments(args, "delegate")

        assert result.index == 1
        assert result.wallet_name == "existing-coldkey"
        assert result.wallet_hotkey == "my-hotkey"

    @patch('builtins.input')
    def test_prompt_invalid_index_then_valid(self, mock_input):
        mock_input.side_effect = ['99', '2', 'my-coldkey', 'my-hotkey']
        args = Namespace()
        result = prompt_for_arguments(args, "delegate")
        assert result.index == 2

    @patch('builtins.input')
    def test_prompt_non_numeric_index_then_valid(self, mock_input):
        mock_input.side_effect = ['abc', '1', 'my-coldkey', 'my-hotkey']
        args = Namespace()
        result = prompt_for_arguments(args, "delegate")
        assert result.index == 1

    @patch('builtins.input')
    def test_prompt_empty_wallet_name_exits(self, mock_input):
        mock_input.side_effect = ['0', '']
        args = Namespace()
        with pytest.raises(SystemExit) as exc_info:
            prompt_for_arguments(args, "delegate")
        assert exc_info.value.code == 1


class TestPromptForWalletArgs:
    """Test prompt_for_wallet_args (status/enable commands)."""

    @patch('builtins.input')
    def test_prompt_for_wallet_only(self, mock_input):
        mock_input.side_effect = ['my-coldkey', 'my-hotkey']
        args = Namespace()
        result = prompt_for_wallet_args(args)

        assert result.wallet_name == "my-coldkey"
        assert result.wallet_hotkey == "my-hotkey"
        assert result.network == "finney"

    @patch('builtins.input')
    def test_empty_wallet_name_exits(self, mock_input):
        mock_input.side_effect = ['']
        args = Namespace()
        with pytest.raises(SystemExit) as exc:
            prompt_for_wallet_args(args)
        assert exc.value.code == 1


class TestDelegateToIndex:
    """Test delegate_to_index function."""

    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_invalid_index(self, mock_input, mock_add_proxy, mock_cv, capsys):
        args = Namespace(
            index=99, wallet_name="test", wallet_hotkey="test",
            network="finney", yes=False
        )
        result = delegate_to_index(args)
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid index" in captured.out

    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_user_cancels(self, mock_input, mock_add_proxy, mock_cv):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_input.return_value = 'n'
            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=False
            )
            result = delegate_to_index(args)
            assert result is False
            mock_add_proxy.assert_not_called()

    @patch('miner_cli._try_enable_real_pays_fee')
    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_success_auto_enables_rpf(self, mock_input, mock_add_proxy, mock_cv, mock_rpf):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)
            mock_subtensor = Mock()
            bt.Subtensor = Mock(return_value=mock_subtensor)

            mock_response = Mock(is_success=True, block_hash="0x123")
            mock_add_proxy.return_value = mock_response

            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=True
            )
            result = delegate_to_index(args)

            assert result is True
            mock_add_proxy.assert_called_once()
            mock_rpf.assert_called_once_with(
                mock_subtensor, mock_wallet, INDEX_IDS[0], "5CReal..."
            )

    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_failure(self, mock_input, mock_add_proxy, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_add_proxy.return_value = Mock(is_success=False, error_message="Insufficient balance")
            mock_input.return_value = 'y'

            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=False
            )
            result = delegate_to_index(args)
            assert result is False
            captured = capsys.readouterr()
            assert "Failed to delegate" in captured.out


class TestUndelegateFromIndex:
    """Test undelegate_from_index function."""

    @patch('miner_cli.check_versions')
    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_invalid_index(self, mock_input, mock_remove_proxy, mock_cv, capsys):
        args = Namespace(
            index=-1, wallet_name="test", wallet_hotkey="test",
            network="finney", yes=False
        )
        result = undelegate_from_index(args)
        assert result is False
        captured = capsys.readouterr()
        assert "Invalid index" in captured.out

    @patch('miner_cli.check_versions')
    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_success(self, mock_input, mock_remove_proxy, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_remove_proxy.return_value = Mock(is_success=True, block_hash="0x456")
            mock_input.return_value = 'y'

            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=False
            )
            result = undelegate_from_index(args)
            assert result is True
            captured = capsys.readouterr()
            assert "Successfully undelegated" in captured.out

    @patch('miner_cli.check_versions')
    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_user_cancels(self, mock_input, mock_remove_proxy, mock_cv):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_input.return_value = 'n'
            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=False
            )
            result = undelegate_from_index(args)
            assert result is False
            mock_remove_proxy.assert_not_called()


class TestStatusCommand:
    """Test status_command (read-only checker)."""

    @patch('miner_cli.check_versions')
    def test_status_no_proxies(self, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)

            mock_substrate = Mock()
            mock_substrate.query.return_value = Mock(value=[[], 0])
            mock_subtensor = Mock()
            mock_subtensor.substrate = mock_substrate
            bt.Subtensor = Mock(return_value=mock_subtensor)

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="finney", yes=False)
            result = status_command(args)

            assert result is True
            out = capsys.readouterr().out
            assert "No Staking proxies" in out

    @patch('miner_cli.is_real_pays_fee_enabled', return_value=True)
    @patch('miner_cli.get_staking_proxies')
    @patch('miner_cli.check_versions')
    def test_status_with_enabled_proxy(self, mock_cv, mock_proxies, mock_rpf, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)

            mock_subtensor = Mock()
            bt.Subtensor = Mock(return_value=mock_subtensor)

            mock_proxies.return_value = [{"delegate": "5Del...", "proxy_type": "Staking"}]

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="finney", yes=False)
            result = status_command(args)

            assert result is True
            out = capsys.readouterr().out
            assert "ENABLED" in out

    @patch('miner_cli.is_real_pays_fee_enabled', return_value=False)
    @patch('miner_cli.get_staking_proxies')
    @patch('miner_cli.check_versions')
    def test_status_with_disabled_proxy(self, mock_cv, mock_proxies, mock_rpf, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_proxies.return_value = [{"delegate": "5Del...", "proxy_type": "Staking"}]

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="test", yes=False)
            result = status_command(args)

            assert result is True
            out = capsys.readouterr().out
            assert "NOT ENABLED" in out


class TestEnableRealPaysFeeCommand:
    """Test enable_real_pays_fee_command."""

    @patch('miner_cli.is_real_pays_fee_enabled', return_value=True)
    @patch('miner_cli.select_delegate', return_value=("5Del...", "KNOWN_TRUSTEDSTAKE_DELEGATE"))
    @patch('miner_cli.get_staking_proxies')
    @patch('miner_cli.check_versions')
    def test_already_enabled(self, mock_cv, mock_proxies, mock_sel, mock_rpf, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_proxies.return_value = [{"delegate": "5Del...", "proxy_type": "Staking"}]

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="finney", yes=True)
            result = enable_real_pays_fee_command(args)

            assert result is True
            out = capsys.readouterr().out
            assert "already enabled" in out

    @patch('miner_cli.get_staking_proxies', return_value=[])
    @patch('miner_cli.check_versions')
    def test_no_proxy(self, mock_cv, mock_proxies, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="finney", yes=True)
            result = enable_real_pays_fee_command(args)

            assert result is False
            out = capsys.readouterr().out
            assert "No Staking proxy found" in out

    @patch('miner_cli.submit_real_pays_fee')
    @patch('miner_cli.is_real_pays_fee_enabled')
    @patch('miner_cli.select_delegate', return_value=("5Del...", "KNOWN_TRUSTEDSTAKE_DELEGATE"))
    @patch('miner_cli.get_staking_proxies')
    @patch('miner_cli.check_versions')
    def test_enable_success(self, mock_cv, mock_proxies, mock_sel, mock_rpf, mock_submit, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5CReal..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_proxies.return_value = [{"delegate": "5Del...", "proxy_type": "Staking"}]
            mock_rpf.side_effect = [False, True]
            mock_submit.return_value = Mock(
                is_success=True, block_hash="0xabc", extrinsic_hash="0xdef"
            )

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="finney", yes=True)
            result = enable_real_pays_fee_command(args)

            assert result is True
            out = capsys.readouterr().out
            assert "now enabled" in out


class TestTryEnableRealPaysFee:
    """Test _try_enable_real_pays_fee auto-enable helper."""

    @patch('miner_cli.is_real_pays_fee_enabled', return_value=True)
    def test_already_enabled_skips(self, mock_rpf, capsys):
        subtensor = Mock()
        wallet = Mock()
        _try_enable_real_pays_fee(subtensor, wallet, "5Del...", "5Real...")

        out = capsys.readouterr().out
        assert "already enabled" in out

    @patch('miner_cli.submit_real_pays_fee')
    @patch('miner_cli.is_real_pays_fee_enabled', return_value=False)
    def test_enable_success(self, mock_rpf, mock_submit, capsys):
        subtensor = Mock()
        wallet = Mock()
        mock_submit.return_value = Mock(is_success=True)

        _try_enable_real_pays_fee(subtensor, wallet, "5Del...", "5Real...")

        out = capsys.readouterr().out
        assert "enabled successfully" in out

    @patch('miner_cli.is_real_pays_fee_enabled', side_effect=Exception("chain error"))
    def test_failure_is_non_fatal(self, mock_rpf, capsys):
        subtensor = Mock()
        wallet = Mock()
        _try_enable_real_pays_fee(subtensor, wallet, "5Del...", "5Real...")

        out = capsys.readouterr().out
        assert "could not enable" in out
        assert "enable-real-pays-fee" in out


class TestIndexConfiguration:
    """Test index configuration constants."""

    def test_index_ids_count(self):
        assert len(INDEX_IDS) == 5

    def test_index_labels_count(self):
        assert len(INDEX_LABEL) == 5

    def test_index_ids_labels_match(self):
        assert len(INDEX_IDS) == len(INDEX_LABEL)

    def test_index_ids_format(self):
        for index_id in INDEX_IDS:
            assert index_id.startswith('5')
            assert len(index_id) == 48

    def test_index_labels_content(self):
        expected_labels = ['TSBCSI', 'Top 10', 'Full Stack', 'Fintech', 'Bittensor Universe']
        assert INDEX_LABEL == expected_labels

    def test_index_ids_unique(self):
        assert len(INDEX_IDS) == len(set(INDEX_IDS))


class TestErrorHandling:
    """Test error handling in various scenarios."""

    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    def test_delegate_exception_handling(self, mock_add_proxy, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            bt.Wallet = Mock(side_effect=Exception("Wallet not found"))

            args = Namespace(
                index=0, wallet_name="nonexistent", wallet_hotkey="nonexistent",
                network="finney", yes=True
            )
            result = delegate_to_index(args)
            assert result is False
            captured = capsys.readouterr()
            assert "Error" in captured.out

    @patch('miner_cli.check_versions')
    @patch('miner_cli.remove_proxy')
    def test_undelegate_exception_handling(self, mock_remove_proxy, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            bt.Wallet = Mock(side_effect=Exception("Network error"))

            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="finney", yes=True
            )
            result = undelegate_from_index(args)
            assert result is False
            captured = capsys.readouterr()
            assert "Error" in captured.out


class TestNetworkSelection:
    """Test network selection works for all commands."""

    @patch('miner_cli._try_enable_real_pays_fee')
    @patch('miner_cli.check_versions')
    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_with_testnet(self, mock_input, mock_add_proxy, mock_cv, mock_rpf):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())

            mock_add_proxy.return_value = Mock(is_success=True, block_hash="0x123")

            args = Namespace(
                index=0, wallet_name="test", wallet_hotkey="test",
                network="test", yes=True
            )
            delegate_to_index(args)
            bt.Subtensor.assert_called_once_with(network="test")

    @patch('miner_cli.check_versions')
    def test_status_with_testnet(self, mock_cv, capsys):
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)

            mock_substrate = Mock()
            mock_substrate.query.return_value = Mock(value=[[], 0])
            mock_subtensor = Mock()
            mock_subtensor.substrate = mock_substrate
            bt.Subtensor = Mock(return_value=mock_subtensor)

            args = Namespace(wallet_name="test", wallet_hotkey="test", network="test", yes=False)
            status_command(args)
            bt.Subtensor.assert_called_once_with(network="test")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
