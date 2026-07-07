# Contributing to AirType

Thank you for contributing to AirType! We welcome contributions to enhance our virtual keyboard tracking, gateway server, and frontend interface.

To maintain high software engineering standards from day one, please read and follow these guidelines.

---

## Code of Conduct
By participating in this project, you agree to treat all contributors with respect and professionalism.

## Getting Started

### 1. Repository Setup
AirType is organized as a monorepo containing:
- `client/`: React Frontend
- `server/`: Node.js Express Gateway
- `ml-service/`: Python Machine Learning pipeline and tracking service

To initialize the repository, run the global setup script:
- On Linux/macOS:
  ```bash
  ./scripts/setup.sh
  ```
- On Windows (PowerShell):
  ```powershell
  .\scripts\setup.ps1
  ```

This will verify environment requirements, install dependencies across all components, and create standard config environment templates.

### 2. Development Workflow
To run all services locally in development mode:
```bash
./scripts/run_dev.sh
```
This script runs the client, server, and ML services concurrently with hot-reloading.

---

## Coding Standards

### Git Branching Strategy
- Core branches: `main` (production-ready) and `develop` (integration).
- Feature branches: `feature/<feature-name>` (e.g., `feature/pinch-tap-detection`).
- Bugfix branches: `bugfix/<issue-number>-<short-description>`.
- Hotfix branches: `hotfix/<short-description>`.

All feature and bugfix branches must target `develop`.

### Commit Message Guidelines
We use semantic commit messages to ensure readability. Commits should follow the pattern:
`<type>(<scope>): <short summary>`

Types include:
- `feat`: A new user-facing feature.
- `fix`: A bug fix.
- `docs`: Documentation changes only.
- `style`: Changes that do not affect code logic (whitespace, formatting, missing semi-colons).
- `refactor`: A code change that neither fixes a bug nor adds a feature.
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Changes to build process, auxiliary tools, or library dependencies.

Example:
`feat(ml): implement velocity-based fingertip smoothing filter`

---

## Code Style Guides

### React / Frontend (`client/`)
- Write components in TypeScript (`.tsx`).
- Use React functional components with hooks.
- Code formatting is enforced via Prettier and ESLint. Run `npm run lint` before committing.
- Place reusable UI components under `client/src/components/`.

### Node.js Gateway (`server/`)
- Write controllers, middlewares, and services in standard ESM Node.js.
- Ensure all API endpoints are fully documented in the Swagger config (if applicable) or gateway README.
- Handle and log errors cleanly. Never return stack traces in production API responses.

### Python ML Service (`ml-service/`)
- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines.
- Use explicit type hinting for functions and classes.
- Use `black` and `flake8` for formatting and linting.
- Document all core algorithms and mathematical concepts in docstrings with parameter descriptions.

---

## Submitting Pull Requests

1. **Verify Code Verification Suite**:
   - Run tests for each service (`npm test` or `pytest`) and ensure all pass.
   - Run lints across directories to ensure formatting matches style guidelines.
2. **Commit and Push**:
   - Push your changes to your remote branch.
3. **Open a Pull Request**:
   - Target the `develop` branch.
   - Fill out the Pull Request Template completely.
   - Link any related GitHub issues in the PR description (e.g., `Closes #42`).
4. **Code Review**:
   - All PRs require at least one approval from a designated code owner (defined in `.github/CODEOWNERS`) before merge.
