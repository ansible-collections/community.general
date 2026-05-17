# Git Rules

- Never mention any user or group  with `@` in the commit message.
- Before commiting changes:
  - Ensure you are in the right branch
  - If containing _code_ changes, look for unit and integration tests and apply them as possible
- When branching:
  - Always ensure you are branching off the `main` branch
  - Do not use `fix` or any other prefix indicating the type of the branch
  - If there is an issue associated with the branch, prefix the name with `####-` (where #### is the is issue number), e.g. if fixing issue 9999 about the xfconf module, name it like `9999-xfconf-something`.
