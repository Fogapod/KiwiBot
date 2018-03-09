from utils.constants import BOT_OWNER_ID


class Permission:

    name = None

    def __init__(self, bot):
        self.bot = bot

    async def check(self, msg, bot=False):
        return await self._check(msg.guild.me if bot else msg.author, msg)
    
    async def _check(self, user, msg):
        return True


class PermissionBotOwner(Permission):

    name = 'BOT_OWNER'

    async def check(self, msg, bot=False):
        if bot:
            raise ValueError(f'Bot can\'t have {self.name} permission')
        return msg.author.id == BOT_OWNER_ID


class PermissionAddReactions(Permission):

    name = 'ADD_REACTIONS'

    async def _check(self, user, msg):
        return user.guild_permissions.add_reactions


class PermissionAdmin(Permission):

    name = 'ADMIN'

    async def _check(self, user, msg):
        return user.guild_permissions.administrator


class PermissionAttachFiles(Permission):

    name = 'ATTACH_FILES'

    async def _check(self, user, msg):
        return user.guild_permissions.attach_files


class PermissionBanMembers(Permission):

    name = 'BAN_MEMBERS'

    async def _check(self, user, msg):
        return user.guild_permissions.ban_members


class PermissionChangeNickname(Permission):

    name = 'CHANGE_NICKNAME'

    async def _check(self, user, msg):
        return user.guild_permissions.change_nickname


class PermissionConnect(Permission):

    name = 'CONNECT'

    async def _check(self, user, msg):
        return user.guild_permissions.connect


class PermissionCreateInstantInvite(Permission):

    name = 'CREATE_INSTANT_INVITE'

    async def _check(self, user, msg):
        return user.guild_permissions.create_instant_invite


class PermissionDeafenMembers(Permission):

    name = 'DEAFENN_MEMBERS'

    async def _check(self, user, msg):
        return user.guild_permissions.deafen_members


class PermissionEmbedLinks(Permission):

    name = 'EMBED_LINKS'

    async def _check(self, user, msg):
        return user.guild_permissions.embed_links


class PermissionExternalEmojis(Permission):

    name = 'EXTERNAL_EMOJIS'

    async def _check(self, user, msg):
        return user.guild_permissions.external_emojis


class PermissionKickMembers(Permission):

    name = 'KICK_MEMBERS'

    async def _check(self, user, msg):
        return user.guild_permissions.kick_members


class PermissionManageChannels(Permission):

    name = 'MANAGE_CHANNELS'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_channels


class PermissionManageEmojis(Permission):

    name = 'MANAGE_EMOJIS'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_emojis


class PermissionManageGuild(Permission):

    name = 'MANAGE_GUILD'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_guild


class PermissionManageMessages(Permission):

    name = 'MANAGE_MESSAGES'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_messages


class PermissionNanageNicknames(Permission):

    name = 'MANAGE_NICKNAMES'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_nicknames


class PermissionManageRoles(Permission):

    name = 'MANAGE_ROLES'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_roles


class PermissionManageWebhooks(Permission):

    name = 'MANAGE_WEBHOOKS'

    async def _check(self, user, msg):
        return user.guild_permissions.manage_webhooks


class PermissionMentionEveryone(Permission):

    name = 'MENTION_EVERYONE'

    async def _check(self, user, msg):
        return user.guild_permissions.mention_everyone


class PermissionMoveMembers(Permission):

    name = 'MOVE_MEMBERS'

    async def _check(self, user, msg):
        return user.guild_permissions.move_members


class PermissionMuteMembers(Permission):

    name = 'MUTE_MEMBERS'

    async def _check(self, user, msg):
        return user.guild_permissions.mute_members


class PermissionReadMessageHistory(Permission):

    name = 'READ_MESSAGE_HISTORY'

    async def _check(self, user, msg):
        return user.guild_permissions.read_message_history


class PermissionReadMessages(Permission):

    name = 'READ_MESSAGES'

    async def _check(self, user, msg):
        return user.guild_permissions.read_messages


class PermissionSendMessages(Permission):

    name = 'SEND_MESSAGES'

    async def _check(self, user, msg):
        return user.guild_permissions.send_messages


class PermissionSendTtsMessages(Permission):

    name = 'SEND_TTS_MESSAGES'

    async def _check(self, user, msg):
        return user.guild_permissions.send_tts_messages


class PermissionSpeak(Permission):

    name = 'SPEAK'

    async def _check(self, user, msg):
        return user.guild_permissions.speak


class PermissionUseVoiceActivation(Permission):

    name = 'USE_VOICE_ACTIVATION'

    async def _check(self, user, msg):
        return user.guild_permissions.use_voice_activation


class PermissionViewAuditLog(Permission):

    name = 'VIEW_AUDIT_LOG'

    async def _check(self, user, msg):
        return user.guild_permissions.view_audit_log