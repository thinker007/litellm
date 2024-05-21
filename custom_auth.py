from fastapi import (
    FastAPI,
    Request,
    HTTPException,
    status,
    Depends,
    Header,
    Response,
    Form,
    UploadFile,
    File,
)
try:
    import fastapi
    import backoff
    import yaml
    import orjson
    import logging
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
except ImportError as e:
    raise ImportError(f"Missing dependency {e}. Run `pip install 'litellm[proxy]'`")

from litellm.proxy._types import UserAPIKeyAuth

async def user_api_key_auth(request: Request, api_key: str) -> UserAPIKeyAuth: 
    try: 
        modified_master_key = "sk-7cfAKBQNaAsWqUM93fF8D863Df62496eAf674d218a7614Ba"
        if api_key == modified_master_key:
            return UserAPIKeyAuth(api_key=api_key)
        else:
            # Use orjson to parse JSON data, orjson speeds up requests significantly
            body = await request.body()
            data = orjson.loads(body)
            latest_message = data['messages'][-1]
            if latest_message['role'] == 'user':
                latest_user_message_content = latest_message['content']
                if latest_user_message_content.startswith('sk-'):
                    api_key = latest_user_message_content.strip()
                    if api_key == modified_master_key:
                        return UserAPIKeyAuth(api_key=api_key,user_role="new_api_user")

            return UserAPIKeyAuth(api_key="None",)
    except: 
        raise Exception