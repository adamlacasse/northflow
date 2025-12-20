# TODO

## UX issue: login-first experience

**Goal**
Make the application feel like it has a real “login gate” so that, when a user is not connected to the database, the only available action is to log in. After a successful login, show the main navigation actions.

**Current behavior (what we want for grading)**
- Not logged in: only `Login` is available in the top-right navigation.
- Logged in: show `Questions`, `Summary`, and `Logout` in the top-right navigation.
- Visiting `/` should route the user to the right place (login if not connected, questions if connected).

## Gameplan (next steps)

1. Confirm navigation gating is correct
   - Not logged in: no `Home`, no `Questions`, no `Summary`, no `Logout`.
   - Logged in: show only `Questions`, `Summary`, `Logout`.

2. Confirm route gating matches README
   - `/` redirects to `/login` when not connected.
   - `/` redirects to `/questions` when connected.

3. Improve the login page UX (if needed)
   - Pre-fill host/user/port with config defaults.
   - Display clear success/failure messages (already via flash).

4. Ensure docs stay in sync
   - Keep README and `.agent/.github` docs aligned as we make UX tweaks.
