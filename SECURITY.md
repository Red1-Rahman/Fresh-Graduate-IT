# Security Policy

## Overview

Fresh Graduate IT is an open-source educational repository containing LaTeX source files, PDFs, diagrams, images, documentation, and other learning resources.

Because the repository accepts contributions from the public and distributes downloadable files, security is treated as an important part of the project’s maintenance process.

Our security approach focuses on reducing the risk of malicious files, compromised dependencies, unsafe GitHub Actions, corrupted documents, and other security issues.

## Security Measures

The project uses multiple layers of automated and manual security checks.

Repository and File Scanning

Repository contents are scanned for potentially malicious files and known malware.

Particular attention is given to downloadable and binary artifacts such as:

* PDF files
* Images
* Archives
* Executable files
* Other binary files

Unexpected executable or suspicious files may be rejected.

## PDF Validation

PDF files are validated to ensure that they are structurally valid and not obviously corrupted.

Compiled PDFs are checked independently from the LaTeX compilation process.

A successful LaTeX compilation does not, by itself, guarantee that a PDF is safe or correctly structured.

LaTeX Build Validation

LaTeX documents are automatically compiled in CI environments.

Where applicable, builds are tested across:

* Ubuntu
* Windows
* macOS

Supported LaTeX engines may include:

* pdfLaTeX
* XeLaTeX
* LuaLaTeX

The build process checks for compilation failures and important LaTeX diagnostics, including layout problems such as overfull boxes.

## GitHub Actions Security

GitHub Actions workflows are maintained using security-focused practices, including:

* Least-privilege permissions
* Pinned GitHub Actions where appropriate
* Automated workflow security analysis
* Avoiding unnecessary repository secrets
* Avoiding execution of untrusted Pull Request code with elevated permissions

The project also uses automated analysis to identify potentially unsafe GitHub Actions configurations.

## Important Security Limitation

Automated scanning cannot guarantee that a file is completely free from malware or other security risks.

Security tools can produce false positives and false negatives. A successful CI run should therefore not be interpreted as a guarantee that an artifact is completely safe.

Contributors and users should exercise appropriate caution when downloading or opening files from any public repository.

Reporting a Security Vulnerability

Please do not create a public GitHub Issue for a security vulnerability.

Publicly disclosing a vulnerability before it can be investigated and addressed may put users at unnecessary risk.

If you discover a potential security vulnerability in this repository:

1. Open the repository’s Security tab on GitHub.
2. Use the available private vulnerability reporting mechanism.
3. Provide enough information to reproduce and understand the issue.
4. If possible, include the affected file, workflow, commit, or component.
5. Do not publicly disclose the vulnerability until it has been investigated and an appropriate resolution has been determined.

The Security tab is the preferred channel for reporting security vulnerabilities.

What Should Be Reported Privately?

Examples include:

* Malware or suspicious code committed to the repository
* Malicious or compromised PDF files
* Vulnerabilities in GitHub Actions workflows
* Exposure of repository secrets or credentials
* Unsafe handling of contributor-controlled files
* Supply-chain vulnerabilities
* Authentication or authorization problems
* Security vulnerabilities that could affect repository users or contributors
* Any other issue that could reasonably create a security risk

For ordinary content errors, incorrect questions, formatting problems, feature requests, or documentation issues, use the normal GitHub contribution and issue mechanisms instead.

Security Updates

Security-related changes may be disclosed after appropriate investigation and remediation.

Depending on the severity of an issue, affected files, workflows, or releases may be temporarily removed or restricted while the issue is investigated.

Scope

This security policy applies to the Fresh Graduate IT repository and its maintained GitHub Actions workflows, source files, generated artifacts, and project infrastructure.

Third-party websites, external resources, and software referenced by the repository are outside the project’s direct control and remain subject to their respective security policies.

Responsible Disclosure

We appreciate responsible security research and disclosure.

Security reports help protect the Fresh Graduate IT community and improve the safety of the project’s materials and infrastructure.