# Security Policy

## Supported versions

Security fixes are released against the latest published version of BrowserControl.

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub's
[private vulnerability reporting](https://github.com/adityasasidhar/browsercontrol/security/advisories/new)
for this repository. Do not open a public issue for a security problem.

Include the affected version, steps to reproduce, and the impact you observed. You can expect an
acknowledgement within a few days, and a fix or mitigation plan once the report is confirmed.

## Scope notes

BrowserControl drives a real browser on your machine, including any sites it is signed in to.

- **HTTP transport.** Authentication is off by default, so keep it bound to loopback (the
  default). To serve it beyond loopback, set `BROWSER_AUTH_TOKEN`: clients must then send
  `Authorization: Bearer <token>`, checked in constant time. The token is read from the
  environment only (there is no flag, so it stays out of process lists) and travels in clear
  text over plain HTTP, so use TLS in front of it off loopback. The server warns when it binds
  beyond loopback and says whether the token is set.
- **Navigation policy.** `javascript:`, `file:`, `data:`, and `chrome:` URLs are refused by the
  navigation tools unless `BROWSER_ALLOW_UNSAFE_SCHEMES=true`. `BROWSER_ALLOWED_DOMAINS`
  restricts them to listed domains and their subdomains. This is a guardrail on the URLs an
  agent passes to navigation tools, not a sandbox: it does not restrict links the agent clicks,
  redirects, or JavaScript it runs (`run_in_console`), so reports of bypasses of the
  documented behavior are welcome, while those needing page-level scripting are out of scope.
