"""Tests for the IAM endpoints."""

from typing import Any

# Token tests


def test_create_role_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST.ROLE", "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"detail": "Role: TEST.ROLE created successfully."}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST.ROLE'
    """
    )
    assert len(result) == 1
    assert result[0] == ("TEST.ROLE", "A role for testing")


def test_create_role_invalid_token(test_client: Any) -> None:
    """Test creating a role with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"role_name": "NEW.ROLE", "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_create_group_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "NEW.GROUP", "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {"detail": "Group: NEW.GROUP created successfully."}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'NEW.GROUP'
    """
    )
    assert len(result) == 1
    assert result[0] == ("NEW.GROUP", "A group for testing")


def test_create_group_invalid_token(test_client: Any) -> None:
    """Test creating a group with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"group_name": "TEST.GROUP", "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_create_permission_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {
        "permission_name": "SEE.DASHBOARD",
        "permission_description": "Can see dashboard",
    }
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Permission: SEE.DASHBOARD created successfully."
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE.DASHBOARD'
    """
    )
    assert len(result) == 1
    assert result[0] == ("SEE.DASHBOARD", "Can see dashboard")


def test_create_permission_invalid_token(test_client: Any) -> None:
    """Test creating a permission with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {
        "permission_name": "SEE.DASHBOARD",
        "permission_description": "Can see dashboard",
    }
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_add_role_to_member_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a role to a member with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Role: TESOUREIRO added to member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "TESOUREIRO")


def test_add_role_to_member_invalid_token(test_client: Any) -> None:
    """Test adding a role to a member with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"role_name": "DIRETOR.REGIONAL", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_add_group_to_member_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a group to a member with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "SIG.MATEMATICA", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Group: SIG.MATEMATICA added to member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'SIG.MATEMATICA'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "SIG.MATEMATICA")


def test_add_group_to_member_invalid_token(test_client: Any) -> None:
    """Test adding a group to a member with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"group_name": "BETA.TESTER", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_add_permission_to_role_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Permission: EDIT.EVENT added to role: TESOUREIRO successfully."
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO' AND p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("TESOUREIRO", "EDIT.EVENT")


