ROLE_PERMISSION={


    "admin":[
        "*"
    ],


    "manager":[
        "chat:use",
        "knowledge:read"
    ],


    "employee":[
        "chat:use"
    ]

}


def require_permission(permission):
    """FastAPI dependency factory for role-based endpoint protection."""
    from fastapi import Depends, HTTPException, status
    from app.auth.dependencies import get_current_user

    async def dependency(user=Depends(get_current_user)):
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
        return user

    return dependency



def has_permission(
    role,
    permission,
):

    permissions=(
        ROLE_PERMISSION
        .get(role,[])
    )


    return (
        "*"
        in permissions
        or
        permission
        in permissions
    )
