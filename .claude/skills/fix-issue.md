---
name: fix-issue
description: Diagnose and fix a bug with proper verification
---

# Fix Issue

## Workflow

1. **Reproduce** — Understand the symptom. Check backend logs:
   ```bash
   docker-compose logs --tail 50 backend
   ```
   Check frontend console errors if UI-related.

2. **Diagnose** — Identify the root cause:
   - Backend error? Check router -> service -> model chain
   - Frontend error? Check component -> service -> API call chain
   - Field mismatch? Compare backend schema with frontend model
   - 401/403? Check auth interceptor and token flow
   - 404/405? Check URL pattern matches between frontend service and backend router

3. **Fix** — Make minimal changes to fix the root cause. Don't refactor surrounding code.

4. **Verify** — Test the fix:
   - Backend: `curl` the endpoint or check Swagger at `localhost:8000/docs`
   - Frontend: Rebuild and test in browser
   ```bash
   docker-compose build --no-cache {service} && docker-compose up -d
   docker-compose logs --tail 20 {service}
   ```

5. **Check for regressions** — Verify related features still work.

## Common Issues
- **[Object object] errors**: Backend returns `detail` as array (Pydantic validation). Frontend must handle both string and array.
- **NaN in calculations**: API returns Decimal as string. Use `Number()` coercion in TypeScript.
- **Stale frontend**: Docker caches layers. Use `--no-cache` flag on rebuild.
- **bcrypt errors**: Pin `bcrypt==4.2.1` for passlib compatibility.
- **Dark mode broken**: Hardcoded hex color in SCSS. Replace with `var(--css-variable)`.