def test_add_permission_to_role_invalid_token(test_client: Any) -> None:
    """Test adding a permission to a role with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"role_name": "DIRETOR.REGIONAL", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_add_permission_to_group_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Permission: EDIT.EVENT added to group: BETA.TESTER successfully."
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "EDIT.EVENT")


def test_add_permission_to_group_invalid_token(test_client: Any) -> None:
    """Test adding a permission to a group with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    data = {"group_name": "TEST.GROUP", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_roles_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test getting roles with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/roles/", headers=headers)
    assert response.status_code == 200


def test_get_roles_invalid_token(test_client: Any) -> None:
    """Test getting roles with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/iam/roles/", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_groups_valid_token(test_client: Any, mock_valid_token: Any) -> None:
    """Test getting groups with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/groups/", headers=headers)
    assert response.status_code == 200


def test_get_groups_invalid_token(test_client: Any) -> None:
    """Test getting groups with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get("/iam/groups/", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_members_by_role_name_valid_token(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting members by"Field: \\ role_name\" with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/role/", params={"role_name": "DIRETOR.REGIONAL"}, headers=headers
    )
    assert response.status_code == 200


def test_get_members_by_role_name_invalid_token(test_client: Any) -> None:
    """Test getting members by"Field: \\ role_name\" with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get(
        "/iam/members/role/", params={"role_name": "DIRETOR.REGIONAL"}, headers=headers
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_members_by_group_name_valid_token(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting members by"Field: \\ group_name\" with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/group/", params={"group_name": "BETA.TESTER"}, headers=headers
    )
    assert response.status_code == 200


def test_get_members_by_group_name_invalid_token(test_client: Any) -> None:
    """Test getting members by"Field: \\ group_name\" with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get(
        "/iam/members/group/", params={"group_name": "TEST.GROUP"}, headers=headers
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_role_permissions_valid_token(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting role permissions with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/role_permissions/",
        params={"role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 200


def test_get_role_permissions_invalid_token(test_client: Any) -> None:
    """Test getting role permissions with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get(
        "/iam/role_permissions/",
        params={"role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_get_group_permissions_valid_token(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting group permissions with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/group_permissions/", params={"group_name": "BETA.TESTER"}, headers=headers
    )
    assert response.status_code == 200


def test_get_group_permissions_invalid_token(test_client: Any) -> None:
    """Test getting group permissions with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.get(
        "/iam/group_permissions/", params={"group_name": "TEST.GROUP"}, headers=headers
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_update_role_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Role: DIRETOR.REGIONAL updated successfully."}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'UPDATED.ROLE'
    """
    )
    assert len(result) == 1
    assert result[0] == ("UPDATED.ROLE", "Updated Description")


def test_update_role_invalid_token(test_client: Any) -> None:
    """Test updating a role with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_update_group_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "group_name": "BETA.TESTER",
        "new_group_name": "BETA.TESTERS",
        "new_group_description": "UpdatedDesc",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Group: BETA.TESTER updated successfully."}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTERS'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTERS", "UpdatedDesc")


def test_update_group_invalid_token(test_client: Any) -> None:
    """Test updating a group with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    json = {
        "group_name": "TEST.GROUP",
        "new_group_name": "UPDATED.GROUP",
        "new_group_description": "UpdatedDesc",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_update_permission_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": "WHATSAPP.BOT",
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Desc",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT updated successfully."
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'UPDATED.PERMISSION'
    """
    )
    assert len(result) == 1
    assert result[0] == ("UPDATED.PERMISSION", "Updated Desc")


def test_update_permission_invalid_token(test_client: Any) -> None:
    """Test updating a permission with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    json = {
        "permission_name": "WHATSAPP.BOT",
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Desc",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_remove_role_from_member_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_role_from_member/",
        json={"role_name": "DIRETOR.REGIONAL", "member_id": 5},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Role: DIRETOR.REGIONAL removed from member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
    """
    )
    assert len(result) == 0


def test_remove_role_from_member_invalid_token(test_client: Any) -> None:
    """Test removing a role from a member with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.delete(
        "/iam/remove_role_from_member/",
        params={"role_name": "DIRETOR.REGIONAL", "member_id": 5},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_remove_group_from_member_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json={"group_name": "BETA.TESTER", "member_id": 5},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Group: BETA.TESTER removed from member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
    """
    )
    assert len(result) == 0


def test_remove_group_from_member_invalid_token(test_client: Any) -> None:
    """Test removing a group from a member with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.delete(
        "iam/remove_group_from_member/",
        params={"group_name": "TEST.GROUP", "member_id": 5},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_remove_permission_from_role_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json={"permission_name": "CREATE.EVENT", "role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: CREATE.EVENT removed from role: DIRETOR.REGIONAL successfully."
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'CREATE.EVENT'
    """
    )
    assert len(result) == 0


def test_remove_permission_from_role_invalid_token(test_client: Any) -> None:
    """Test removing a permission from a role with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.delete(
        "/iam/remove_permission_from_role/",
        params={"permission_name": "WHATSAPP.BOT", "role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_remove_permission_from_group_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json={"permission_name": "WHATSAPP.BOT", "group_name": "BETA.TESTER"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT removed from group: BETA.TESTER successfully."
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'WHATSAPP.BOT'
    """
    )
    assert len(result) == 0


def test_remove_permission_from_group_invalid_token(test_client: Any) -> None:
    """Test removing a permission from a group with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.delete(
        "/iam/remove_permission_from_group/",
        params={"permission_name": "WHATSAPP.BOT", "group_name": "TEST.GROUP"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_delete_role_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_role/",
        json={"role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Role: DIRETOR.REGIONAL deleted successfully."}

    result = run_db_query(
        """
        SELECT role_name
        FROM iam_roles
        WHERE role_name = 'DIRETOR.REGIONAL'
    """
    )
    assert len(result) == 0


def test_delete_role_invalid_token(test_client: Any) -> None:
    """Test deleting a role with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_role/",
        json={"role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_delete_group_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_group/",
        json={"group_name": "BETA.TESTER"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Group: BETA.TESTER deleted successfully."}

    result = run_db_query(
        """
        SELECT group_name
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
    """
    )
    assert len(result) == 0


def test_delete_group_invalid_token(test_client: Any) -> None:
    """Test deleting a group with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_group/",
        json={"group_name": "TEST.GROUP"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


def test_delete_permission_valid_token(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with a valid token."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_permission/",
        json={"permission_name": "WHATSAPP.BOT"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT deleted successfully."
    }

    result = run_db_query(
        """
        SELECT permission_name
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
    """
    )
    assert len(result) == 0


def test_delete_permission_invalid_token(test_client: Any) -> None:
    """Test deleting a permission with an invalid token."""

    headers = {"Authorization": "Bearer invalid-token"}
    response = test_client.request(
        method="delete",
        url="/iam/delete_permission/",
        json={"permission_name": "WHATSAPP.BOT"},
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid Token"}


### SPECIFIF ENDPOINT TESTS ###

## POST ENDPOINTS ##

# 01/24 /iam/create_role/


def test_create_role_missing_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "input": {"role_description": "A role for testing"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_description = 'A role for testing'
    """
    )
    assert len(result) == 0


def test_create_role_missing_role_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with missing role_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST.ROLE"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "role_description"],
                "msg": "Field required",
                "input": {"role_name": "TEST.ROLE"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST.ROLE'
    """
    )
    assert len(result) == 0


def test_create_role_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with invalid role_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": 123, "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_description = 'A role for testing'
    """
    )
    assert len(result) == 0


def test_create_role_invalid_role_description_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with invalid role_description type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST.ROLE", "role_description": 123}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_description" must be a string.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST.ROLE'
    """
    )
    assert len(result) == 0


def test_create_role_empty_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with empty role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "", "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_description = 'A role for testing'
    """
    )
    assert len(result) == 0


def test_create_role_name_contain_spaces(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with role_name containing spaces."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST ROLE", "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot contain spaces.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST ROLE'
    """
    )
    assert len(result) == 0


def test_create_role_numeric_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with numeric role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "123", "role_description": "A role for testing"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_description = 'A role for testing'
    """
    )
    assert len(result) == 0


def test_create_role_empty_role_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with empty role_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST.ROLE", "role_description": ""}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_description" cannot be empty.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST.ROLE'
    """
    )
    assert len(result) == 0


def test_create_role_numeric_role_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role with numeric role_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TEST.ROLE", "role_description": "123"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_description" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TEST.ROLE'
    """
    )
    assert len(result) == 0


def test_create_role_already_exists(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a role that already exists."""

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 1
    assert result[0][0] == "TESOUREIRO"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "role_description": "A role that already exists"}
    response = test_client.post("/iam/create_role/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Role: TESOUREIRO already exists."}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 1
    assert result[0][0] == "TESOUREIRO"


# 02/24 /iam/create_group/


def test_create_group_missing_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with missing group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "input": {"group_description": "A group for testing"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_description = 'A group for testing'
    """
    )
    assert len(result) == 0


def test_create_group_missing_group_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with missing group_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "TEST.GROUP"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "group_description"],
                "msg": "Field required",
                "input": {"group_name": "TEST.GROUP"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'TEST.GROUP'
    """
    )
    assert len(result) == 0


def test_create_group_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with invalid group_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": 123, "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_description = 'A group for testing'
    """
    )
    assert len(result) == 0


def test_create_group_invalid_group_description_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with invalid group_description type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "TEST.GROUP", "group_description": 123}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_description" must be a string.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'TEST.GROUP'
    """
    )
    assert len(result) == 0


def test_create_group_empty_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with empty group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "", "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_description = 'A group for testing'
    """
    )
    assert len(result) == 0


def test_create_group_name_contain_spaces(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with group_name containing spaces."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "TEST GROUP", "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot contain spaces.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'TEST GROUP'
    """
    )
    assert len(result) == 0


def test_create_group_numeric_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with numeric group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "123", "group_description": "A group for testing"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_description = 'A group for testing'
    """
    )
    assert len(result) == 0


def test_create_group_empty_group_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with empty group_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "TEST.GROUP", "group_description": ""}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_description" cannot be empty.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'TEST.GROUP'
    """
    )
    assert len(result) == 0


def test_create_group_numeric_group_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group with numeric group_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "TEST.GROUP", "group_description": "123"}
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "group_description" cannot be numeric.'
    }

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'TEST.GROUP'
    """
    )
    assert len(result) == 0


def test_create_group_already_exists(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a group that already exists."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {
        "group_name": "BETA.TESTER",
        "group_description": "A group that already exists",
    }
    response = test_client.post("/iam/create_group/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Group: BETA.TESTER already exists."}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "Grupo de testadores beta da Mensa Brasil.")


# 03/24 /iam/create_permission/


def test_create_permission_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with missing permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_description": "Can see dashboard"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "input": {"permission_description": "Can see dashboard"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_description = 'Can see dashboard'
    """
    )
    assert len(result) == 0


def test_create_permission_missing_permission_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with missing permission_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "SEE.DASHBOARD"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "permission_description"],
                "msg": "Field required",
                "input": {"permission_name": "SEE.DASHBOARD"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE.DASHBOARD'
    """
    )
    assert len(result) == 0


def test_create_permission_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with invalid permission_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": 123, "permission_description": "Can see dashboard"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_description = 'Can see dashboard'
    """
    )
    assert len(result) == 0


def test_create_permission_invalid_permission_description_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with invalid permission_description type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "SEE.DASHBOARD", "permission_description": 123}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "permission_description" must be a string.'
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE.DASHBOARD'
    """
    )
    assert len(result) == 0


def test_create_permission_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with empty permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "", "permission_description": "Can see dashboard"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_description = 'Can see dashboard'
    """
    )
    assert len(result) == 0


