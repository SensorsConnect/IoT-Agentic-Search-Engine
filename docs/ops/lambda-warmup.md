# Lambda Warm-Up Ping

## Problem

The `localelive-backend` Lambda was showing cold-start **init timeouts** — 8 consecutive failures around 20:25 UTC on 2026-07-12:

```
INIT_REPORT Init Duration: 9914.59 ms  Phase: init  Status: timeout
INIT_REPORT Init Duration: 9969.89 ms  Phase: init  Status: timeout
...
```

**Why it happens:** AWS Lambda has a fixed 10-second init timeout. When the container has been idle (AWS recycled it), a fresh invocation must import all dependencies before it can serve the request — LangChain, PyMongo, Groq, etc. push the import time to ~10 s, causing the init to timeout. The user sees a failed or very slow request.

**Why it recovers on its own:** Lambda retries. Once a container is warm (imports already done), all subsequent requests are fast (2–3 ms execution, ~900 ms with LLM calls).

---

## Fix: Scheduled Warm-Up Ping

A CloudWatch Events rule fires every 5 minutes and invokes the Lambda with a tiny payload. This keeps the container alive so real user requests never hit a cold start.

### What was created

| Resource | Name | Value |
|---|---|---|
| CloudWatch Events rule | `localelive-backend-warmup` | `rate(5 minutes)`, ENABLED |
| Lambda target | `localelive-backend-warmup-target` | `localelive-backend` |
| Payload sent | — | `{"source": "warmup"}` |
| Lambda permission | `allow-eventbridge-warmup` | grants `events.amazonaws.com` invoke rights |

The `{"source": "warmup"}` payload is passed through `mangum` to FastAPI. It doesn't match any route, so FastAPI returns a 404 — that's fine. The purpose is only to trigger the Lambda so the container stays initialised.

---

## Cost

At current traffic (~10k invocations/month) you are well within the free tier:

| | Monthly cost |
|---|---|
| Before (no ping) | $0.00 |
| Warm-up ping adds 8,640 extra invocations/month (~5 ms each) | +$0.002 |
| **Total** | **~$0.00** |

Provisioned Concurrency (the 100% guaranteed alternative) would cost ~$10.80/month — not worth it at current traffic.

---

## Limitations

The ping keeps one container alive. It won't help if:

- You **redeploy** the Lambda — all containers are replaced and the first request after a deploy will cold-start once.
- AWS **force-recycles** the container (rare, happens during maintenance or if the function hasn't been called for >15 minutes after the ping gap).
- Traffic suddenly **spikes** and Lambda needs to spin up additional containers in parallel — those new containers will cold-start.

For the current traffic level these edge cases are rare and acceptable.

---

## Managing the rule

```bash
# Disable (stop pinging, no cost)
aws events disable-rule --name localelive-backend-warmup

# Re-enable
aws events enable-rule --name localelive-backend-warmup

# Delete entirely
aws events remove-targets --rule localelive-backend-warmup \
  --ids localelive-backend-warmup-target
aws events delete-rule --name localelive-backend-warmup
aws lambda remove-permission --function-name localelive-backend \
  --statement-id allow-eventbridge-warmup
```
