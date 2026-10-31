### Introduction

Your prompt library from Migrations with Alembic has a problem: anyone who can reach it can read, change or delete every prompt in it. That's fine on your laptop. It's not fine once the API is on the internet, where every request that reaches a model costs you money and every record might belong to a different person.

This lesson adds **user accounts**. People register with an email and a password, log in to get a **token** (a string that proves who they are), and send that token with every request. Your API checks the token, works out which user is calling, and only ever shows that user their own records. Two words come up constantly here, and they mean different things. **Authentication** answers "who are you?" **Authorization** answers "are you allowed to do this?" You need both, and most real security bugs in APIs are authorization bugs: the code knew exactly who the user was and showed them someone else's data anyway.

### Lesson overview

This section contains a general overview of topics that you will learn in this lesson.

- Why you store a password hash and never the password, and which library to hash with.
- How to store users in Postgres with SQLModel, and add them with an Alembic migration.
- How registering and logging in work, and what a JWT is.
- JWTs versus opaque tokens, and when to use a hosted auth provider instead.
- How a `get_current_user` dependency protects routes.
- When to return 401, 403 or 404, and how to keep each user's data separate.
- How to test protected routes with dependency overrides.

### Never store passwords

The first rule of accounts is that your database never holds anyone's password. Databases leak: a backup gets copied to the wrong place, a SQL injection bug slips through, an employee's laptop is stolen. People reuse passwords, so a leaked list of passwords from your little API unlocks their email and their bank.

Instead you store a **password hash**. A hash function turns any input into a fixed-length string, and it only works one way: you can't run it backward to get the password. When someone logs in, you hash what they typed and compare it with the stored hash. You never need the original.

Not just any hash will do. The hash functions you may have heard of, such as SHA-256, are designed to be *fast*, and fast is exactly wrong here. An attacker with a stolen hash list and a graphics card can try billions of SHA-256 guesses a second. **Password hashing functions** are deliberately slow and memory-hungry, so each guess costs real time. They also add a **salt**, a random value mixed into each password before hashing and stored alongside the hash, so two users with the same password get different hashes and an attacker can't use one precomputed table for everyone. The current recommendation, from [OWASP's password storage guide](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), is **Argon2id**.

In Python, use **pwdlib** with its Argon2 extra. Older tutorials, including older versions of FastAPI's own docs, use a library called passlib. It hasn't been maintained for years and breaks with current versions of its dependencies, so skip it. Here is all pwdlib needs:

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()      # Argon2id with sensible settings
stored = password_hash.hash("correct horse battery")
print(stored)                                    # $argon2id$v=19$m=65536,t=3,p=4$...
print(password_hash.verify("correct horse battery", stored))  # True
print(password_hash.verify("wrong guess", stored))            # False
```

The stored string records the algorithm, its settings and the salt, so `verify` has everything it needs. Hashing takes a noticeable fraction of a second on purpose. Never write your own hashing or comparison code; this is one place where "use the boring library" is the whole lesson.

### Users in Postgres

Add the libraries to your prompt library project. `fastapi[standard]` already brought `python-multipart` (for the login form) and `email-validator` (for checking email addresses):

```bash
uv add "pwdlib[argon2]" pyjwt
```

Users are a table like any other. Add these to `models.py`, next to your prompt models:

```python
from datetime import UTC, datetime

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "user_account"             # "user" is a reserved word in Postgres
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(max_length=320, unique=True, index=True)
    hashed_password: str                       # never the password itself
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), sa_type=DateTime(timezone=True)
    )


class UserCreate(SQLModel):                    # what a client sends to register
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserPublic(SQLModel):                    # what the API returns: no hash
    id: int
    email: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class PromptBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, index=True)
    text: str = Field(min_length=1)