def create_permission_name_contain_spaces(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with permission_name containing spaces."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {
        "permission_name": "SEE DASHBOARD",
        "permission_description": "Can see dashboard",
    }
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "permission_name" cannot contain spaces.'
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE DASHBOARD'
    """
    )
    assert len(result) == 0


def test_create_permission_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with numeric permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "123", "permission_description": "Can see dashboard"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_description = 'Can see dashboard'
    """
    )
    assert len(result) == 0


def test_create_permission_empty_permission_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with empty permission_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "SEE.DASHBOARD", "permission_description": ""}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "permission_description" cannot be empty.'
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE.DASHBOARD'
    """
    )
    assert len(result) == 0


def test_create_permission_numeric_permission_description(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission with numeric permission_description."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "SEE.DASHBOARD", "permission_description": "123"}
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "permission_description" cannot be numeric.'
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'SEE.DASHBOARD'
    """
    )
    assert len(result) == 0


def test_create_permission_already_exists(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test creating a permission that already exists."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {
        "permission_name": "CREATE.EVENT",
        "permission_description": "A permission that already exists",
    }
    response = test_client.post("/iam/create_permission/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": "Permission: CREATE.EVENT already exists."}

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'CREATE.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("CREATE.EVENT", "Can create events.")


# 04/24 /iam/add_role_to_member/


def test_add_role_to_member_missing_role_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "input": {"member_id": 5},
            }
        ]
    }


def test_add_role_to_member_missing_member_id(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with missing member_id."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "DIRETOR.REGIONAL"}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "member_id"],
                "msg": "Field required",
                "input": {"role_name": "DIRETOR.REGIONAL"},
            }
        ]
    }


def test_add_role_to_member_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with invalid role_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": 123, "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}


def test_add_role_to_member_invalid_member_id_type(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with invalid member_id type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "DIRETOR.REGIONAL", "member_id": "five"}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "member_id" must be an integer.'}


def test_add_role_to_member_empty_role_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with empty role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}


def test_add_role_to_member_numeric_role_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with numeric role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "123", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}


def test_add_role_to_member_member_id_zero(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a role to a member with member_id zero."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "DIRETOR.REGIONAL", "member_id": 0}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "member_id" must be positive. (greater than 0)'
    }


def test_add_role_to_member_role_already_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a role to a member that already has the role."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "DIRETOR.REGIONAL", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Role: DIRETOR.REGIONAL already assigned to member with id: 5."
    }

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "DIRETOR.REGIONAL")


