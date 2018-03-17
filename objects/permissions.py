from constants import BOT_OWNER_ID


class Permission:

    name = None

    def __init__(self, bot):
        self.bot = bot

    async def check(self, msg, bot=False):
        return await self._check((msg.guild.me if msg.guild else None) if bot else msg.author, msg)
    
    async def _check(self, user, msg):
        return True


class PermissionBotOwner(Permission):

    name = 'BOT_OWNER'

    async def check(self, msg, bot=False):
        if bot:
            raise ValueError(f'Bot can\'t have {self.name} permission')
        return msg.author.id == BOT_OWNER_ID


class PermissionGuildOwner(Permission):

    name = 'GUILD_OWNER'

    async def _check(self, user, msg):
        return msg.channel.guild.owner == user


class PermissionAddReactions(Permission):

    name = 'ADD_REACTIONS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).add_reactions


class PermissionAdmin(Permission):

    name = 'ADMIN'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).administrator


class PermissionAttachFiles(Permission):

    name = 'ATTACH_FILES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).attach_files


class PermissionBanMembers(Permission):

    name = 'BAN_MEMBERS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).ban_members


class PermissionChangeNickname(Permission):

    name = 'CHANGE_NICKNAME'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).change_nickname


class PermissionConnect(Permission):

    name = 'CONNECT'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).connect


class PermissionCreateInstantInvite(Permission):

    name = 'CREATE_INSTANT_INVITE'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).create_instant_invite


class PermissionDeafenMembers(Permission):

    name = 'DEAFENN_MEMBERS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).deafen_members


class PermissionEmbedLinks(Permission):

    name = 'EMBED_LINKS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).embed_links


class PermissionExternalEmojis(Permission):

    name = 'EXTERNAL_EMOJIS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).external_emojis


class PermissionKickMembers(Permission):

    name = 'KICK_MEMBERS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).kick_members


class PermissionManageChannels(Permission):

    name = 'MANAGE_CHANNELS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_channels


class PermissionManageEmojis(Permission):

    name = 'MANAGE_EMOJIS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_emojis


class PermissionManageGuild(Permission):

    name = 'MANAGE_GUILD'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_guild


class PermissionManageMessages(Permission):

    name = 'MANAGE_MESSAGES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_messages


class PermissionNanageNicknames(Permission):

    name = 'MANAGE_NICKNAMES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_nicknames


class PermissionManageRoles(Permission):

    name = 'MANAGE_ROLES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_roles


class PermissionManageWebhooks(Permission):

    name = 'MANAGE_WEBHOOKS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).manage_webhooks


class PermissionMentionEveryone(Permission):

    name = 'MENTION_EVERYONE'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).mention_everyone


class PermissionMoveMembers(Permission):

    name = 'MOVE_MEMBERS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).move_members


class PermissionMuteMembers(Permission):

    name = 'MUTE_MEMBERS'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).mute_members


class PermissionReadMessageHistory(Permission):

    name = 'READ_MESSAGE_HISTORY'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).read_message_history


class PermissionReadMessages(Permission):

    name = 'READ_MESSAGES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).read_messages


class PermissionSendMessages(Permission):

    name = 'SEND_MESSAGES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).send_messages


class PermissionSendTtsMessages(Permission):

    name = 'SEND_TTS_MESSAGES'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).send_tts_messages


class PermissionSpeak(Permission):

    name = 'SPEAK'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).speak


class PermissionUseVoiceActivation(Permission):

    name = 'USE_VOICE_ACTIVATION'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).use_voice_activation


class PermissionViewAuditLog(Permission):

    name = 'VIEW_AUDIT_LOG'

    async def _check(self, user, msg):
        return msg.channel.permissions_for(user).view_audit_log