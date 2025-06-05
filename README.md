## Improvements
- Enhanced output formatting with double newlines between paragraphs, achieved by updating Grok’s prompt and Flask template styling (`white-space: pre-wrap`).
- Improved content quality to match professional cover letters by refining the prompt to include specific, quantifiable examples and a personal background narrative.
- Added a 'Background' input field to personalize cover letters, capturing user career context (e.g., years in IT, transitioning to AI).
- Optimized Grok API parameters (`max_tokens=600`, `temperature=0.7`) for detailed, tailored outputs.

## Prompt Engineering
- Iterated prompts to ensure structured, 200-250 word cover letters with two body paragraphs (skills and company alignment).
- Emphasized specific, quantifiable examples (e.g., 'improved efficiency by 20%') and avoided clichés for authenticity.
- Tailored outputs to company achievements and user background, enhancing relevance and professionalism.