def test_add_role_to_member_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a role to a member with a role that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "NON.EXISTENT.ROLE", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'NON.EXISTENT.ROLE'
    """
    )
    assert len(result) == 0


def test_add_role_to_member_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a role to a member with valid data."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "member_id": 5}
    response = test_client.post("/iam/add_role_to_member/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Role: TESOUREIRO added to member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "TESOUREIRO")


# 05/24 /iam/add_group_to_member/


def test_add_group_to_member_missing_group_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with missing group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "input": {"member_id": 5},
            }
        ]
    }


def test_add_group_to_member_missing_member_id(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with missing member_id."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER"}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "member_id"],
                "msg": "Field required",
                "input": {"group_name": "BETA.TESTER"},
            }
        ]
    }


def test_add_group_to_member_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with invalid group_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": 123, "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}


def test_add_group_to_member_invalid_member_id_type(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with invalid member_id type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "member_id": "five"}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "member_id" must be an integer.'}


def test_add_group_to_member_empty_group_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with empty group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}


def test_add_group_to_member_numeric_group_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with numeric group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "123", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}


def test_add_group_to_member_member_id_zero(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test adding a group to a member with member_id zero."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "member_id": 0}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "member_id" must be positive. (greater than 0)'
    }


def test_add_group_to_member_group_already_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a group to a member that already has the group."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Group: BETA.TESTER already assigned to member with id: 5."
    }

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "BETA.TESTER")


def test_add_group_to_member_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a group to a member with a group that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "NON.EXISTENT.GROUP", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'NON.EXISTENT.GROUP'
    """
    )
    assert len(result) == 0


def test_add_group_to_member_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a group to a member with valid data."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "SIG.MATEMATICA", "member_id": 5}
    response = test_client.post("/iam/add_group_to_member/", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Group: SIG.MATEMATICA added to member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'SIG.MATEMATICA'
    """
    )
    assert len(result) == 1
    assert result[0] == (5, "SIG.MATEMATICA")


# 06/24 /iam/add_permission_to_role/


def test_add_permission_to_role_missing_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "input": {"permission_name": "EDIT.EVENT"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'EDIT.EVENT'
    """
    )
    # Initial state should be maintained
    assert len(result) == 0


def test_add_permission_to_role_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with missing permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "input": {"role_name": "TESOUREIRO"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with invalid role_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": 123, "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with invalid permission_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": 123}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_empty_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with empty role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_numeric_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with numeric role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "123", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with empty permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": ""}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with numeric permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": "123"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_permission_already_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role that already has the permission."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'CREATE.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("DIRETOR.REGIONAL", "CREATE.EVENT")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "DIRETOR.REGIONAL", "permission_name": "CREATE.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Role: DIRETOR.REGIONAL already has permission: CREATE.EVENT."
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'CREATE.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("DIRETOR.REGIONAL", "CREATE.EVENT")


def test_add_permission_to_role_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "NON.EXISTENT.ROLE", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'NON.EXISTENT.ROLE'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with a permission that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": "NON.EXISTENT.PERMISSION"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Permission: NON.EXISTENT.PERMISSION does not exist."
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO'
    """
    )
    assert len(result) == 0


def test_add_permission_to_role_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a role with valid data."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"role_name": "TESOUREIRO", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_role/", json=data, headers=headers
    )
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Permission: EDIT.EVENT added to role: TESOUREIRO successfully."
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'TESOUREIRO' AND p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("TESOUREIRO", "EDIT.EVENT")


# 07/24 /iam/add_permission_to_group/


def test_add_permission_to_group_missing_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with missing group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "input": {"permission_name": "WHATSAPP.BOT"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with missing permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "input": {"group_name": "BETA.TESTER"},
            }
        ]
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with invalid group_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": 123, "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with invalid permission_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": 123}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_empty_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with empty group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_numeric_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with numeric group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "123", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with empty permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": ""}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with numeric permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": "123"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
    """
    )
    # Initial state should be just one record
    assert len(result) == 1


def test_add_permission_to_group_permission_already_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group that already has the permission."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'WHATSAPP.BOT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "WHATSAPP.BOT")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Group: BETA.TESTER already has permission: WHATSAPP.BOT."
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'WHATSAPP.BOT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "WHATSAPP.BOT")


def test_add_permission_to_group_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "NON.EXISTENT.GROUP", "permission_name": "WHATSAPP.BOT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'NON.EXISTENT.GROUP'
    """
    )
    assert len(result) == 0


def test_add_permission_to_group_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with a permission that does not exist."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": "NON.EXISTENT.PERMISSION"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Permission: NON.EXISTENT.PERMISSION does not exist."
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'NON.EXISTENT.PERMISSION'
    """
    )
    assert len(result) == 0


def test_add_permission_to_group_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test adding a permission to a group with valid data."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    data = {"group_name": "BETA.TESTER", "permission_name": "EDIT.EVENT"}
    response = test_client.post(
        "/iam/add_permission_to_group/", json=data, headers=headers
    )
    assert response.status_code == 201
    assert response.json() == {
        "detail": "Permission: EDIT.EVENT added to group: BETA.TESTER successfully."
    }

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'EDIT.EVENT'
    """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "EDIT.EVENT")


## GET ENDPOINTS ##

# 08/24 /iam/roles/


def test_get_roles_check_response_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting roles for a member."""

    result = run_db_query(
        """
        SELECT r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE urm.registration_id = 5
        ORDER BY r.role_name
        """
    )
    assert len(result) == 2
    assert [r[0] for r in result] == ["DIRETOR.MARKETING", "DIRETOR.REGIONAL"]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/roles/", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["DIRETOR.REGIONAL", "DIRETOR.MARKETING"]


def test_get_roles_no_roles_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting roles for a member with no roles."""

    result = run_db_query(
        """
        SELECT r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE urm.registration_id = 5
        """
    )
    assert len(result) > 0

    run_db_query("DELETE FROM iam_user_roles_map WHERE registration_id = 5;")

    result = run_db_query(
        """
        SELECT r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE urm.registration_id = 5
        """
    )
    assert len(result) == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/roles/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


# 09/24 /iam/groups/


def test_get_groups_check_response_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting groups for a member."""

    result = run_db_query(
        """
        SELECT g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE ugm.registration_id = 5
        ORDER BY g.group_name
        """
    )
    assert len(result) == 1
    assert result[0][0] == "BETA.TESTER"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/groups/", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["BETA.TESTER"]


