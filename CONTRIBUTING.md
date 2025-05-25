# Contributing to Chatbot API with Telegram & DynamoDB

Thank you for your interest in contributing!  
We welcome all improvements, bug fixes, documentation, and ideas.

---

## How to Contribute

1. **Fork the repository**  
   Click the "Fork" button at the top right of this page.

2. **Clone your fork**
   ```bash
   git clone https://github.com/Alwil17/chatbot.git
   cd chatbot
   ```

3. **Create a new branch**
   ```bash
   git checkout -b my-feature
   ```

4. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

5. **Set up your environment**
   - Copy `.env.example` to `.env`
   - Fill in your AWS credentials, Mistral API key, and Telegram bot token
   - Create your DynamoDB table following the README instructions

6. **Make your changes**
   - Add features, fix bugs, or improve documentation
   - Follow the project's code style and structure
   - Ensure no DynamoDB scans are used in your code

7. **Test your changes**
   ```bash
   pytest
   ```

8. **Commit and push**
   ```bash
   git add .
   git commit -m "Describe your change"
   git push origin my-feature
   ```

9. **Open a Pull Request**
   - Go to your fork on GitHub
   - Click "Compare & pull request"
   - Describe your changes and submit

---

## Branch Naming & Pull Request Rules

- **Branch naming convention:**
  - For new features: `feat/short-description`
  - For bug fixes: `bugfix/short-description`
  - For maintenance or chores: `chore/short-description`
  - For documentation: `docs/short-description`
  - Example:  
    ```
    git checkout -b feat/add-conversation-context
    git checkout -b bugfix/fix-telegram-webhook
    ```

- **Pull Request Guidelines:**
  - Use a clear and descriptive title (e.g. `feat: add conversation context support`)
  - In the PR description, explain **what** you changed and **why**
  - Reference related issues by number if applicable (e.g. `Closes #42`)
  - Make sure your branch is up to date with the target branch (usually `main`)
  - Ensure all tests pass before requesting a review
  - Assign reviewers if possible

---

## Code Style & Best Practices

- Use [PEP8](https://www.python.org/dev/peps/pep-0008/) conventions
- Use type hints and docstrings
- Keep functions and classes small and focused
- **DynamoDB Best Practices:**
  - Never use table scans
  - Always use indexes for queries
  - Use batch operations when possible
  - Keep item sizes small
- **Telegram Bot Best Practices:**
  - Handle all possible message types
  - Implement proper error handling
  - Keep webhook endpoints secure
  - Use conversation context appropriately

---

## Testing

- Add or update tests for your changes
- Make sure all tests pass with `pytest`
- Test both API and Telegram bot functionality
- Test DynamoDB operations with mocked responses
- If you add new endpoints, add corresponding tests in `tests/`

---

## Documentation

- Update the `README.md` or docstrings if your change affects usage or API
- Add comments to clarify complex code
- Document any new environment variables
- Keep DynamoDB table structure documentation up to date

---

## Suggestions & Issues

- For feature requests or bug reports, please [open an issue](https://github.com/Alwil17/chatbot/issues)
- Be clear and provide as much context as possible
- For DynamoDB issues, include table structure and access patterns
- For Telegram bot issues, include message logs if possible

---

## Code of Conduct

Be respectful and constructive.  
See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) if available.

---

## Important Notes

- Never commit sensitive information (API keys, tokens, credentials)
- Never commit the `.env` file
- Always test DynamoDB operations locally first
- Be careful with webhook URLs in development
- Consider rate limits for both Telegram and Mistral AI APIs

---

Thank you for helping make this project better! 🚀 