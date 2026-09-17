# Security Policy

## Overview

Fresh Graduate IT is an open-source educational repository containing LaTeX source files, PDFs, diagrams, images, documentation, and other learning resources.

Because the repository accepts contributions from the public and distributes downloadable files, security is treated as an important part of the project's maintenance process.

Our security approach focuses on reducing the risk of malicious files, compromised dependencies, unsafe GitHub Actions, corrupted documents, and other security issues.

## Security Measures

The project uses multiple layers of automated and manual security checks. A comprehensive security workflow runs on every push and pull request.

### Malware Scanning

Repository contents are scanned using ClamAV for potentially malicious files and known malware signatures. The scanning process includes:

* Recursive directory scanning with file limit protections
* Maximum file size enforcement (100 MB per file)
* Maximum scan size limits (1 GB total)
* Recursion depth controls (max 10 levels)
* File count limits (max 10,000 files)
* Detection of infected files and broken archives
* FreshClam virus definition updates before each scan

### Secret Scanning

The repository is scanned for accidentally committed secrets, API keys, credentials, and other sensitive data using Gitleaks, which detects:

* Private keys and certificates
* API tokens and credentials
* Database connection strings
* Authentication tokens
* Other high-entropy secrets

Results are kept confidential and not posted as comments.

### File Inventory and Size Limits

All repository files are validated against configured size limits:

* Individual file size limit: 100 MB
* Archive expanded size limit: 1 GB
* Archive compression ratio limit: 100:1
* Maximum files in archive: 10,000

Files exceeding these limits are flagged as violations.

### File Type and Magic Validation

Files are validated to ensure that their content matches their declared file extension. This prevents disguised malicious files:

* PDF files are verified to have valid PDF signatures
* Images (PNG, JPEG, GIF, WebP, BMP, SVG) are verified against their expected formats
* Archive files (ZIP, 7-Zip) are verified to have correct signatures

Mismatches between file extension and actual file type are rejected.

### Suspicious Executable Files

The repository prohibits certain file types that are not needed for an educational resource:

* Executable files (.exe, .dll, .scr, .com, .msi)
* Java archives (.jar, .class)
* Mobile apps (.apk)
* Desktop packages (.appimage, .deb, .rpm, .dmg, .iso)
* Script files (.bat, .cmd, .ps1, .vbs, .vbe, .js)

Any of these file types found in the repository will cause the security check to fail.

### PDF Security Validation

PDF files receive comprehensive structural and content validation:

* File signature verification using the `file` command
* Structural validation using qpdf to check for corruption or malformed PDFs
* Normalization and inspection of PDF object stream
* Detection of potentially dangerous embedded content:
  - JavaScript code (/JavaScript, /JS)
  - Launch actions (/Launch)
  - Embedded files (/EmbeddedFile, /Filespec)
  - Rich media content (/RichMedia, /Rendition)
  - Audio and video (/Sound, /Movie)
  - 3D objects (/3D)
  - File attachments (/FileAttachment)

PDFs are compiled independently from source files and checked separately. A successful LaTeX compilation does not guarantee that a PDF is safe or correctly structured.

### SVG Security Validation

SVG files are validated for XML well-formedness and checked for dangerous content:

* XML parsing with disabled external entity and network access
* Detection of active script content (<script>, javascript:)
* Detection of foreign objects (<foreignObject>, <iframe>, <object>, <embed>)
* Detection of event handler attributes (on* attributes like onclick)
* Detection of external resource references (HTTP(S), FTP URLs)
* Detection of XML external entity (XXE) and DTD constructs
* Rejection of active data URLs in SVG (particularly HTML, JavaScript)

### Raster Image Security Validation

Raster images (PNG, JPEG, WebP, GIF, BMP) are validated for structural integrity:

* PNG images are checked using pngcheck for valid structure
* PNG IEND chunk validation to detect trailing data after the image
* JPEG images are validated using jpeginfo
* JPEG EOI marker (FF D9) validation with detection of non-zero trailing data
* WebP images are validated using webpinfo
* GIF images are checked for valid GIF87a/GIF89a headers and trailer markers
* BMP images are validated against expected format signatures

