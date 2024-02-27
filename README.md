# Environment variables:

* AZURE_OPENAI_KEY=`<API Management subscription key>`

* AZURE_OPENAI_BASE_URL=`<API management url>/deployments/<deployment-id>`

# Run locally

1. In app folder create `.env` file with environment variables

2. Run below commands

```bash
docker build -t demo/demo:v1.0 -f Dockerfile .
docker run -p 8501:8501 -it demo/demo:v1.0 
```

3. Open http://0.0.0.0:8501