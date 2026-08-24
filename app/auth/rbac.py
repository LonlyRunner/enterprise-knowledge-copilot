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