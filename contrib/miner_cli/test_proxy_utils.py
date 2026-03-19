#!/usr/bin/env python3
"""
Tests for proxy_utils.py

Run with: python -m pytest test_proxy_utils.py -v
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock

from proxy_utils import (
    TRUSTEDSTAKE_DELEGATES,
    BAD_WALLET_VERSIONS,
    BAD_BTCLI_VERSIONS,
    get_pkg_version,
    check_versions,
    get_staking_proxies,
    is_real_pays_fee_enabled,
    submit_real_pays_fee,
    select_delegate,
)


class TestGetPkgVersion:
    """Test get_pkg_version."""

    @patch("proxy_utils.metadata.version", return_value="4.0.1")
    def test_installed_package(self, mock_ver):
        assert get_pkg_version("bittensor-wallet") == "4.0.1"

    @patch("proxy_utils.metadata.version", side_effect=Exception("not found"))
    def test_missing_package(self, mock_ver):
        assert get_pkg_version("nonexistent-pkg") is None


class TestCheckVersions:
    """Test check_versions."""

    @patch("proxy_utils.get_pkg_version", return_value="4.0.1")
    def test_safe_versions_pass(self, mock_ver, capsys):
        check_versions()
        out = capsys.readouterr().out
        assert "4.0.1" in out

    @patch("proxy_utils.get_pkg_version", side_effect=lambda pkg: "4.0.2" if "wallet" in pkg else "9.18.1")
    def test_bad_wallet_version_exits(self, mock_ver):
        with pytest.raises(SystemExit) as exc:
            check_versions()
        assert exc.value.code == 1

    @patch("proxy_utils.get_pkg_version", side_effect=lambda pkg: "4.0.1" if "wallet" in pkg else "9.18.2")
    def test_bad_btcli_version_exits(self, mock_ver):
        with pytest.raises(SystemExit) as exc:
            check_versions()
        assert exc.value.code == 1

    @patch("proxy_utils.get_pkg_version", return_value=None)
    def test_not_installed_passes(self, mock_ver, capsys):
        check_versions()
        out = capsys.readouterr().out
        assert "not installed" in out


class TestGetStakingProxies:
    """Test get_staking_proxies."""

    def test_returns_staking_proxies(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=[
            [
                {"delegate": "5Abc...", "proxy_type": "Staking", "delay": 0},
                {"delegate": "5Def...", "proxy_type": "Governance", "delay": 0},
            ],
            100_000,
        ])
        result = get_staking_proxies(substrate, "5Real...")
        assert len(result) == 1
        assert result[0]["delegate"] == "5Abc..."

    def test_no_proxies(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=[[], 0])
        result = get_staking_proxies(substrate, "5Real...")
        assert result == []

    def test_invalid_value(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=None)
        result = get_staking_proxies(substrate, "5Real...")
        assert result == []

    def test_multiple_staking_proxies(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=[
            [
                {"delegate": "5Abc...", "proxy_type": "Staking", "delay": 0},
                {"delegate": "5Xyz...", "proxy_type": "Staking", "delay": 0},
            ],
            200_000,
        ])
        result = get_staking_proxies(substrate, "5Real...")
        assert len(result) == 2


class TestIsRealPaysFeeEnabled:
    """Test is_real_pays_fee_enabled."""

    def test_enabled(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=())
        assert is_real_pays_fee_enabled(substrate, "5Real...", "5Del...") is True

    def test_not_enabled(self):
        substrate = Mock()
        substrate.query.return_value = Mock(value=None)
        assert is_real_pays_fee_enabled(substrate, "5Real...", "5Del...") is False


class TestSubmitRealPaysFee:
    """Test submit_real_pays_fee."""

    def test_success(self):
        substrate = Mock()
        coldkey = Mock()

        mock_call = Mock()
        substrate.compose_call.return_value = mock_call

        mock_ext = Mock()
        substrate.create_signed_extrinsic.return_value = mock_ext

        mock_receipt = Mock(is_success=True, block_hash="0xabc")
        substrate.submit_extrinsic.return_value = mock_receipt

        result = submit_real_pays_fee(substrate, coldkey, "5Del...")

        assert result.is_success is True
        substrate.compose_call.assert_called_once_with(
            call_module="Proxy",
            call_function="set_real_pays_fee",
            call_params={"delegate": "5Del...", "pays_fee": True},
        )
        substrate.create_signed_extrinsic.assert_called_once_with(call=mock_call, keypair=coldkey)

    def test_failure(self):
        substrate = Mock()
        coldkey = Mock()
        substrate.compose_call.return_value = Mock()
        substrate.create_signed_extrinsic.return_value = Mock()
        substrate.submit_extrinsic.return_value = Mock(is_success=False, error_message="BadOrigin")

        result = submit_real_pays_fee(substrate, coldkey, "5Del...")
        assert result.is_success is False


class TestSelectDelegate:
    """Test select_delegate allowlist logic."""

    def _make_proxy(self, delegate):
        return {"delegate": delegate, "proxy_type": "Staking", "delay": 0}

    def test_no_proxies(self):
        selected, status = select_delegate([])
        assert selected is None
        assert status == "NO_STAKING_PROXY"

    def test_single_known(self):
        known_addr = list(TRUSTEDSTAKE_DELEGATES)[0]
        selected, status = select_delegate([self._make_proxy(known_addr)])
        assert selected == known_addr
        assert status == "KNOWN_TRUSTEDSTAKE_DELEGATE"

    def test_multiple_known(self):
        addrs = list(TRUSTEDSTAKE_DELEGATES)[:2]
        proxies = [self._make_proxy(a) for a in addrs]
        selected, status = select_delegate(proxies)
        assert status == "MULTIPLE_KNOWN"
        assert isinstance(selected, list)
        assert len(selected) == 2

    def test_single_unknown(self):
        selected, status = select_delegate([self._make_proxy("5UnknownAddress000000000000000000000000000000000")])
        assert status == "SINGLE_UNKNOWN"
        assert selected == "5UnknownAddress000000000000000000000000000000000"

    def test_multiple_unknown(self):
        proxies = [
            self._make_proxy("5UnknownA00000000000000000000000000000000000000"),
            self._make_proxy("5UnknownB00000000000000000000000000000000000000"),
        ]
        selected, status = select_delegate(proxies)
        assert status == "MULTIPLE_UNKNOWN"
        assert isinstance(selected, list)


class TestConstants:
    """Test constant integrity."""

    def test_trustedstake_delegates_not_empty(self):
        assert len(TRUSTEDSTAKE_DELEGATES) > 0

    def test_all_delegates_are_ss58(self):
        for addr in TRUSTEDSTAKE_DELEGATES:
            assert addr.startswith("5")
            assert len(addr) == 48

    def test_bad_versions_defined(self):
        assert "4.0.2" in BAD_WALLET_VERSIONS
        assert "9.18.2" in BAD_BTCLI_VERSIONS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
