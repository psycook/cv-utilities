# CV Finder Azure Functions Project

This project hosts an Azure Functions application with three HTTP-triggered operations:

- `findCVOnHomepage` crawls a candidate homepage up to three links deep to locate a CV document or the best HTML fallback.
- `wordToPlainText` converts a base64-encoded Word document to a formatted plain-text representation.
- `wordToMarkdown` converts a base64-encoded Word document to a Markdown representation.

## Prerequisites

- Python 3.10+
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) (optional for deployment)

## Environment Setup

```pwsh
# create and activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# copy local settings template and set secrets
Copy-Item local.settings.json.example local.settings.json
# edit local.settings.json to set CV_FINDER_API_KEYS (comma separated list)
```

## Running Locally

```pwsh
func start
```

The endpoints will be available under `http://localhost:7071/api/`:

- `GET /findCVOnHomepage?apiKey=<key>&url=<homepage>`
- `POST /wordToPlainText`
- `POST /wordToMarkdown`

For POST operations provide a JSON payload:

```json
{
  "apiKey": "<key>",
  "documentContent": "<base64 docx>"
}
```

## Testing

```pwsh
python -m pytest
```

## Deployment

1. Create an Azure Function App resource (Python, Windows or Linux).
2. Configure the `CV_FINDER_API_KEYS` application setting in the Function App.
3. Publish via Azure Functions Core Tools:

   ```pwsh
   func azure functionapp publish <FUNCTION_APP_NAME>
   ```

## Project Structure

```
function_app.py          # Azure Functions entry point
cv_finder/               # Shared helpers
  auth.py
  crawler.py
  document_processing.py
  settings.py
requirements.txt
local.settings.json.example
host.json
```
