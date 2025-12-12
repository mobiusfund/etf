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

# Import the functions to test
from miner_cli import (
    add_proxy,
    remove_proxy,
    list_indexes,
    delegate_to_index,
    undelegate_from_index,
    prompt_for_arguments,
    INDEX_IDS,
    INDEX_LABEL,
)


class TestProxyFunctions:
    """Test add_proxy and remove_proxy functions"""

    def test_add_proxy_success(self):
        """Test successful proxy addition"""
        # Mock objects
        mock_subtensor = Mock()
        mock_wallet = Mock()
        mock_wallet.coldkey = Mock()
        
        # Mock substrate calls
        mock_call = Mock()
        mock_subtensor.substrate.compose_call.return_value = mock_call
        
        mock_extrinsic = Mock()
        mock_subtensor.substrate.create_signed_extrinsic.return_value = mock_extrinsic
        
        mock_response = Mock()
        mock_response.is_success = True
        mock_response.block_hash = "0x123"
        mock_subtensor.substrate.submit_extrinsic.return_value = mock_response
        
        # Call function
        result = add_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")
        
        # Assertions
        assert result.is_success == True
        assert result.block_hash == "0x123"
        mock_subtensor.substrate.compose_call.assert_called_once_with(
            call_module="Proxy",
            call_function="add_proxy",
            call_params={"delegate": "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", "proxy_type": "Staking", "delay": 0}
        )
        mock_subtensor.substrate.create_signed_extrinsic.assert_called_once()
        mock_subtensor.substrate.submit_extrinsic.assert_called_once()

    def test_add_proxy_with_staking_type(self):
        """Test add_proxy with Staking proxy type"""
        mock_subtensor = Mock()
        mock_wallet = Mock()
        mock_wallet.coldkey = Mock()
        
        mock_call = Mock()
        mock_subtensor.substrate.compose_call.return_value = mock_call
        mock_extrinsic = Mock()
        mock_subtensor.substrate.create_signed_extrinsic.return_value = mock_extrinsic
        mock_response = Mock()
        mock_subtensor.substrate.submit_extrinsic.return_value = mock_response
        
        # Call with Staking proxy_type
        add_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")
        
        # Check proxy_type is "Staking"
        call_params = mock_subtensor.substrate.compose_call.call_args[1]["call_params"]
        assert call_params["proxy_type"] == "Staking"

    def test_remove_proxy_success(self):
        """Test successful proxy removal"""
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
        
        # Call function
        result = remove_proxy(mock_subtensor, "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", mock_wallet, "Staking")
        
        # Assertions
        assert result.is_success == True
        assert result.block_hash == "0x456"
        mock_subtensor.substrate.compose_call.assert_called_once_with(
            call_module="Proxy",
            call_function="remove_proxy",
            call_params={"delegate": "5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr", "proxy_type": "Staking", "delay": 0}
        )


class TestListIndexes:
    """Test list_indexes function"""

    def test_list_indexes_output(self, capsys):
        """Test that list_indexes prints correct output"""
        list_indexes()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check header
        assert "Available TrustedStake Indexes" in output
        assert "=" * 60 in output
        
        # Check all indexes are listed
        for i, (label, address) in enumerate(zip(INDEX_LABEL, INDEX_IDS)):
            assert f"Index {i}: {label}" in output
            assert f"Address: {address}" in output

    def test_list_indexes_all_indexes_present(self, capsys):
        """Test that all 5 indexes are present"""
        list_indexes()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check all 5 indexes
        assert "Index 0: TSBCSI" in output
        assert "Index 1: Top 10" in output
        assert "Index 2: Full Stack" in output
        assert "Index 3: Fintech" in output
        assert "Index 4: Bittensor Universe" in output


