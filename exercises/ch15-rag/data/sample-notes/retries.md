# Retries and timeouts

## Which failures to retry
A retry is only safe for transient failures: HTTP 429, 5xx responses, timeouts and dropped connections.
A 400 or 401 will fail again in exactly the same way, so retrying only hides the bug.

## Backoff
Wait an exponentially growing random time (full jitter) between attempts, cap the wait, and give up
at a total deadline. Error code E0502 has nothing to do with retries; it is a Rust borrow-checker error.
