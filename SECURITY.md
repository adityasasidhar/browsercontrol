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

BrowserControl drives a real browser on your machine. The HTTP transport has no authentication,
so keep it bound to loopback (the default) unless you add your own access control.
