from http import HTTPStatus
from unittest.mock import ANY

import pytest

pytestmark = pytest.mark.asyncio


class UserAuthorisationApi:
    register_url = '/register'
    login_url = '/login'
    refresh_url = '/refresh'
    logout_url = '/logout'
    update_url = '/update'
    get_sessions_url = '/get_sessions'

    async def register_and_login(self, make_post_request, email, password):
        json = {
            'email': email,
            'password': password,
        }
        response = await make_post_request(url_ending=self.register_url, json=json)
        assert response.status == HTTPStatus.CREATED

        response = await make_post_request(url_ending=self.login_url, json=json)
        assert response.status == HTTPStatus.OK
        return response


class TestRegisterUser(UserAuthorisationApi):

    async def test_register(
            self,
            make_post_request,
            email,
            password,
    ):
        json = {
            'email': email,
            'password': password,
        }

        response = await make_post_request(url_ending=self.register_url, json=json)

        body = await response.text()
        assert response.status == HTTPStatus.CREATED
        assert body == ''

    @pytest.mark.parametrize(
        'incorrect_email',
        [
            'aaa',
            'aaa.com',
            'aaa@aaa'
        ])
    async def test_register_incorrect_email(
            self,
            make_post_request,
            incorrect_email,
            password,
    ):
        json = {
            'email': incorrect_email,
            'password': password,
        }

        response = await make_post_request(url_ending=self.register_url, json=json)

        body = await response.json()
        assert response.status == HTTPStatus.BAD_REQUEST
        assert body == {'message': f'Not valid email {incorrect_email}'}

    async def test_register_twice(
            self,
            make_post_request,
            email,
            password,
    ):
        json = {
            'email': email,
            'password': password,
        }
        await make_post_request(url_ending=self.register_url, json=json)

        response = await make_post_request(url_ending=self.register_url, json=json)

        body = await response.json()
        assert response.status == HTTPStatus.BAD_REQUEST
        assert body == {'message': 'User has already registered'}


class TestLoginUser(UserAuthorisationApi):

    async def test_login_not_found(
            self,
            make_post_request,
            email,
            password,
    ):
        json = {
            'email': email,
            'password': password,
        }

        response = await make_post_request(url_ending=self.login_url, json=json)

        body = await response.json()
        assert response.status == HTTPStatus.NOT_FOUND
        assert body == {"message": "User not found"}

    async def test_login(
            self,
            make_post_request,
            email,
            password,
    ):
        response = await self.register_and_login(make_post_request, email, password)

        body = await response.json()
        assert body.get('access_token')
        assert body.get('refresh_token')

        access_token_cookie = response.cookies.get('access_token_cookie')
        assert access_token_cookie.value
        assert access_token_cookie.get('httponly')

        assert response.cookies.get('refresh_token_cookie').value
        assert response.cookies['refresh_token_cookie'].get('httponly')

    async def test_login_wrong_pass(
            self,
            make_post_request,
            email,
            password,
    ):
        json = {
            'email': email,
            'password': password,
        }
        response = await make_post_request(url_ending=self.register_url, json=json)
        assert response.status == HTTPStatus.CREATED

        json['password'] = '12345'

        response = await make_post_request(url_ending=self.login_url, json=json)

        body = await response.json()
        assert response.status == HTTPStatus.UNAUTHORIZED
        assert body == {'message': 'Bad username or password'}


class TestRefreshUser(UserAuthorisationApi):

    async def test_refresh(
            self,
            make_post_request,
            email,
            password,
    ):
        response = await self.register_and_login(make_post_request, email, password)

        access_cookie = response.cookies.get('access_token_cookie').value
        refresh_cookie = response.cookies.get('refresh_token_cookie').value

        response = await make_post_request(
            url_ending=self.refresh_url,
            cookies=response.cookies,
            headers=response.headers,
        )

        body = await response.json()
        assert body == ''

        new_access_cookie = response.cookies.get('access_token_cookie').value
        new_refresh_cookie = response.cookies.get('refresh_token_cookie').value
        assert new_access_cookie
        assert new_refresh_cookie
        assert new_access_cookie != access_cookie
        assert new_refresh_cookie != refresh_cookie

    async def test_refresh_empty(
            self,
            make_post_request,
            email,
            password,
    ):
        response = await make_post_request(
            url_ending=self.refresh_url,
        )
        assert response.status == HTTPStatus.UNAUTHORIZED

        body = await response.json()
        assert body == {'msg': 'Missing cookie "refresh_token_cookie"'}

        new_access_cookie = response.cookies.get('access_token_cookie')
        new_refresh_cookie = response.cookies.get('refresh_token_cookie')
        assert not new_access_cookie
        assert not new_refresh_cookie


class TestLogoutUser(UserAuthorisationApi):

    async def test_logout(
            self,
            make_post_request,
            email,
            password,
    ):
        response = await self.register_and_login(make_post_request, email, password)

        response = await make_post_request(
            url_ending=self.logout_url,
            cookies=response.cookies,
            headers=response.headers,
        )
        assert response.status == HTTPStatus.OK

        body = await response.json()
        assert body == {'message': 'logout successful'}

        assert not response.cookies.get('access_token_cookie').value
        assert not response.cookies.get('refresh_token_cookie').value

    async def test_logout_unauthorised(
            self,
            make_post_request,
            email,
            password,
    ):
        response = await make_post_request(url_ending=self.logout_url)
        assert response.status == HTTPStatus.UNAUTHORIZED


class TestUpdateUser(UserAuthorisationApi):

    async def test_update(
            self,
            make_post_request,
            email,
            password,
            email2,
    ):
        response = await self.register_and_login(make_post_request, email, password)

        json_new = {
            'email': email2,
            'password': password,
        }
        response = await make_post_request(
            url_ending=self.update_url,
            json=json_new,
            cookies=response.cookies,
        )
        assert response.status == HTTPStatus.OK

        body = await response.json()
        assert body == {'message': 'User updated'}

        assert response.cookies.get('access_token_cookie').value
        assert response.cookies.get('refresh_token_cookie').value

    async def test_update_unauthorised(
            self,
            make_post_request,
    ):
        response = await make_post_request(
            url_ending=self.update_url,
        )
        assert response.status == HTTPStatus.UNAUTHORIZED


class TestGetSessions(UserAuthorisationApi):

    async def test_get_sessions(
            self,
            make_post_request,
            make_get_request,
            email,
            password,
    ):
        response = await self.register_and_login(make_post_request, email, password)

        response = await make_get_request(
            url_ending=self.get_sessions_url,
            cookies=response.cookies,
        )
        assert response.status == HTTPStatus.OK

        body = await response.json()
        assert body == [
            {
                'auth_date': ANY,
                'user_agent': ANY,
            }
        ]

    async def test_get_sessions_unauthorised(
            self,
            make_get_request,
    ):
        response = await make_get_request(
            url_ending=self.get_sessions_url,
        )
        assert response.status == HTTPStatus.UNAUTHORIZED
