# Contributing to AI Trading Bot

Thank you for considering contributing to this project! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Check if the enhancement is already suggested
- Clearly describe the feature and its benefits
- Explain your use case

### Code Contributions

1. **Fork the Repository**

   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/trade-bot.git
   cd trade-bot
   ```

2. **Create a Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**

   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test Your Changes**

   ```bash
   # Run tests
   ./test_modules.sh

   # Test with dry-run
   python main.py --dry-run

   # Test Docker build
   docker build -t trading-bot:test .
   ```

5. **Commit and Push**

   ```bash
   git add .
   git commit -m "Add: description of your changes"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub and create a PR
   - Describe your changes clearly
   - Reference any related issues

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Use type hints where appropriate

## Areas for Contribution

### High Priority

- [ ] LSTM model implementation
- [ ] Multiple trading pairs support
- [ ] Advanced order types (OCO, trailing stop)
- [ ] Improved backtesting metrics
- [ ] More technical indicators

### Medium Priority

- [ ] Web UI for configuration
- [ ] Trade execution controls in dashboard
- [ ] Email notifications
- [ ] Database backend (PostgreSQL)
- [ ] RESTful API for external integrations

### Documentation

- [ ] Video tutorials
- [ ] More examples and use cases
- [ ] API documentation
- [ ] Strategy development guide
- [ ] Performance optimization tips

## Testing Guidelines

- Test on testnet before submitting
- Include test cases for new features
- Ensure existing tests pass
- Test with different configurations
- Document any edge cases

## Questions?

Feel free to:

- Open an issue for discussion
- Join our community (if applicable)
- Email the maintainers

Thank you for contributing! 🚀