def test_get_groups_no_groups_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting groups for a member with no groups."""

    result = run_db_query(
        """
        SELECT g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE ugm.registration_id = 5
        """
    )
    assert len(result) > 0

    run_db_query("DELETE FROM iam_user_groups_map WHERE registration_id = 5;")

    result = run_db_query(
        """
        SELECT g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE ugm.registration_id = 5
        """
    )
    assert len(result) == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/groups/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


# 10/24 /iam/permissions/

def test_get_permissions_check_response_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions by member_id."""

    result = run_db_query(
        """
        SELECT p.permission_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        JOIN iam_role_permissions_map rpm ON rpm.role_id = r.id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE urm.registration_id = 5
        ORDER BY p.permission_name
        """
    )

    assert len(result) == 2
    assert [r[0] for r in result] == ["CREATE.EVENT", "DELETE.EVENT"]

    result = run_db_query(
        """
        SELECT p.permission_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        JOIN iam_group_permissions_map gpm ON gpm.group_id = g.id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE ugm.registration_id = 5
        ORDER BY p.permission_name
        """
    )

    assert len(result) == 1
    assert result[0][0] == "WHATSAPP.BOT"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/permissions/", headers=headers)
    assert response.status_code == 200
    assert response.json() == ["CREATE.EVENT", "DELETE.EVENT", "WHATSAPP.BOT"]


def test_get_permissions_no_permissions_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions by member_id with no permissions."""

    run_db_query("DELETE FROM iam_user_roles_map WHERE registration_id = 5;")
    run_db_query("DELETE FROM iam_user_groups_map WHERE registration_id = 5;")

    result = run_db_query(
        """
        SELECT p.permission_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        JOIN iam_role_permissions_map rpm ON rpm.role_id = r.id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE urm.registration_id = 5
        """
    )
    assert len(result) == 0

    result = run_db_query(
        """
        SELECT p.permission_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        JOIN iam_group_permissions_map gpm ON gpm.group_id = g.id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE ugm.registration_id = 5
        """
    )
    assert len(result) == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get("/iam/permissions/", headers=headers)
    assert response.status_code == 200
    assert response.json() == []

# 11/24 /iam/members/role/


def test_get_members_by_role_name_should_return_member_list(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting members by role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/role/", params={"role_name": "DIRETOR.REGIONAL"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == [["Fernando Diniz Souza Filho", 5]]


def test_get_members_by_role_name_should_return_no_members_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting members by role_name with no members found."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'TESOUREIRO'
        """
    )
    assert result[0][0] == 1

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE r.role_name = 'TESOUREIRO'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/role/", params={"role_name": "TESOUREIRO"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_members_by_role_name_role_dont_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting members by role_name that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/role/", params={"role_name": "NON.EXISTENT.ROLE"}, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}


# 12/24 /iam/members/group/


def test_get_members_by_group_name_should_return_member_list(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test getting members by group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/group/", params={"group_name": "BETA.TESTER"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == [["Fernando Diniz Souza Filho", 5]]


def test_get_members_by_group_name_should_return_no_members_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting members by group_name with no members found."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 1

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE g.group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/group/", params={"group_name": "SIG.MATEMATICA"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_members_by_group_name_group_dont_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting members by group_name that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/members/group/",
        params={"group_name": "NON.EXISTENT.GROUP"},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}


# 13/24 /iam/role_permissions/


def test_get_role_permissions_by_role_name_should_return_permission_list(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a role."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        ORDER BY p.permission_name
        """
    )
    assert len(result) == 1
    assert result[0][1] == "CREATE.EVENT"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/role_permissions/",
        params={"role_name": "DIRETOR.REGIONAL"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == ["CREATE.EVENT"]


def test_get_role_permissions_by_role_name_no_permissions_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a role with no permissions."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'SECRETARIO'
        """
    )
    assert result[0][0] == 1

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        WHERE r.role_name = 'SECRETARIO'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/role_permissions/", params={"role_name": "SECRETARIO"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_role_permissions_by_role_name_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a role that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/role_permissions/",
        params={"role_name": "NON.EXISTENT.ROLE"},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}


# 14/24 /iam/group_permissions/


def test_get_group_permissions_by_group_name_should_return_permission_list(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a group."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        ORDER BY p.permission_name
        """
    )
    assert len(result) == 1
    assert result[0][1] == "WHATSAPP.BOT"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/group_permissions/", params={"group_name": "BETA.TESTER"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == ["WHATSAPP.BOT"]


def test_get_group_permissions_by_group_name_no_permissions_found(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a group with no permissions."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 1

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        WHERE g.group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/group_permissions/",
        params={"group_name": "SIG.MATEMATICA"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_group_permissions_by_group_name_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test getting permissions for a group that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*) 
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.get(
        "/iam/group_permissions/",
        params={"group_name": "NON.EXISTENT.GROUP"},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}


## UPDATE ENDPOINTS ##

# 15/24 /iam/update_role/


def test_update_role_missing_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "input": {
                    "new_role_name": "UPDATED.ROLE",
                    "new_role_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles 
        WHERE role_name = 'UPDATED.ROLE'
        """
    )
    assert len(result) == 0


