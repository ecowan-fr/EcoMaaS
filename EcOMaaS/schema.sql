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