class TestPromptForArguments:
    """Test prompt_for_arguments function"""

    @patch('builtins.input')
    def test_prompt_for_all_missing_arguments(self, mock_input):
        """Test prompting when all arguments are missing"""
        # Mock user inputs
        mock_input.side_effect = ['0', 'my-coldkey', 'my-hotkey']
        
        # Create args with no attributes
        args = Namespace()
        
        # Call function
        result = prompt_for_arguments(args, "delegate")
        
        # Assertions
        assert result.index == 0
        assert result.wallet_name == "my-coldkey"
        assert result.wallet_hotkey == "my-hotkey"
        assert result.network == "finney"
        assert result.yes == False

    @patch('builtins.input')
    def test_prompt_for_partial_arguments(self, mock_input):
        """Test prompting when some arguments are provided"""
        # Mock user inputs (only need hotkey)
        mock_input.side_effect = ['my-hotkey']
        
        # Create args with some attributes
        args = Namespace(index=1, wallet_name="existing-coldkey", wallet_hotkey=None)
        
        # Call function
        result = prompt_for_arguments(args, "delegate")
        
        # Assertions
        assert result.index == 1
        assert result.wallet_name == "existing-coldkey"
        assert result.wallet_hotkey == "my-hotkey"

    @patch('builtins.input')
    def test_prompt_invalid_index_then_valid(self, mock_input):
        """Test handling invalid index input then valid"""
        # Mock user inputs: invalid, then valid
        mock_input.side_effect = ['99', '2', 'my-coldkey', 'my-hotkey']
        
        args = Namespace()
        result = prompt_for_arguments(args, "delegate")
        
        # Should eventually get valid index
        assert result.index == 2

    @patch('builtins.input')
    def test_prompt_non_numeric_index_then_valid(self, mock_input):
        """Test handling non-numeric index input"""
        # Mock user inputs: non-numeric, then valid
        mock_input.side_effect = ['abc', '1', 'my-coldkey', 'my-hotkey']
        
        args = Namespace()
        result = prompt_for_arguments(args, "delegate")
        
        assert result.index == 1

    @patch('builtins.input')
    def test_prompt_empty_wallet_name_exits(self, mock_input):
        """Test that empty wallet name causes exit"""
        # Mock user inputs: valid index, empty wallet name
        mock_input.side_effect = ['0', '']
        
        args = Namespace()
        
        # Should exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            prompt_for_arguments(args, "delegate")
        assert exc_info.value.code == 1


