"""Test `monz.command_line` module."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from click.testing import CliRunner
from pytest_mock import MockerFixture
from time_machine import TimeMachineFixture

from monz.command_line import MONZO_MAX_PAGE_SIZE, cli

from .factories import MonzoTransactionFactory
from .utils import renderable_to_str


def test_info(
    mocker: MockerFixture,
    time_machine: TimeMachineFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs account balance and latest transaction."""
    time_machine.move_to(datetime(2024, 3, 1), tick=False)

    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["info"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.balance.get.assert_called_once_with(account_id=None)
    mocked_monzo_api.transactions.list.assert_called_once_with(
        account_id=None,
        expand_merchant=True,
        since=datetime.now() - timedelta(days=30),
    )

    assert result.exit_code == 0
    assert result.output

    balance = mocked_monzo_api.balance.get()
    assert renderable_to_str(balance) in result.output

    transactions = mocked_monzo_api.transactions.list()
    assert renderable_to_str(transactions[-1]) in result.output
    for transaction in transactions[:-1]:
        assert renderable_to_str(transaction) not in result.output

    # Running the script with no arguments should have the same effect
    result_no_args = cli_runner.invoke(cli)

    assert result.exit_code == result_no_args.exit_code
    assert result.output == result_no_args.output


def test_whoami(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs `whoami` data."""
    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["whoami"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.whoami.assert_called_once_with()

    assert result.exit_code == 0
    assert result.output

    whoami = mocked_monzo_api.whoami()
    assert renderable_to_str(whoami) in result.output


def test_accounts(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs user accounts."""
    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["accounts"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.accounts.list.assert_called_once_with()

    assert result.exit_code == 0
    assert result.output

    accounts = mocked_monzo_api.accounts.list()
    for account in accounts:
        assert renderable_to_str(account) in result.output


def test_balance(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs user balance."""
    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["balance"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.balance.get.assert_called_once_with(account_id=None)

    assert result.exit_code == 0
    assert result.output

    balance = mocked_monzo_api.balance.get()
    assert renderable_to_str(balance) in result.output

    # TODO: Test `--account_id` option


def test_pots(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs user accounts."""
    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["pots"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.pots.list.assert_called_once_with(account_id=None)

    assert result.exit_code == 0
    assert result.output

    pots = mocked_monzo_api.pots.list()
    for pot in pots:
        assert renderable_to_str(pot) in result.output

    # TODO: Test `--account_id` option
    # TODO: Test `--show_deleted` option


def test_transactions(
    mocker: MockerFixture,
    time_machine: TimeMachineFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Outputs user transactions."""
    time_machine.move_to(datetime(2024, 3, 1), tick=False)

    mocked_MonzoAPI = mocker.patch(  # noqa
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["transactions"])

    mocked_MonzoAPI.assert_called_once_with(access_token=None)
    mocked_monzo_api.transactions.list.assert_called_once_with(
        account_id=None,
        expand_merchant=True,
        since=datetime.now() - timedelta(days=30),
    )

    assert result.exit_code == 0
    assert result.output

    transactions = mocked_monzo_api.transactions.list()
    for transaction in transactions[-3:]:
        assert renderable_to_str(transaction) in result.output

    for transaction in transactions[:-3]:
        assert renderable_to_str(transaction) not in result.output

    # TODO: Test `--account_id` option
    # TODO: Test `--num` option


def test_transactions_explicit_window(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Queries the given window once, without widening `since`."""
    mocker.patch(
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(
        cli,
        args=["transactions", "--since", "2026-08-12", "--before", "2026-08-13"],
    )

    assert result.exit_code == 0
    mocked_monzo_api.transactions.list.assert_called_once_with(
        account_id=None,
        expand_merchant=True,
        limit=MONZO_MAX_PAGE_SIZE,
        since=datetime(2026, 8, 12),
        before=datetime(2026, 8, 13),
    )


def test_transactions_since_only(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Omits `before` when only `--since` is given."""
    mocker.patch(
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    result = cli_runner.invoke(cli, args=["transactions", "--since", "2026-08-12"])

    assert result.exit_code == 0
    mocked_monzo_api.transactions.list.assert_called_once_with(
        account_id=None,
        expand_merchant=True,
        limit=MONZO_MAX_PAGE_SIZE,
        since=datetime(2026, 8, 12),
    )


def test_transactions_window_pages_past_the_first_page(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Follows the cursor until a short page ends the window."""
    mocker.patch(
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    first_page = MonzoTransactionFactory.batch(MONZO_MAX_PAGE_SIZE)
    last_page = MonzoTransactionFactory.batch(2)
    mocked_monzo_api.transactions.list.side_effect = [first_page, last_page]

    result = cli_runner.invoke(
        cli,
        args=["transactions", "--since", "2026-07-01", "--before", "2026-09-04"],
    )

    assert result.exit_code == 0
    assert mocked_monzo_api.transactions.list.call_args_list == [
        mocker.call(
            account_id=None,
            expand_merchant=True,
            limit=MONZO_MAX_PAGE_SIZE,
            since=datetime(2026, 7, 1),
            before=datetime(2026, 9, 4),
        ),
        mocker.call(
            account_id=None,
            expand_merchant=True,
            limit=MONZO_MAX_PAGE_SIZE,
            since=first_page[-1].id,
            before=datetime(2026, 9, 4),
        ),
    ]

    for transaction in last_page + first_page[:1]:
        assert renderable_to_str(transaction) in result.output


def test_transactions_window_fails_when_the_cursor_stalls(
    mocker: MockerFixture,
    cli_runner: CliRunner,
    mocked_monzo_api: MagicMock,
) -> None:
    """Refuses to return a window the cursor stopped advancing through."""
    mocker.patch(
        "monz.command_line.MonzoAPI",
        autospec=True,
        return_value=mocked_monzo_api,
    )

    page = MonzoTransactionFactory.batch(MONZO_MAX_PAGE_SIZE)
    mocked_monzo_api.transactions.list.side_effect = [page, page]

    result = cli_runner.invoke(cli, args=["transactions", "--since", "2026-07-01"])

    assert result.exit_code != 0
    assert "did not advance" in result.output
