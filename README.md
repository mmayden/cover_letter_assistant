## Model and Prompt Engineering
- Switched from `flan-t5-base` to xAI’s Grok API for high-quality cover letter generation.
- Resolved 400 Bad Request errors by adopting `/v1/chat/completions` with `messages` format.
- Designed structured prompts with `system` and `user` roles, specifying sentence counts and avoiding clichés for tailored outputs.
- Optimized API parameters (`max_tokens=400`, `temperature=0.7`) for professional results.