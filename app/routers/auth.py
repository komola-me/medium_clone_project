from fastapi import APIRouter, HTTPException
from jose import JWTError, jwt

from app.models.user import User
from app.schemas.auth import UserCreate, TokenIn, TokenResponse, LoginInput
from app.dependencies import db_dep
from app.utils import hash_password, verify_password, generate_confirmation_token, create_jwt_token, decode_confirmation_token
from app.tasks import send_email
from app.config import FRONTEND_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(db: db_dep, user: UserCreate):
    existing_user_by_email = db.query(User).filter(User.email == user.email).first()
    if existing_user_by_email:
        raise HTTPException(status_code=400, detail="Email already in use")

    existing_user_by_username = db.query(User).filter(User.username == user.username).first()
    if existing_user_by_username:
        raise HTTPException(status_code=400, detail="Username already in use")

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password_hash),
        is_admin=False,
        is_active=False,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = generate_confirmation_token(email=user.email)

    send_email.delay(
        to_email=new_user.email,
        subject="Confirmation of SignUp to Medium",
        body = f"Hi, {new_user.username}, \n Please click the link to confirm your email: \n http://{FRONTEND_URL}/auth/verify-email/{token}",
    )

    return {
        "detail": f"Confirmation email has been sent to {new_user.email}. Please confirm to finilize your registration.",
    }


@router.get("/verify-email/{token}")
async def confirm_email(db: db_dep, token: str):
    try:
        email = decode_confirmation_token(token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, details="User not found")
        if user.is_verified:
            return {"detail": "User already confirmed."}

        user.is_verified = True
        user.is_active = True
        db.commit()

        return {"detail": "Email confirmed successfully"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Token is invalid or expired")


@router.post('/login', response_model=TokenResponse)
async def login(db: db_dep, login_data: LoginInput):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password_hash, user.password_hash):
        raise HTTPException(
            status_code=400, detail="User not found or you entered wrong credentials."
        )
    login_dict = {"email": user.email, "is_admin": user.is_admin}

    access_token = create_jwt_token(data={"sub": user.email}, expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_jwt_token(data=login_dict, expires_in_minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh/")
async def refresh_token(db: db_dep, token_data: TokenIn):
    try:
        email = jwt.decode(token_data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_jwt_token(
            data={"email": email},
            expires_in_minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        return {"access_token": new_access_token, "refresh_token": token_data.refresh_token, "token_type": "bearer"}

    except JWTError as err:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from err
    except jwt.ExpiredSignatureError as err:
        raise HTTPException(status_code=401, detail="Refresh token has expired") from err
    except Exception as err:
        raise HTTPException(status_code=400, detail="Something went wrong. Please try again.") from err