class TestDelegateToIndex:
    """Test delegate_to_index function"""

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_invalid_index(self, mock_input, mock_add_proxy, capsys):
        """Test delegation with invalid index"""
        args = Namespace(
            index=99,
            wallet_name="test-coldkey",
            wallet_hotkey="test-hotkey",
            network="finney",
            yes=False
        )
        
        result = delegate_to_index(args)
        
        assert result == False
        captured = capsys.readouterr()
        assert "Invalid index" in captured.out

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_user_cancels(self, mock_input, mock_add_proxy):
        """Test delegation when user cancels"""
        # Mock bittensor imports
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())
            
            # User says 'n' to confirmation
            mock_input.return_value = 'n'
            
            args = Namespace(
                index=0,
                wallet_name="test-coldkey",
                wallet_hotkey="test-hotkey",
                network="finney",
                yes=False
            )
            
            result = delegate_to_index(args)
            
            assert result == False
            mock_add_proxy.assert_not_called()

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_success_with_yes_flag(self, mock_input, mock_add_proxy):
        """Test successful delegation with --yes flag"""
        # Mock bittensor imports
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())
            
            # Mock successful response
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.block_hash = "0x123"
            mock_add_proxy.return_value = mock_response
            
            args = Namespace(
                index=0,
                wallet_name="test-coldkey",
                wallet_hotkey="test-hotkey",
                network="finney",
                yes=True  # Skip confirmation
            )
            
            result = delegate_to_index(args)
            
            assert result == True
            mock_add_proxy.assert_called_once()
            # Should not prompt for confirmation
            mock_input.assert_not_called()

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_failure(self, mock_input, mock_add_proxy, capsys):
        """Test delegation failure"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())
            
            # Mock failed response
            mock_response = Mock()
            mock_response.is_success = False
            mock_response.error_message = "Insufficient balance"
            mock_add_proxy.return_value = mock_response
            
            mock_input.return_value = 'y'
            
            args = Namespace(
                index=0,
                wallet_name="test-coldkey",
                wallet_hotkey="test-hotkey",
                network="finney",
                yes=False
            )
            
            result = delegate_to_index(args)
            
            assert result == False
            captured = capsys.readouterr()
            assert "Failed to delegate" in captured.out


class TestUndelegateFromIndex:
    """Test undelegate_from_index function"""

    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_invalid_index(self, mock_input, mock_remove_proxy, capsys):
        """Test undelegation with invalid index"""
        args = Namespace(
            index=-1,
            wallet_name="test-coldkey",
            wallet_hotkey="test-hotkey",
            network="finney",
            yes=False
        )
        
        result = undelegate_from_index(args)
        
        assert result == False
        captured = capsys.readouterr()
        assert "Invalid index" in captured.out

    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_success(self, mock_input, mock_remove_proxy, capsys):
        """Test successful undelegation"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())
            
            # Mock successful response
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.block_hash = "0x456"
            mock_remove_proxy.return_value = mock_response
            
            mock_input.return_value = 'y'
            
            args = Namespace(
                index=0,
                wallet_name="test-coldkey",
                wallet_hotkey="test-hotkey",
                network="finney",
                yes=False
            )
            
            result = undelegate_from_index(args)
            
            assert result == True
            captured = capsys.readouterr()
            assert "Successfully undelegated" in captured.out
            assert "proxy reserve has been refunded" in captured.out

    @patch('miner_cli.remove_proxy')
    @patch('builtins.input')
    def test_undelegate_user_cancels(self, mock_input, mock_remove_proxy):
        """Test undelegation when user cancels"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            bt.Subtensor = Mock(return_value=Mock())
            
            # User says 'n' to confirmation
            mock_input.return_value = 'n'
            
            args = Namespace(
                index=0,
                wallet_name="test-coldkey",
                wallet_hotkey="test-hotkey",
                network="finney",
                yes=False
            )
            
            result = undelegate_from_index(args)
            
            assert result == False
            mock_remove_proxy.assert_not_called()


class TestIndexConfiguration:
    """Test index configuration constants"""

    def test_index_ids_count(self):
        """Test that we have 5 index IDs"""
        assert len(INDEX_IDS) == 5

    def test_index_labels_count(self):
        """Test that we have 5 index labels"""
        assert len(INDEX_LABEL) == 5

    def test_index_ids_labels_match(self):
        """Test that IDs and labels have same count"""
        assert len(INDEX_IDS) == len(INDEX_LABEL)

    def test_index_ids_format(self):
        """Test that all index IDs are valid SS58 addresses"""
        for index_id in INDEX_IDS:
            # SS58 addresses start with '5' and are 48 characters
            assert index_id.startswith('5')
            assert len(index_id) == 48

    def test_index_labels_content(self):
        """Test that index labels are correct"""
        expected_labels = ['TSBCSI', 'Top 10', 'Full Stack', 'Fintech', 'Bittensor Universe']
        assert INDEX_LABEL == expected_labels

    def test_index_ids_unique(self):
        """Test that all index IDs are unique"""
        assert len(INDEX_IDS) == len(set(INDEX_IDS))


class TestErrorHandling:
    """Test error handling in various scenarios"""

    @patch('miner_cli.add_proxy')
    def test_delegate_exception_handling(self, mock_add_proxy, capsys):
        """Test that exceptions are caught and handled"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            # Mock to raise exception
            bt.Wallet = Mock(side_effect=Exception("Wallet not found"))
            
            args = Namespace(
                index=0,
                wallet_name="nonexistent",
                wallet_hotkey="nonexistent",
                network="finney",
                yes=True
            )
            
            result = delegate_to_index(args)
            
            assert result == False
            captured = capsys.readouterr()
            assert "Error" in captured.out

    @patch('miner_cli.remove_proxy')
    def test_undelegate_exception_handling(self, mock_remove_proxy, capsys):
        """Test that exceptions are caught in undelegate"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            # Mock to raise exception
            bt.Wallet = Mock(side_effect=Exception("Network error"))
            
            args = Namespace(
                index=0,
                wallet_name="test",
                wallet_hotkey="test",
                network="finney",
                yes=True
            )
            
            result = undelegate_from_index(args)
            
            assert result == False
            captured = capsys.readouterr()
            assert "Error" in captured.out


class TestNetworkSelection:
    """Test network selection functionality"""

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_with_testnet(self, mock_input, mock_add_proxy):
        """Test delegation with testnet"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            
            mock_subtensor = Mock()
            bt.Subtensor = Mock(return_value=mock_subtensor)
            
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.block_hash = "0x123"
            mock_add_proxy.return_value = mock_response
            
            args = Namespace(
                index=0,
                wallet_name="test",
                wallet_hotkey="test",
                network="test",  # Using testnet
                yes=True
            )
            
            result = delegate_to_index(args)
            
            # Verify subtensor was called with correct network
            bt.Subtensor.assert_called_once_with(network="test")

    @patch('miner_cli.add_proxy')
    @patch('builtins.input')
    def test_delegate_with_local_network(self, mock_input, mock_add_proxy):
        """Test delegation with local network"""
        with patch.dict('sys.modules', {'bittensor': Mock()}):
            import bittensor as bt
            
            mock_wallet = Mock()
            mock_wallet.coldkeypub.ss58_address = "5C..."
            bt.Wallet = Mock(return_value=mock_wallet)
            
            mock_subtensor = Mock()
            bt.Subtensor = Mock(return_value=mock_subtensor)
            
            mock_response = Mock()
            mock_response.is_success = True
            mock_response.block_hash = "0x123"
            mock_add_proxy.return_value = mock_response
            
            args = Namespace(
                index=0,
                wallet_name="test",
                wallet_hotkey="test",
                network="local",  # Using local
                yes=True
            )
            
            result = delegate_to_index(args)
            
            # Verify subtensor was called with correct network
            bt.Subtensor.assert_called_once_with(network="local")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