def test_update_role_missing_new_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with missing new_role_name."""

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    original_role = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "new_role_name"],
                "msg": "Field required",
                "input": {
                    "role_name": "DIRETOR.REGIONAL",
                    "new_role_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles 
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == original_role


def test_update_role_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with invalid role_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": 123,
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT role_name, role_description 
        FROM iam_roles
        WHERE role_name = 'UPDATED.ROLE'
        """
    )
    assert len(result) == 0


def test_update_role_invalid_new_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with invalid new_role_name type."""

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles 
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    original_role = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "new_role_name": 123,
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "new_role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles 
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == original_role


def test_update_role_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "NON.EXISTENT.ROLE",
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name IN ('NON.EXISTENT.ROLE', 'UPDATED.ROLE')
        """
    )
    assert result[0][0] == 0


def test_update_role_valid_data_inserted(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a role with valid data."""

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'DIRETOR.REGIONAL' 
        """
    )
    assert len(result) == 1

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "new_role_name": "UPDATED.ROLE",
        "new_role_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_role/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Role: DIRETOR.REGIONAL updated successfully."}

    result = run_db_query(
        """
        SELECT role_name, role_description  
        FROM iam_roles
        WHERE role_name = 'UPDATED.ROLE'
        """
    )
    assert len(result) == 1
    assert result[0] == ("UPDATED.ROLE", "Updated Description")

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles 
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0][0] == 0


# 16/24 /iam/update_group/


def test_update_group_missing_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with missing group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "new_group_name": "UPDATED.GROUP",
        "new_group_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "input": {
                    "new_group_name": "UPDATED.GROUP",
                    "new_group_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups 
        WHERE group_name = 'UPDATED.GROUP'
        """
    )
    assert len(result) == 0


def test_update_group_missing_new_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with missing new_group_name."""

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    original_group = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "new_group_description": "Updated Description"}
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "new_group_name"],
                "msg": "Field required",
                "input": {
                    "group_name": "BETA.TESTER",
                    "new_group_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups 
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == original_group


def test_update_group_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with invalid group_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "group_name": 123,
        "new_group_name": "UPDATED.GROUP",
        "new_group_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'UPDATED.GROUP'
        """
    )
    assert len(result) == 0


def test_update_group_invalid_new_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with invalid new_group_name type."""

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    original_group = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "group_name": "BETA.TESTER",
        "new_group_name": 123,
        "new_group_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "new_group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == original_group


def test_update_group_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups 
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "group_name": "NON.EXISTENT.GROUP",
        "new_group_name": "UPDATED.GROUP",
        "new_group_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name IN ('NON.EXISTENT.GROUP', 'UPDATED.GROUP')
        """
    )
    assert result[0][0] == 0


def test_update_group_valid_data_inserted(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a group with valid data."""

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert len(result) == 1

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "group_name": "BETA.TESTER",
        "new_group_name": "UPDATED.GROUP",
        "new_group_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_group/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"detail": "Group: BETA.TESTER updated successfully."}

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'UPDATED.GROUP'
        """
    )
    assert len(result) == 1
    assert result[0] == ("UPDATED.GROUP", "Updated Description")

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert result[0][0] == 0


# 17/24 /iam/update_permission/


def test_update_permission_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with missing permission_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "input": {
                    "new_permission_name": "UPDATED.PERMISSION",
                    "new_permission_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'UPDATED.PERMISSION'
        """
    )
    assert len(result) == 0


def test_update_permission_missing_new_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with missing new_permission_name."""

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    original_permission = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": "WHATSAPP.BOT",
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "new_permission_name"],
                "msg": "Field required",
                "input": {
                    "permission_name": "WHATSAPP.BOT",
                    "new_permission_description": "Updated Description",
                },
            }
        ]
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0] == original_permission


def test_update_permission_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with invalid permission_name type."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": 123,
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'UPDATED.PERMISSION'
        """
    )
    assert len(result) == 0


def test_update_permission_invalid_new_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with invalid new_permission_name type."""

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    original_permission = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": "WHATSAPP.BOT",
        "new_permission_name": 123,
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "new_permission_name" must be a string.'
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0] == original_permission


def test_update_permission_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": "NON.EXISTENT",
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Permission: NON.EXISTENT does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name IN ('NON.EXISTENT', 'UPDATED.PERMISSION')
        """
    )
    assert result[0][0] == 0


def test_update_permission_valid_data_inserted(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test updating a permission with valid data."""

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert len(result) == 1

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "permission_name": "WHATSAPP.BOT",
        "new_permission_name": "UPDATED.PERMISSION",
        "new_permission_description": "Updated Description",
    }
    response = test_client.patch("/iam/update_permission/", json=json, headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT updated successfully."
    }

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'UPDATED.PERMISSION'
        """
    )
    assert len(result) == 1
    assert result[0] == ("UPDATED.PERMISSION", "Updated Description")

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0][0] == 0


## DELETE ENDPOINTS ##

# 18/24 /iam/remove_role_from_member/


def test_remove_role_from_member_missing_role_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a role from a member with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"member_id": 5},
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


def test_remove_role_from_member_missing_member_id(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a role from a member with missing member_id."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL"}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"role_name": "DIRETOR.REGIONAL"},
                "loc": ["body", "member_id"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


def test_remove_role_from_member_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with invalid role_name type."""

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": 123, "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT registration_id, r.role_name  
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == initial_state


def test_remove_role_from_member_invalid_member_id_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with invalid member_id type."""

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "member_id": "five"}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "member_id" must be an integer.'}

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == initial_state


def test_remove_role_from_member_empty_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with empty role_name."""

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "", "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == initial_state


def test_remove_role_from_member_numeric_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with numeric role_name."""

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "123", "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0] == initial_state


