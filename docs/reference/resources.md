---
title: MCP resources
description: The browser:// MCP resources that expose captured console messages, network traffic, errors, tabs, downloads, sessions, and the action log as JSON.
---

# MCP resources

Besides tools, BrowserControl publishes what it has captured as read-only [MCP resources](https://modelcontextprotocol.io/docs/concepts/resources). Reading one costs no tool call and returns no screenshot, which suits clients that can attach resources to a conversation or poll them.

| URI | Contents |
| --- | --- |
| `browser://console` | Captured console messages |
| `browser://network` | The last 100 network requests, with headers and status |
| `browser://network/{request_id}` | One request by its `#id` |
| `browser://errors` | Uncaught page errors |
| `browser://tabs` | Open tabs |
| `browser://downloads` | Downloaded files and where they were saved |
| `browser://actions` | The action log that [`export_test`](/reference/recording#export_test) turns into a test |
| `browser://sessions` | Sessions and their tabs |

Every resource is JSON (`application/json`) and reads the session of the client asking, so with several clients on one server each sees its own data. Reading a resource never starts the browser.

Internal fields (such as the live response object behind a request) are left out, so what you read is plain data.

## Tools or resources?

They expose the same data. Tools return it as text formatted for the model and take options like `clear=True`; resources return the raw JSON. Use whichever your client handles better.
