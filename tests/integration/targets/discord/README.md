<!--
Copyright (c) Ansible Project
GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
SPDX-License-Identifier: GPL-3.0-or-later
-->

The integration tests can be executed locally:

1. Create or use an existing discord server
2. Open `Server Settings` and navigate to `Integrations` tab
3. Click `Create Webhook` to create a new webhook
4. Click `Copy Webhook URL` and extract the webhook_id + webhook_token

    Example: https://discord.com/api/webhooks/`webhook_id`/`webhook_token`

5. Replace the variables `discord_id` and `discord_token` in the var file
6. Run the integration test
````
ansible-test integration -v --color yes discord --allow-unsupported
````
