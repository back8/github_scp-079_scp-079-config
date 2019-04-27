# SCP-079-CONFIG - Manage the settings of each bot
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-CONFIG.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pyrogram import Client, Filters

from .. import glovar
from ..functions.config import check_commit, get_config_message
from ..functions.etc import delay, random_str, receive_data
from ..functions.filters import exchange_channel
from ..functions.telegram import send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.channel & exchange_channel
                   & ~Filters.command(glovar.all_commands, glovar.prefix))
def process_data(client, message):
    try:
        data = receive_data(message)
        sender = data["from"]
        receivers = data["to"]
        action = data["action"]
        action_type = data["type"]
        data = data["data"]
        # This will look awkward,
        # seems like it can be simplified,
        # but this is to ensure that the permissions are clear,
        # so it is intentionally written like this
        if "CONFIG" in receivers:
            if sender == "WARN":

                if action == "config":
                    if action_type == "ask":
                        config_key = random_str(8)
                        while glovar.configs.get(config_key):
                            config_key = random_str(8)

                        glovar.configs[config_key] = data
                        glovar.configs[config_key]["type"] = "warn"
                        glovar.configs[config_key]["commit"] = False
                        text, markup = get_config_message(config_key)
                        sent_message = send_message(client, glovar.config_channel_id, text, None, markup)
                        if sent_message:
                            glovar.config[config_key]["message_id"] = sent_message.message_id
                            delay(300, check_commit, [client, config_key])
                        else:
                            glovar.config.pop(config_key, None)
    except Exception as e:
        logger.warning(f"Process data error: {e}", exc_info=True)
