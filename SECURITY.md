# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability, please:

1. **DO NOT** create a public GitHub issue
2. Email the details to: [your-email@domain.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Secure Configuration

### API Keys
- **NEVER** commit `.env` file to git
- Use environment variables for all credentials
- Rotate API keys regularly
- Use API keys with minimum required permissions
- Enable IP whitelist on exchange if possible

### Dashboard Access
- Add authentication in production
- Use HTTPS/SSL for remote access
- Restrict access by IP if possible
- Use strong passwords
- Enable rate limiting

### Deployment
- Keep dependencies updated
- Use latest stable versions
- Enable firewall rules
- Monitor logs for suspicious activity
- Use VPN or SSH tunnel for remote access

## Best Practices

### API Security
```python
# Good ✅
api_key = os.getenv('BITGET_API_KEY')

# Bad ❌
api_key = "your_actual_key_here"
```

### Password Protection
```python
# For production dashboard
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.route('/')
@auth.login_required
def dashboard():
    return render_template('dashboard.html')
```

### Secure Communication
- Always use HTTPS in production
- Enable SSL/TLS certificates
- Use secure WebSocket (WSS) if implemented

## Known Limitations

1. **No built-in authentication** - Add basic auth for production
2. **Logs contain sensitive info** - Rotate and secure log files
3. **Dashboard on port 5000** - Use reverse proxy in production
4. **No rate limiting** - Implement if exposing publicly

## Security Checklist

Before deploying to production:

- [ ] All API keys in environment variables
- [ ] `.env` file in `.gitignore`
- [ ] Dashboard has authentication
- [ ] HTTPS/SSL enabled
- [ ] Firewall configured
- [ ] Latest dependencies installed
- [ ] Strong passwords used
- [ ] IP whitelist configured (if possible)
- [ ] Logging is secure
- [ ] Regular backups enabled
- [ ] Monitoring/alerts configured

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Dependencies

We use `pip` for dependency management. Run regularly:

```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

Monitor security advisories for:
- ccxt
- Flask
- scikit-learn
- xgboost
- tensorflow
- pandas
- numpy

## Disclosure Policy

We follow responsible disclosure:
1. Report received
2. Acknowledgment within 48 hours
3. Investigation and fix developed
4. Coordinated public disclosure
5. Credit given to reporter (if desired)

Thank you for helping keep this project secure! 🔒