### Steganography Heuristic Scan

PNG and BMP files are scanned for common steganography patterns using zsteg:

* Detection of embedded files and archives
* Detection of zlib-compressed data
* Detection of known steganography tools (OpenStego, wbStego)
* Detection of embedded executables or archives
* Detection of suspicious encoded content

Note: Steganography detection is a heuristic scan and is not treated as definitive proof of malicious content. Findings are reported as warnings and do not cause the workflow to fail. Manual review may be necessary for high-risk cases.

### Archive and Embedded Content Security

ZIP and 7-Zip archives are inspected for unsafe content:

* Archive structural validation
* Detection of absolute paths and path traversal attempts (.., leading /)
* Detection of Windows absolute paths (C:\, etc.)
* Detection of suspicious executable/script payloads inside archives
* Archive content listing inspection without extraction

### Embedded Payload and Polyglot Detection

All image and document files are scanned for suspicious embedded binary signatures:

* ELF executable signatures (Unix/Linux binaries)
* PE/MZ signatures (Windows executables)
* ZIP archive signatures embedded in images or documents
* Secondary PDF signatures (polyglot detection)

Embedded PE or ELF signatures cause failures. Embedded archives or secondary PDFs are flagged as warnings for manual review.

### Metadata and Embedded Data Inspection

Media files are inspected for embedded metadata using ExifTool:

* EXIF data extraction from images and PDFs
* Identification of creation tools and software
* Detection of embedded comments, descriptions, and author information
* Generation of comprehensive metadata reports

Metadata reports are generated and retained for audit purposes but do not cause workflow failures.

### GitHub Actions Workflow Security

GitHub Actions workflows are validated for security using Zizmor:

* Analysis of least-privilege permission configuration
* Detection of potentially unsafe GitHub Actions configurations
* Verification of pinned GitHub Actions versions
* Automated workflow security analysis

All GitHub Actions are pinned to specific commit hashes to prevent unauthorized updates and supply chain attacks.

Permissions are denied by default and explicitly granted only to individual jobs as needed:

* Repository contents: read-only where needed
* GitHub Actions metadata: read-only for workflow analysis
* No use of automatic repository secrets in workflows
* No execution of untrusted pull request code with elevated permissions

### Artifact Integrity Verification

SHA-256 hashes are generated for all downloadable artifacts (PDFs, images, archives):

* PDF files
* Image files (PNG, JPEG, WebP, GIF, BMP, SVG)

A comprehensive SHA256SUMS inventory is generated and retained for long-term integrity verification and user verification of downloaded files.

## Important Security Limitation

Automated scanning cannot guarantee that a file is completely free from malware or other security risks.

Security tools can produce false positives and false negatives. A successful CI run should therefore not be interpreted as a guarantee that an artifact is completely safe.

Contributors and users should exercise appropriate caution when downloading or opening files from any public repository.

## Reporting a Security Vulnerability

Please do not create a public GitHub Issue for a security vulnerability.

Publicly disclosing a vulnerability before it can be investigated and addressed may put users at unnecessary risk.

If you discover a potential security vulnerability in this repository:

1. Open the repository's Security tab on GitHub.
2. Use the available private vulnerability reporting mechanism.
3. Provide enough information to reproduce and understand the issue.
4. If possible, include the affected file, workflow, commit, or component.
5. Do not publicly disclose the vulnerability until it has been investigated and an appropriate resolution has been determined.

The Security tab is the preferred channel for reporting security vulnerabilities.

## What Should Be Reported Privately?

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

## Security Updates

Security-related changes may be disclosed after appropriate investigation and remediation.

Depending on the severity of an issue, affected files, workflows, or releases may be temporarily removed or restricted while the issue is investigated.

## Scope

This security policy applies to the Fresh Graduate IT repository and its maintained GitHub Actions workflows, source files, generated artifacts, and project infrastructure.

Third-party websites, external resources, and software referenced by the repository are outside the project's direct control and remain subject to their respective security policies.

## Responsible Disclosure

We appreciate responsible security research and disclosure.

Security reports help protect the Fresh Graduate IT community and improve the safety of the project's materials and infrastructure.
