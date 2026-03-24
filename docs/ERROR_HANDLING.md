# Error Handling Guide

## Overview

Netflix GPT includes comprehensive error handling for production-ready operation.

## Error Types

### 1. Query Validation Errors
- Empty queries
- Too short (< 3 chars)
- Too long (> 500 chars)
- Special characters only

**Handling**: User-friendly error message with suggestions

### 2. Ollama Connection Errors
- Ollama not running
- Model not downloaded
- Connection timeout

**Handling**: Clear instructions to fix the issue

### 3. Vector Store Errors
- Empty database
- Collection not found
- Insufficient documents

**Handling**: Instructions to run setup scripts

### 4. No Results Errors
- Query doesn't match any documents
- Filters too restrictive

**Handling**: Suggestions for alternative queries

### 5. Generic Errors
- Unexpected exceptions
- LLM generation failures

**Handling**: Graceful degradation with error logging

## Using Error Handling

### Safe Query (Recommended)
```python
response = rag.query_safe("your query", raise_on_error=False)

if response['success']:
    print(response['answer'])
else:
    print(f"Error: {response['error_message']}")
```

### Query with Retry
```python
# Automatically retries on failure
response = rag.query_with_retry("your query")
```

### Batch Processing
```python
responses = rag.batch_query_safe(queries, stop_on_error=False)

for resp in responses:
    if resp['success']:
        print(resp['answer'])
    else:
        print(f"Error: {resp['error']}")
```

### Health Check
```python
health = rag.health_check()

if health['overall_status'] == 'healthy':
    # Proceed with queries
else:
    # Check individual components
    for component, status in health['checks'].items():
        if status['status'] == 'error':
            print(f"{component}: {status['message']}")
```

## Common Issues

### "Ollama connection failed"
**Solution**:
```bash
ollama serve  # In separate terminal
ollama pull llama3.2
```

### "Vector store is empty"
**Solution**:
```bash
python src/data_ingestion.py
python src/vectorstore.py
```

### "Query validation failed"
**Solution**: Ensure query is 3-500 characters with meaningful content

## Best Practices

1. Always use `query_safe()` instead of direct `query()`
2. Check `response['success']` before using results
3. Run health checks before processing
4. Enable validation in production
5. Log errors for debugging