-- Copyright (c) Ansible Project
-- GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
-- SPDX-License-Identifier: GPL-3.0-or-later

CREATE OR REPLACE FUNCTION dummy_display_ext_version()
RETURNS text LANGUAGE SQL AS 'SELECT (''1.0'')::text';
