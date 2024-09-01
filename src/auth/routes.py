from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from src.auth.schemas import UserCreateModel, UserLoginModel, UserBookModel, PasswordResetRequestModel, PasswordResetConfirmModel
from src.auth.service import UserService
from sqlmodel import Session
from src.db.main import get_session
from src.auth.utils import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_password_hash
from datetime import timedelta, datetime
from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_jti_to_blocklist
from src.errors import UserAlreadyExists, InvalidCredentials, InvalidToken, UserNotFound
from src.mail import create_message, mail
from src.config import Config
from src.celery_tasks import send_email

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(['admin', 'user'])


@auth_router.post('/send_mail')
async def send_mail(emails: list[str], subject='Welcome to our app', body='<h1>Welcome to the app</h1>'):

    send_email.delay(emails, subject, body)
    return {'message': 'Email sent successfully'}


@auth_router.post('/signup')
async def create_user_account(user_data: UserCreateModel, bg_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    email = user_data.email

    user_exsist = user_service.user_exists(email, session)

    if user_exsist:
        raise UserAlreadyExists()

    new_user = user_service.create_user(user_data, session)

    token = create_url_safe_token({'email': email})

    link = f'http://{Config.DOMAIN}/api/v1/auth/verify/{token}'
    html_message = f'''
    <h1>Verify your email</h1>
    <p>Please click this <a href="{link}">link</a> to verify your email</p>

    '''
    send_email.delay([email, 'Verify your email', html_message])

    return {'message': 'Account Created! Check email to verify your account', 'user': new_user}


@auth_router.get('/verify/{token}')
async def verify_user_account(token: str, session: Session = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')

    if user_email:
        user = user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        user_service.update_user(user, {'is_verified': True}, session)

        return JSONResponse(content={
            'message': 'Account verified successfully'
        }, status_code=status.HTTP_200_OK)

    return JSONResponse(content={
        'message': 'Error occurred during verification'
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post('/login')
async def login_user(login_data: UserLoginModel, session: Session = Depends(get_session)):
    email = login_data.email
    password = login_data.password

    user = user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(user_data={
                'email': user.email,
                'user_id': str(user.id),
                'role': user.role
            })

            refresh_token = create_access_token(user_data={
                'email': user.email,
                'user_id': str(user.id)
            }, refresh=True, expiry=timedelta(days=2))

            return JSONResponse(content={
                'message': "Login Successful",
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'email': user.email,
                    'id': str(user.id)
                }
            })

    raise InvalidCredentials()


@auth_router.get('/refresh_token')
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_access_token(user_data=token_details['user'])
        return JSONResponse(content={
            'access_token': new_access_token,

        })

    raise InvalidToken()


@auth_router.get('/me')
async def get_current(user=Depends(get_current_user), _: bool = Depends(role_checker)) -> UserBookModel:
    return user


@auth_router.get('/logout')
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details['jti']
    await add_jti_to_blocklist(jti)

    return JSONResponse(content={
        'message': 'Logged out'
    }, status_code=status.HTTP_200_OK)


@auth_router.post('/password-reset-request')
async def password_reset_request(email_data: PasswordResetRequestModel):
    email = email_data.email

    token = create_url_safe_token({'email': email})

    link = f'http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}'
    html_message = f'''
    <h1>Reset Your Password</h1>
    <p>Please click this <a href="{link}">link</a> to Reset your Password</p>

    '''
    message = create_message(
        [email], subject='Reset Your Password', body=html_message)

    await mail.send_message(message)

    return JSONResponse(content={'message': 'Please check your email for instructions to reset your password'}, status_code=status.HTTP_200_OK)


@auth_router.post('/password-reset-confirm/{token}')
async def reset_account_password(token: str, passwords: PasswordResetConfirmModel, session: Session = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    user_email = token_data.get('email')

    if passwords.new_password != passwords.confirm_new_password:
        raise HTTPException(detail='Passwords do not match',
                            status_code=status.HTTP_400_BAD_REQUEST)
    if user_email:
        user = user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        user_service.update_user(
            user, {'password_hash': generate_password_hash(passwords.new_password)}, session)

        return JSONResponse(content={
            'message': 'Password reset successfully'
        }, status_code=status.HTTP_200_OK)

    return JSONResponse(content={
        'message': 'Error occurred during password reset'
    }, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
