# Security Policy

## Supported Versions

Currently, CLE-Net is in Phase 3: Cognitive Enhancement. Security considerations are documented, but the system is not production-ready.

| Version | Supported | Status |
|---------|-----------|--------|
| 0.1.x | Experimental - Not for production |
| 0.2.x | Phase 3 - Enhanced features in development |

## Reporting Security Vulnerabilities

### Responsible Disclosure

If you discover a security vulnerability in CLE-Net, please follow responsible disclosure practices:

1. **Do NOT** open a public issue
2. **Do NOT** discuss the vulnerability publicly
3. **Do** send a detailed report to: [security email]

### What to Include

When reporting, please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested mitigations (if any)

## Threat Model

CLE-Net has an explicit threat model documented in `/docs/architecture/threat_model.md`. Key points:

- Single malicious agents cannot compromise the network
- Consensus requires independent discovery
- Privacy is protected through hashing, not raw data sharing
- Economic incentives discourage harmful behavior

## Known Limitations

CLE-Net does NOT claim to provide:

- Absolute immunity to attacks
- Complete privacy guarantees
- Resistance to global coordination attacks
- Ethical alignment

See `/docs/architecture/threat_model.md` for detailed analysis.

## Best Practices for Running CLE-Net

1. Run nodes in isolated environments
2. Monitor network activity
3. Keep software updated
4. Use secure key management
5. Understand the experimental nature of the system

## Multi-Modal Input Security

With Phase 3's multi-modal input capabilities, additional security considerations apply:

### Voice Input
- Validate audio sources before processing
- Implement rate limiting for transcription services
- Protect speaker identification data

### Video Input
- Sanitize video content before processing
- Implement frame rate limits
- Protect against video injection attacks

### Document Input
- Scan uploaded documents for malware
- Implement file size limits
- Sanitize OCR output

### Image Input
- Validate image formats and sizes
- Implement rate limiting for object detection
- Protect against adversarial images

### Full-Duplex Interaction
- Implement interrupt authentication
- Rate limit simultaneous I/O operations
- Validate real-time streams

## Attribution

Security researchers who responsibly disclose vulnerabilities will be acknowledged (unless they request anonymity).