def test_remove_role_from_member_member_id_zero(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a role from a member with member_id zero."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "member_id": 0}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "member_id" must be positive. (greater than 0)'
    }


def test_remove_role_from_member_role_not_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member that is not assigned."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'TESOUREIRO'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "TESOUREIRO", "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Role: TESOUREIRO not assigned to member with id: 5."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'TESOUREIRO'
        """
    )
    assert result[0][0] == 0


def test_remove_role_from_member_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with a role that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "NON.EXISTENT.ROLE", "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0


def test_remove_role_from_member_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a role from a member with valid data."""

    result = run_db_query(
        """
        SELECT registration_id, r.role_name
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert len(result) == 1
    assert result[0] == (5, "DIRETOR.REGIONAL")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "member_id": 5}
    response = test_client.request(
        method="delete", url="/iam/remove_role_from_member/", json=json, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Role: DIRETOR.REGIONAL removed from member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_roles_map urm
        JOIN iam_roles r ON r.id = urm.role_id
        WHERE registration_id = 5 AND r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0][0] == 0


# 19/24 /iam/remove_group_from_member/


def test_remove_group_from_member_missing_group_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a group from a member with missing group_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"member_id": 5},
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


def test_remove_group_from_member_missing_member_id(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a group from a member with missing member_id."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"group_name": "BETA.TESTER"},
                "loc": ["body", "member_id"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


def test_remove_group_from_member_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with invalid group_name type."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": 123, "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == initial_state


def test_remove_group_from_member_invalid_member_id_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with invalid member_id type."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "member_id": "five"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "member_id" must be an integer.'}

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == initial_state


def test_remove_group_from_member_empty_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with empty group_name."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "", "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == initial_state


def test_remove_group_from_member_numeric_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with numeric group_name."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "123", "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == initial_state


def test_remove_group_from_member_member_id_zero(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with member_id zero."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = result[0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "member_id": 0}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        "detail": 'Field: "member_id" must be positive. (greater than 0)'
    }

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0] == initial_state


def test_remove_group_from_member_group_not_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member that is not assigned."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "SIG.MATEMATICA", "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Group: SIG.MATEMATICA not assigned to member with id: 5."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'SIG.MATEMATICA'
        """
    )
    assert result[0][0] == 0


def test_remove_group_from_member_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with a group that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "NON.EXISTENT.GROUP", "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0


def test_remove_group_from_member_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a group from a member with valid data."""

    result = run_db_query(
        """
        SELECT registration_id, g.group_name
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert len(result) == 1
    assert result[0] == (5, "BETA.TESTER")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "member_id": 5}
    response = test_client.request(
        method="delete",
        url="/iam/remove_group_from_member/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Group: BETA.TESTER removed from member with id: 5 successfully."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_user_groups_map ugm
        JOIN iam_groups g ON g.id = ugm.group_id
        WHERE registration_id = 5 AND g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0][0] == 0


# 20/24 /iam/remove_permission_from_role/


def test_remove_permission_from_role_missing_role_name(
    test_client: Any, mock_valid_token: Any
) -> None:
    """Test removing a permission from a role with missing role_name."""

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"permission_name": "CREATE.EVENT"},
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }


def test_remove_permission_from_role_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with missing permission_name."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"role_name": "DIRETOR.REGIONAL"},
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with invalid role_name type."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": 123, "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with invalid permission_name type."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "permission_name": 123}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name 
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_empty_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with empty role_name."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id 
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "", "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_numeric_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with numeric role_name."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "123", "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE p.permission_name = 'CREATE.EVENT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with empty permission_name."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "permission_name": ""}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with numeric permission_name."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "permission_name": "123"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_role_permission_not_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role that is not assigned."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'EDIT.EVENT'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "permission_name": "EDIT.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Role: DIRETOR.REGIONAL does not have permission: EDIT.EVENT."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'EDIT.EVENT'
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_role_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "NON.EXISTENT.ROLE", "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_role_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with a permission that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {
        "role_name": "DIRETOR.REGIONAL",
        "permission_name": "NON.EXISTENT",
    }
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Permission: NON.EXISTENT does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT'
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_role_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a role with valid data."""

    result = run_db_query(
        """
        SELECT r.role_name, p.permission_name
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'CREATE.EVENT'
        """
    )
    assert len(result) == 1
    assert result[0] == ("DIRETOR.REGIONAL", "CREATE.EVENT")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL", "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_role/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: CREATE.EVENT removed from role: DIRETOR.REGIONAL successfully."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_role_permissions_map rpm
        JOIN iam_roles r ON r.id = rpm.role_id
        JOIN iam_permissions p ON p.id = rpm.permission_id
        WHERE r.role_name = 'DIRETOR.REGIONAL' AND p.permission_name = 'CREATE.EVENT'
        """
    )
    assert result[0][0] == 0


# 21/24 /iam/remove_permission_from_group/


def test_remove_permission_from_group_missing_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with missing group_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"permission_name": "WHATSAPP.BOT"},
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0][0] == initial_count


def test_remove_permission_from_group_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with missing permission_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {"group_name": "BETA.TESTER"},
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    assert result[0][0] == initial_count


def test_remove_permission_from_group_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with invalid group_name type."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": 123, "permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with invalid permission_name type."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": 123}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_empty_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with empty group_name."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "", "permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_numeric_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with numeric group_name."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "123", "permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with empty permission_name."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": ""}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with numeric permission_name."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    initial_state = list(result)

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": "123"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER'
        """
    )
    assert list(result) == initial_state


def test_remove_permission_from_group_permission_not_assigned(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group that is not assigned."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'CREATE.EVENT'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": "CREATE.EVENT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Group: BETA.TESTER does not have permission: CREATE.EVENT."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'CREATE.EVENT'
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_group_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "NON.EXISTENT.GROUP", "permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups 
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_group_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with a permission that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT.PERMISSION'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": "NON.EXISTENT.PERMISSION"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Permission: NON.EXISTENT.PERMISSION does not exist."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT.PERMISSION' 
        """
    )
    assert result[0][0] == 0


