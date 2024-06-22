CREATE TABLE IF NOT EXISTS django_migrations (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    group_id INT NOT NULL REFERENCES auth_group(id),
    permission_id INT NOT NULL REFERENCES auth_permission(id)
);

CREATE TABLE IF NOT EXISTS auth_user_groups (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL REFERENCES auth_user(id),
    group_id INT NOT NULL REFERENCES auth_group(id)
);

CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL REFERENCES auth_user(id),
    permission_id INT NOT NULL REFERENCES auth_permission(id)
);

CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id_uniq ON auth_group_permissions (group_id, permission_id);
CREATE INDEX auth_group_permissions_group_id_idx ON auth_group_permissions (group_id);
CREATE INDEX auth_group_permissions_permission_id_idx ON auth_group_permissions (permission_id);

CREATE UNIQUE INDEX auth_user_groups_user_id_group_id_uniq ON auth_user_groups (user_id, group_id);
CREATE INDEX auth_user_groups_user_id_idx ON auth_user_groups (user_id);
CREATE INDEX auth_user_groups_group_id_idx ON auth_user_groups (group_id);

CREATE UNIQUE INDEX auth_user_user_permissions_user_id_permission_id_uniq ON auth_user_user_permissions (user_id, permission_id);
CREATE INDEX auth_user_user_permissions_user_id_idx ON auth_user_user_permissions (user_id);
CREATE INDEX auth_user_user_permissions_permission_id_idx ON auth_user_user_permissions (permission_id);

CREATE TABLE IF NOT EXISTS django_admin_log (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT UNSIGNED NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id INT NULL REFERENCES django_content_type(id),
    user_id INT NOT NULL REFERENCES auth_user(id),
    action_time DATETIME NOT NULL
);

CREATE INDEX django_admin_log_content_type_id_idx ON django_admin_log (content_type_id);
CREATE INDEX django_admin_log_user_id_idx ON django_admin_log (user_id);

