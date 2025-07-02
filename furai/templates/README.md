## Caution

**DO NOT UPDATE HTML FILES DIRECTLY**

## Guide

In `furai` repository, export the email template with `pnpm email-export` and commit the template file along with the build version.

```sh
# pnpm email-export
> cd transactional && pnpm export

> react-email-starter@1.1.0 export /.../transactional
> email export

✔ Preparing files...

✔ Rendered all files
✔ Copying static files
out
└── auth-verification-code.html
✔ Successfully exported emails
```

Then copy the HTML output and paste it in a new file inside `/templates`.

[React Email CLI documentation](https://react.email/docs/cli)