# Privacy Policy

This plugin (`dify-plugin-bugzilla`) does not collect, store or transmit any personal
data to the plugin author or any third party.

- The configured credentials are `base_url` (the URL of the Bugzilla instance you choose)
  and an optional `api_key`. They are stored by your Dify instance, not by the plugin
  author.
- When you invoke a tool, the plugin sends HTTP requests **only** to that `base_url`
  (its `/rest` API), carrying the bug id or search query you provided, and the `api_key`
  if you configured one. Requests use the User-Agent `dify-plugin-bugzilla/0.0.1`.
- No analytics, telemetry or external hosts are involved. The plugin itself persists
  nothing.

Your queries and the bug data you read are subject to the privacy policy of the Bugzilla
instance configured in `base_url`.