CREATE TABLE IF NOT EXISTS django_content_type (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

CREATE UNIQUE INDEX django_content_type_app_label_model_uniq ON django_content_type (app_label, model);

CREATE TABLE IF NOT EXISTS auth_permission (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    content_type_id INT NOT NULL REFERENCES django_content_type(id),
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX auth_permission_content_type_id_codename_uniq ON auth_permission (content_type_id, codename);
CREATE INDEX auth_permission_content_type_id_idx ON auth_permission (content_type_id);

CREATE TABLE IF NOT EXISTS auth_group (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS auth_user (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL,
    first_name VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date DATETIME NOT NULL
);

CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);

CREATE TABLE IF NOT EXISTS Clients_server (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    servers TEXT NOT NULL,
    user_id INT NOT NULL UNIQUE REFERENCES auth_user(id)
);

CREATE TABLE IF NOT EXISTS oauth2_provider_refreshtoken (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) NOT NULL,
    access_token_id BIGINT NULL UNIQUE REFERENCES oauth2_provider_accesstoken(id),
    application_id BIGINT NOT NULL REFERENCES oauth2_provider_application(id),
    user_id INT NOT NULL REFERENCES auth_user(id),
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    revoked DATETIME NULL
);

CREATE UNIQUE INDEX oauth2_provider_refreshtoken_token_revoked_uniq ON oauth2_provider_refreshtoken (token, revoked);
CREATE INDEX oauth2_provider_refreshtoken_application_id_idx ON oauth2_provider_refreshtoken (application_id);
CREATE INDEX oauth2_provider_refreshtoken_user_id_idx ON oauth2_provider_refreshtoken (user_id);

CREATE TABLE IF NOT EXISTS oauth2_provider_idtoken (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    jti CHAR(32) NOT NULL UNIQUE,
    expires DATETIME NOT NULL,
    scope TEXT NOT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    application_id BIGINT NULL REFERENCES oauth2_provider_application(id),
    user_id INT NULL REFERENCES auth_user(id)
);

CREATE TABLE IF NOT EXISTS oauth2_provider_accesstoken (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires DATETIME NOT NULL,
    scope TEXT NOT NULL,
    application_id BIGINT NULL REFERENCES oauth2_provider_application(id),
    user_id INT NULL REFERENCES auth_user(id),
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    source_refresh_token_id BIGINT NULL UNIQUE REFERENCES oauth2_provider_refreshtoken(id),
    id_token_id BIGINT NULL UNIQUE REFERENCES oauth2_provider_idtoken(id)
);

CREATE INDEX oauth2_provider_idtoken_application_id_idx ON oauth2_provider_idtoken (application_id);
CREATE INDEX oauth2_provider_idtoken_user_id_idx ON oauth2_provider_idtoken (user_id);
CREATE INDEX oauth2_provider_accesstoken_application_id_idx ON oauth2_provider_accesstoken (application_id);
CREATE INDEX oauth2_provider_accesstoken_user_id_idx ON oauth2_provider_accesstoken (user_id);

CREATE TABLE IF NOT EXISTS oauth2_provider_grant (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(255) NOT NULL UNIQUE,
    expires DATETIME NOT NULL,
    redirect_uri TEXT NOT NULL,
    scope TEXT NOT NULL,
    application_id BIGINT NOT NULL REFERENCES oauth2_provider_application(id),
    user_id INT NOT NULL REFERENCES auth_user(id),
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    code_challenge VARCHAR(128) NOT NULL,
    code_challenge_method VARCHAR(10) NOT NULL,
    nonce VARCHAR(255) NOT NULL,
    claims TEXT NOT NULL
);

CREATE INDEX oauth2_provider_grant_application_id_idx ON oauth2_provider_grant (application_id);
CREATE INDEX oauth2_provider_grant_user_id_idx ON oauth2_provider_grant (user_id);

CREATE TABLE IF NOT EXISTS oauth2_provider_application (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    client_id VARCHAR(100) NOT NULL UNIQUE,
    redirect_uris TEXT NOT NULL,
    client_type VARCHAR(32) NOT NULL,
    authorization_grant_type VARCHAR(32) NOT NULL,
    client_secret VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    user_id INT NULL REFERENCES auth_user(id),
    skip_authorization BOOLEAN NOT NULL,
    created DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    algorithm VARCHAR(5) NOT NULL,
    post_logout_redirect_uris TEXT NOT NULL
);

CREATE INDEX oauth2_provider_application_client_secret_idx ON oauth2_provider_application (client_secret);
CREATE INDEX oauth2_provider_application_user_id_idx ON oauth2_provider_application (user_id);

CREATE TABLE IF NOT EXISTS oidc_provider_rsakey (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oidc_provider_code (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    expires_at DATETIME NOT NULL,
    _scope TEXT NOT NULL,
    code VARCHAR(255) NOT NULL UNIQUE,
    client_id INT NOT NULL REFERENCES oidc_provider_client(id),
    user_id INT NOT NULL REFERENCES auth_user(id),
    is_authentication BOOLEAN NOT NULL,
    code_challenge VARCHAR(255) NULL,
    code_challenge_method VARCHAR(255) NULL,
    nonce VARCHAR(255) NOT NULL
);

CREATE INDEX oidc_provider_code_client_id_idx ON oidc_provider_code (client_id);
CREATE INDEX oidc_provider_code_user_id_idx ON oidc_provider_code (user_id);

CREATE TABLE IF NOT EXISTS oidc_provider_userconsent (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    expires_at DATETIME NOT NULL,
    client_id INT NOT NULL REFERENCES oidc_provider_client(id),
    user_id INT NOT NULL REFERENCES auth_user(id),
    date_given DATETIME NOT NULL,
    _scope TEXT NOT NULL
);

CREATE UNIQUE INDEX oidc_provider_userconsent_user_id_client_id_uniq ON oidc_provider_userconsent (user_id, client_id);
CREATE INDEX oidc_provider_userconsent_client_id_idx ON oidc_provider_userconsent (client_id);
CREATE INDEX oidc_provider_userconsent_user_id_idx ON oidc_provider_userconsent (user_id);

CREATE TABLE IF NOT EXISTS oidc_provider_client (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    client_id VARCHAR(255) NOT NULL UNIQUE,
    client_secret VARCHAR(255) NOT NULL,
    _redirect_uris TEXT NOT NULL,
    date_created DATE NOT NULL,
    client_type VARCHAR(30) NOT NULL,
    jwt_alg VARCHAR(10) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    logo VARCHAR(100) NOT NULL,
    terms_url VARCHAR(255) NOT NULL,
    website_url VARCHAR(255) NOT NULL,
    _post_logout_redirect_uris TEXT NOT NULL,
    require_consent BOOLEAN NOT NULL,
    reuse_consent BOOLEAN NOT NULL,
    owner_id INT NULL REFERENCES auth_user(id),
    _scope TEXT NOT NULL
);

CREATE INDEX oidc_provider_client_owner_id_idx ON oidc_provider_client (owner_id);

CREATE TABLE IF NOT EXISTS oidc_provider_token (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    expires_at DATETIME NOT NULL,
    _scope TEXT NOT NULL,
    access_token VARCHAR(255) NOT NULL UNIQUE,
    _id_token TEXT NOT NULL,
    client_id INT NOT NULL REFERENCES oidc_provider_client(id),
    refresh_token VARCHAR(255) NOT NULL UNIQUE,
    user_id INT NULL REFERENCES auth_user(id)
);

CREATE INDEX oidc_provider_token_client_id_idx ON oidc_provider_token (client_id);
CREATE INDEX oidc_provider_token_user_id_idx ON oidc_provider_token (user_id);

CREATE TABLE IF NOT EXISTS oidc_provider_responsetype (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    value VARCHAR(30) NOT NULL UNIQUE,
    description VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS oidc_provider_client_response_types (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    client_id INT NOT NULL REFERENCES oidc_provider_client(id),
    responsetype_id INT NOT NULL REFERENCES oidc_provider_responsetype(id)
);

CREATE UNIQUE INDEX oidc_provider_client_response_types_client_id_responsetype_id_uniq ON oidc_provider_client_response_types (client_id, responsetype_id);
CREATE INDEX oidc_provider_client_response_types_client_id_idx ON oidc_provider_client_response_types (client_id);
CREATE INDEX oidc_provider_client_response_types_responsetype_id_idx ON oidc_provider_client_response_types (responsetype_id);

CREATE TABLE IF NOT EXISTS Clients_os (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    value VARCHAR(255) NOT NULL,
    storage_layout TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Clients_maas (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    MAAS_HOST VARCHAR(255) NOT NULL,
    CONSUMER_KEY VARCHAR(255) NOT NULL,
    CONSUMER_TOKEN VARCHAR(255) NOT NULL,
    SECRET VARCHAR(255) NOT NULL,
    Name VARCHAR(255) NOT NULL,
    editable BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS Clients_cloudinit (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    userdata TEXT NOT NULL,
    os VARCHAR(8000) NOT NULL,
    name VARCHAR(255) NOT NULL
);