class Prompt(PromptBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user_account.id", index=True)


class PromptCreate(PromptBase):                # no owner_id: the server sets it
    pass


class PromptPublic(PromptBase):
    id: int
```

This shows only the fields that matter for auth. Keep `description` and `slug` from Migrations with Alembic in your real `models.py`, or autogenerate will try to drop them.

The table is named `user_account` because `user` is a reserved word in Postgres: SQLAlchemy quotes it for you, but every time you type `SELECT * FROM user` in `psql` you'd get the current database user instead of your table. `unique=True` on the email lets the database itself refuse a second account with the same address, which is safer than checking in Python, because two sign-ups at the same instant can both pass a Python check. The new `owner_id` column is a **foreign key**: the database guarantees it points at a real row in `user_account`, the same idea you met in SQL Fundamentals. Notice the separate models again. `UserPublic` has no `hashed_password`, and `PromptCreate` has no `owner_id`, so a client can neither read a hash nor claim to be someone else.

Now the migration. Run `uv run alembic revision --autogenerate -m "add users and prompt owners"` and review the draft, as Migrations with Alembic taught. It creates `user_account` and adds a required `owner_id` to `prompt`, which fails on a table that already has rows, for the same reason the `slug` column did. Edit `upgrade()` so it looks like this:

```python
def upgrade() -> None:
    op.create_table(
        "user_account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sqlmodel.AutoString(length=320), nullable=False),
        sa.Column("hashed_password", sqlmodel.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_account")),
    )
    op.create_index(op.f("ix_user_account_email"), "user_account", ["email"], unique=True)

    # Existing prompts have no owner. This is local practice data, so remove it.
    # On a database with real users, add owner_id as nullable, backfill it with
    # the right user's id, then make it required, as in the slug migration.
    op.execute("DELETE FROM prompt")
    op.add_column("prompt", sa.Column("owner_id", sa.Integer(), nullable=False))
    op.create_index(op.f("ix_prompt_owner_id"), "prompt", ["owner_id"], unique=False)
    op.create_foreign_key(
        op.f("fk_prompt_owner_id_user_account"), "prompt", "user_account", ["owner_id"], ["id"]
    )
```

Write the matching `downgrade()` in reverse order (drop the foreign key, the index and the column, then the index and the table), run `uv run alembic upgrade head`, and round-trip it with `downgrade -1` and `upgrade head`.

### Tokens: JWT or opaque

After a user logs in, every later request needs to prove who's calling without sending the password again. The server hands out a token, and the client sends it in a header on each request:

```text
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

"Bearer" means "whoever holds this token is allowed in", so a token is as sensitive as a password. There are two common kinds.

An **opaque token** is a long random string, such as one from `secrets.token_urlsafe(32)`, stored in a `session` table next to the user's ID. To check one, you look it up. It means nothing on its own, and to log someone out you delete the row.

A **JWT** (JSON Web Token, pronounced "jot") carries its own information. It's three base64-encoded parts joined by dots: a header naming the algorithm, a **payload** of **claims** such as `{"sub": "42", "exp": 1793212800}` ("subject is user 42, expires at this time"), and a **signature**. The server makes the signature from the header, the payload and a secret key only it knows. To check a token, the server recomputes the signature; if anyone changed a single character of the payload, it won't match. No database lookup is needed to know the token is genuine.

This lesson uses **JWTs**, for three reasons. They need no extra table. They're what FastAPI's security tutorial uses, so the docs you'll read match your code. And the deploy you'll set up in Deploying Your API has Render generate the signing secret, `AUTH_SECRET`, for you. The trade-offs are real, though:

- **You can't take a JWT back.** It stays valid until it expires, even if the user logs out or you ban them. The usual answer is a short lifetime, 15 to 60 minutes, and making users log in again (or adding "refresh tokens", which the extra resources cover). With opaque tokens, revoking is one `DELETE`.
- **The payload is readable by anyone.** Base64 is an encoding, not encryption. Paste a token into [jwt.io](https://jwt.io/) and you'll see its claims. Never put secrets or personal data in it; a user ID is enough.
- **Everything rests on one secret.** Anyone who has `AUTH_SECRET` can mint a token for any user. Keep it out of Git, as with every secret, and make it long: `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

If you'd rather not run accounts yourself at all, a **hosted auth provider** such as Auth0, Clerk or Supabase Auth handles sign-up, password resets, email verification and "log in with Google" for you. Your API then only verifies the JWTs the provider issues. Many real products do this, and it's a sensible choice for a startup. Building it yourself once is still worth it, because you'll understand what those services do and what can go wrong.

### Registering and logging in

Here is the auth module. Save it as `auth.py`:

```python
import os
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlmodel import select

from database import SessionDep
from models import User

AUTH_SECRET = os.environ["AUTH_SECRET"]           # a long random string, never in Git
ALGORITHM = "HS256"
TOKEN_LIFETIME = timedelta(minutes=30)

password_hash = PasswordHash.recommended()        # Argon2id with sensible settings
DUMMY_HASH = password_hash.hash("not-a-real-password")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")  # reads "Authorization: Bearer ..."


def authenticate(session: SessionDep, email: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.email == email.lower())).first()
    if user is None:
        password_hash.verify(password, DUMMY_HASH)  # take the same time either way
        return None
    if not password_hash.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    claims = {"sub": str(user_id), "iat": now, "exp": now + TOKEN_LIFETIME}
    return jwt.encode(claims, AUTH_SECRET, algorithm=ALGORITHM)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        claims = jwt.decode(token, AUTH_SECRET, algorithms=[ALGORITHM])  # checks signature and exp
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized
    user = session.get(User, user_id)
    if user is None:                              # the account was deleted
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
```

A few details are doing more work than they look:

- **`DUMMY_HASH`.** If an email doesn't exist, `authenticate` still runs one slow `verify`. Otherwise "no such user" would answer instantly and "wrong password" would take a quarter of a second, and an attacker could time your login to discover which emails have accounts.
- **`algorithms=[ALGORITHM]`** is required by PyJWT, and it matters: it stops an attacker from sending a token that claims a different (or no) algorithm.
- **`jwt.decode` checks `exp` for you** and raises `ExpiredSignatureError`, a kind of `InvalidTokenError`, so expired, tampered and garbage tokens all end up as the same `401`.
- **`OAuth2PasswordBearer`** reads the `Authorization` header and returns the token, or answers `401` itself when the header is missing. `tokenUrl` tells the `/docs` page where to log in, which gives you a working **Authorize** button there.

Now the routes in `main.py`:

```python
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from auth import CurrentUser, authenticate, create_access_token, password_hash
from database import SessionDep
from models import Prompt, PromptCreate, PromptPublic, Token, User, UserCreate, UserPublic

app = FastAPI(title="Prompt Library")


@app.post("/register", status_code=201, response_model=UserPublic)
def register(body: UserCreate, session: SessionDep):
    user = User(email=body.email.lower(), hashed_password=password_hash.hash(body.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:                        # the unique constraint on email
        session.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    session.refresh(user)
    return user


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = authenticate(session, form.username, form.password)  # "username" holds the email
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))


@app.get("/me", response_model=UserPublic)
def read_me(user: CurrentUser):
    return user


@app.post("/prompts", status_code=201, response_model=PromptPublic)
def create_prompt(body: PromptCreate, user: CurrentUser, session: SessionDep):
    prompt = Prompt.model_validate(body, update={"owner_id": user.id})  # owner comes from the token
    session.add(prompt)
    session.commit()
    session.refresh(prompt)
    return prompt


@app.get("/prompts/{prompt_id}", response_model=PromptPublic)
def read_prompt(prompt_id: int, user: CurrentUser, session: SessionDep):
    prompt = session.get(Prompt, prompt_id)
    if prompt is None or prompt.owner_id != user.id:  # someone else's looks the same as missing
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt
```

`/token` takes a **form**, not JSON, because that's what the OAuth2 "password flow" standard says, and it's what the `/docs` Authorize button sends. The standard calls the field `username`, so your users type their email into it. The login error says "incorrect email or password" without saying which, for the same reason as the dummy hash. Try it: set `AUTH_SECRET` in your `.env`, run `uv run fastapi dev main.py`, register at `/docs`, click **Authorize**, and call `/me`.

### The current user dependency

`get_current_user` is the heart of the lesson. It's an ordinary FastAPI dependency, like `get_session`, but it depends on two others: the token from `oauth2_scheme` and a database session. FastAPI resolves that whole chain for each request. Any route that adds `user: CurrentUser` to its parameters is now protected: the route body only runs if the token is valid, and `user` is a real `User` row loaded from Postgres.

That single parameter is also how you enforce ownership. `create_prompt` sets `owner_id` from `user.id`, never from the request body. Every query that reads records must filter by the owner too. For a list route that means `select(Prompt).where(Prompt.owner_id == user.id)`; for a single record, check `owner_id` after loading it, as `read_prompt` does. Do this in every route, because the one you forget is the one that leaks. Some teams write a small helper, such as `get_owned_or_404(session, Prompt, prompt_id, user)`, so there's only one place to get it right.

### 401 403 or 404

Three status codes cover "you can't have this", and choosing correctly matters, because clients act on them:

- **401 Unauthorized** means "I don't know who you are." The token is missing, malformed, expired or signed with the wrong key. (The name is a historical mistake: it's really about authentication.) The client's fix is to log in again, and the `WWW-Authenticate: Bearer` header tells it how.
- **403 Forbidden** means "I know who you are, and you may not do this." Use it for actions, not specific records: a regular user calling an admin-only route, or a free-tier user calling a paid feature.
- **404 Not Found** for someone else's record. If user B asks for prompt 7 and it belongs to user A, answering `403` confirms that prompt 7 exists, and by trying IDs 1, 2, 3 and so on, B learns how many records you have. Answering `404` makes another user's record indistinguishable from one that never existed. GitHub does exactly this for private repositories.

This bug class, where a user changes an ID in the URL and gets someone else's data, is so common it tops the [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) as "broken object level authorization". Sequential IDs make it easy to try; the owner check is what makes it fail.

### Testing protected routes

You test auth the same way you've tested everything since FastAPI Basics: with `TestClient`, an in-memory database and dependency overrides. There are two styles, and a good test suite uses both. Save this as `test_auth.py`:

```python
import os

os.environ.setdefault("AUTH_SECRET", "test-secret-at-least-32-bytes-long!!")  # before importing auth

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from auth import get_current_user
from database import get_session
from main import app
from models import User


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session):
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


def login(client, email: str) -> dict[str, str]:
    """Register and log in through the real endpoints; return an auth header."""
    client.post("/register", json={"email": email, "password": "correct horse battery"})
    r = client.post("/token", data={"username": email, "password": "correct horse battery"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_register_login_and_me(client):
    headers = login(client, "ada@example.com")
    assert client.get("/me", headers=headers).json()["email"] == "ada@example.com"


def test_wrong_password_is_401(client):
    login(client, "ada@example.com")
    r = client.post("/token", data={"username": "ada@example.com", "password": "nope nope nope"})
    assert r.status_code == 401


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer not-a-jwt"}])
def test_missing_or_bad_token_is_401(client, headers):
    assert client.get("/me", headers=headers).status_code == 401


def test_other_users_prompt_is_404(client):
    ada, bob = login(client, "ada@example.com"), login(client, "bob@example.com")
    created = client.post("/prompts", json={"name": "s", "text": "Summarize"}, headers=ada)
    prompt_id = created.json()["id"]
    assert client.get(f"/prompts/{prompt_id}", headers=ada).status_code == 200
    assert client.get(f"/prompts/{prompt_id}", headers=bob).status_code == 404


def test_skip_login_with_an_override(client, session):
    user = User(email="test@example.com", hashed_password="x")
    session.add(user)
    session.commit()
    app.dependency_overrides[get_current_user] = lambda: user   # every request is this user
    assert client.get("/me").json()["email"] == "test@example.com"
```

The first four tests go through the real login, so they prove the whole flow works, including the two cases the LLM-Powered API project asks for: a bad token gets `401` and another user's record gets `404`. The last test shows the shortcut. Overriding `get_current_user` skips tokens entirely, which keeps tests about *other* features short: they just say "pretend this user is logged in". Use the shortcut for feature tests, and keep a handful of real-login tests so the auth itself stays covered. To test expiry, create a token with `jwt.encode` and an `exp` in the past, and check that `/me` returns `401`. Hashing is slow on purpose, so a suite with hundreds of logins will feel it; that's another reason to use the override for most tests.

<div class="lesson-note lesson-note--warning" markdown="1">

#### What this lesson leaves out

A production login system also needs rate limits on `/token` (so nobody can try a million passwords; you'll add per-user rate limits in Timeouts, Retries and Rate Limits), email verification, password resets, and HTTPS everywhere (your host provides it). For a browser front end, tokens usually live in secure, HTTP-only cookies rather than JavaScript-readable storage. These are the main reasons teams reach for a hosted provider.

</div>

### Assignment

<div class="lesson-content__panel" markdown="1">

1. Work through FastAPI's [Security tutorial](https://fastapi.tiangolo.com/tutorial/security/), because it builds the same flow step by step with more explanation of each piece.
   - Read "Security - First Steps", "Get Current User", "Simple OAuth2 with Password and Bearer" and "OAuth2 with Password (and hashing), Bearer with JWT tokens". It also uses pwdlib and PyJWT, so its code matches yours.
1. Read OWASP's [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) for why Argon2id is the recommendation and what salting and work factors do.
   - Read the introduction, "Background" and "Password Hashing Algorithms". You can skip the parts about upgrading legacy hashes.
1. Read [Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/) from the OWASP API Security Top 10, which shows real attack scenarios for the cross-user bug this lesson prevents.
1. Skim the [PyJWT usage examples](https://pyjwt.readthedocs.io/en/stable/usage.html), especially "Expiration Time Claim (exp)", to see which claims PyJWT checks for you.
1. Practice: add accounts to your summarizer API from Migrations with Alembic.
   - Add the `User` table and an `owner_id` on `Summary`, and write and review the Alembic migration. Round-trip it with `downgrade -1` and `upgrade head`.
   - Add `/register`, `/token` and `/me`. Protect `POST /summarize` and the summary routes with `CurrentUser`, and make `GET /summaries` list only the caller's summaries. Leave `GET /health` public.
   - Write tests for a missing token, a bad token, an expired token, the wrong password, and user B getting `404` for user A's summary. Use the `get_current_user` override for your other feature tests.
   - Log in through `/docs` with the Authorize button, copy your token into [jwt.io](https://jwt.io/), and confirm the payload holds only your user ID and timestamps.

</div>

### Knowledge check

The following questions are an opportunity to reflect on key topics in this lesson. If you can't answer a question, click on it to review the material, but keep in mind you are not expected to memorize or master this knowledge.

- [Why do you store a slow, salted password hash instead of the password or a SHA-256 hash, and which library should you use?](#never-store-passwords)
- [Why does the email column have a unique constraint, and why is the table not called user?](#users-in-postgres)
- [What is in a JWT, how does the server know it hasn't been changed, and why can't you revoke one before it expires?](#tokens-jwt-or-opaque)
- [Why does the login check a dummy hash when the email doesn't exist?](#registering-and-logging-in)
- [How does adding a CurrentUser parameter protect a route, and where must the owner ID come from?](#the-current-user-dependency)
- [When should an API return 401, 403 and 404, and why is 404 the right answer for another user's record?](#401-403-or-404)
- [What are the two ways to test protected routes, and when would you use each one?](#testing-protected-routes)

### Additional resources

This section contains helpful links to related content. It isn't required, so consider it supplemental.

- [The pwdlib documentation](https://frankie567.github.io/pwdlib/) covers its options, including upgrading old hashes with `verify_and_update`.
- [OWASP's Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) lists what a production login also needs: generic error messages, rate limiting, account lockout and more.
- [JWT.io's introduction](https://jwt.io/introduction) explains the three parts of a JWT with diagrams.
