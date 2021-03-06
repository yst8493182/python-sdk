# Copyright 2020 TestProject (https://testproject.io)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.command import Command
from src.testproject.sdk.internal.agent import AgentClient
from src.testproject.sdk.internal.helpers.reporting_command_executor import (
    ReportingCommandExecutor,
)


class CustomAppiumCommandExecutor(AppiumConnection, ReportingCommandExecutor):
    """Extension of the Appium AppiumConnection (command_executor) class

    Args:
        agent_client (AgentClient): Client used to communicate with the TestProject Agent
        remote_server_addr (str): Remote server (Agent) address
    """

    def __init__(self, agent_client: AgentClient, remote_server_addr: str):
        AppiumConnection.__init__(self, remote_server_addr=remote_server_addr)
        ReportingCommandExecutor.__init__(
            self, agent_client=agent_client, command_executor=self
        )

        self.w3c = agent_client.agent_session.dialect == "W3C"

    def execute(self, command: str, params: dict, skip_reporting: bool = False):
        """Execute an Appium command

        Args:
            command (str): A string specifying the command to execute
            params (dict): A dictionary of named parameters to send with the command as its JSON payload
            skip_reporting (bool): True if command should not be reported to Agent, False otherwise

        Returns:
            response: Response returned by the Selenium remote webdriver server
        """
        self.update_known_test_name()

        response = {}

        # Preserve mobile sessions
        if not command == Command.QUIT:
            response = super().execute(command=command, params=params)

        result = response.get("value")

        # Both None and 0 response status values indicate command execution was OK
        # 0 seems to be returned on some iOS commands
        passed = True if response.get("status") in [None, 0] else False

        if not skip_reporting:
            self._report_command(command, params, result, passed)

        return response