def test_remove_permission_from_group_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test removing a permission from a group with valid data."""

    result = run_db_query(
        """
        SELECT g.group_name, p.permission_name
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert len(result) == 1
    assert result[0] == ("BETA.TESTER", "WHATSAPP.BOT")

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER", "permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete",
        url="/iam/remove_permission_from_group/",
        json=json,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT removed from group: BETA.TESTER successfully."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_group_permissions_map gpm
        JOIN iam_groups g ON g.id = gpm.group_id
        JOIN iam_permissions p ON p.id = gpm.permission_id
        WHERE g.group_name = 'BETA.TESTER' AND p.permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0][0] == 0


# 22/24 /iam/delete_role/


def test_delete_role_missing_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with missing role_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json={}, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "role_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    assert result[0][0] == initial_count


def test_delete_role_invalid_role_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with invalid role_name type."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": 123}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" must be a string.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    assert result[0][0] == initial_count


def test_delete_role_empty_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with empty role_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": ""}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    assert result[0][0] == initial_count


def test_delete_role_numeric_role_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with numeric role_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "123"}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "role_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        """
    )
    assert result[0][0] == initial_count


def test_delete_role_role_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "NON.EXISTENT.ROLE"}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json=json, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Role: NON.EXISTENT.ROLE does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'NON.EXISTENT.ROLE'
        """
    )
    assert result[0][0] == 0


def test_delete_role_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a role with valid data."""

    result = run_db_query(
        """
        SELECT role_name, role_description
        FROM iam_roles
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert len(result) == 1
    assert result[0][0] == "DIRETOR.REGIONAL"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"role_name": "DIRETOR.REGIONAL"}
    response = test_client.request(
        method="delete", url="/iam/delete_role/", json=json, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Role: DIRETOR.REGIONAL deleted successfully."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_roles
        WHERE role_name = 'DIRETOR.REGIONAL'
        """
    )
    assert result[0][0] == 0


# 23/24 /iam/delete_group/


def test_delete_group_missing_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with missing group_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json={}, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "group_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    assert result[0][0] == initial_count


def test_delete_group_invalid_group_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with invalid group_name type."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": 123}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" must be a string.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    assert result[0][0] == initial_count


def test_delete_group_empty_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with empty group_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": ""}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    assert result[0][0] == initial_count


def test_delete_group_numeric_group_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with numeric group_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "123"}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "group_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        """
    )
    assert result[0][0] == initial_count


def test_delete_group_group_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*) 
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "NON.EXISTENT.GROUP"}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json=json, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Group: NON.EXISTENT.GROUP does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'NON.EXISTENT.GROUP'
        """
    )
    assert result[0][0] == 0


def test_delete_group_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a group with valid data."""

    result = run_db_query(
        """
        SELECT group_name, group_description
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert len(result) == 1
    assert result[0][0] == "BETA.TESTER"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"group_name": "BETA.TESTER"}
    response = test_client.request(
        method="delete", url="/iam/delete_group/", json=json, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Group: BETA.TESTER deleted successfully."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_groups
        WHERE group_name = 'BETA.TESTER'
        """
    )
    assert result[0][0] == 0


# 24/24 /iam/delete_permission/


def test_delete_permission_missing_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with missing permission_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json={}, headers=headers
    )
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": {},
                "loc": ["body", "permission_name"],
                "msg": "Field required",
                "type": "missing",
            }
        ]
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    assert result[0][0] == initial_count


def test_delete_permission_invalid_permission_name_type(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with invalid permission_name type."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": 123}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" must be a string.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    assert result[0][0] == initial_count


def test_delete_permission_empty_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with empty permission_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": ""}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be empty.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    assert result[0][0] == initial_count


def test_delete_permission_numeric_permission_name(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with numeric permission_name."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    initial_count = result[0][0]

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": "123"}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json=json, headers=headers
    )
    assert response.status_code == 400
    assert response.json() == {"detail": 'Field: "permission_name" cannot be numeric.'}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        """
    )
    assert result[0][0] == initial_count


def test_delete_permission_permission_does_not_exist(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission that does not exist."""

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT'
        """
    )
    assert result[0][0] == 0

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": "NON.EXISTENT"}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json=json, headers=headers
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Permission: NON.EXISTENT does not exist."}

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'NON.EXISTENT'
        """
    )
    assert result[0][0] == 0


def test_delete_permission_valid_data(
    test_client: Any, mock_valid_token: Any, run_db_query: Any
) -> None:
    """Test deleting a permission with valid data."""

    result = run_db_query(
        """
        SELECT permission_name, permission_description
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert len(result) == 1
    assert result[0][0] == "WHATSAPP.BOT"

    headers = {"Authorization": f"Bearer {mock_valid_token}"}
    json = {"permission_name": "WHATSAPP.BOT"}
    response = test_client.request(
        method="delete", url="/iam/delete_permission/", json=json, headers=headers
    )
    assert response.status_code == 200
    assert response.json() == {
        "detail": "Permission: WHATSAPP.BOT deleted successfully."
    }

    result = run_db_query(
        """
        SELECT COUNT(*)
        FROM iam_permissions
        WHERE permission_name = 'WHATSAPP.BOT'
        """
    )
    assert result[0][0] == 0
