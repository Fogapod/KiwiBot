-- TABLES --
CREATE OR REPLACE TABLE color_roles (
	guild_id BIGINT NOT NULL,
	role_id BIGINT NOT NULL
);


-- INDEXES --
CREATE OR REPLACE INDEX idx_color_roles_guild_id ON color_roles(guild_id);
