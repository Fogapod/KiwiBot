from discord import ClientUser

from constants import BOT_OWNER_ID


class Permission(Exception):

    name = ''
    is_bot_missing = True

    def check(self, channel, user):
        if isinstance(user, ClientUser) and channel.guild is not None:
            user = channel.guild.me

        self.is_bot_missing = user.id == getattr(channel, 'guild', channel).me.id

        return getattr(channel.permissions_for(user), self.name.lower(), False)


class PermissionBotOwner(Permission):

    name = 'BOT_OWNER'
    is_bot_missing = False

    def check(self, channel, user):
        return user.id == BOT_OWNER_ID


class PermissionGuildOwner(Permission):

    def check(channel, user):
        self.is_bot_missing = user.id == (channel.guild if channel.guild is not None else channel).me.id

        return channel.guild is not None and channel.guild.owner == user


class PermissionAddReactions(Permission):

    name = 'ADD_REACTIONS'


class PermissionAdmin(Permission):

    name = 'ADMINISTRATOR'


class PermissionAttachFiles(Permission):

    name = 'ATTACH_FILES'


class PermissionBanMembers(Permission):

    name = 'BAN_MEMBERS'


class PermissionChangeNickname(Permission):

    name = 'CHANGE_NICKNAME'


class PermissionConnect(Permission):

    name = 'CONNECT'


class PermissionCreateInstantInvite(Permission):

    name = 'CREATE_INSTANT_INVITE'


class PermissionDeafenMembers(Permission):

    name = 'DEAFENN_MEMBERS'


class PermissionEmbedLinks(Permission):

    name = 'EMBED_LINKS'


class PermissionExternalEmojis(Permission):

    name = 'EXTERNAL_EMOJIS'


class PermissionKickMembers(Permission):

    name = 'KICK_MEMBERS'


class PermissionManageChannels(Permission):

    name = 'MANAGE_CHANNELS'


class PermissionManageEmojis(Permission):

    name = 'MANAGE_EMOJIS'


class PermissionManageGuild(Permission):

    name = 'MANAGE_GUILD'


class PermissionManageMessages(Permission):

    name = 'MANAGE_MESSAGES'


class PermissionNanageNicknames(Permission):

    name = 'MANAGE_NICKNAMES'


class PermissionManageRoles(Permission):

    name = 'MANAGE_ROLES'


class PermissionManageWebhooks(Permission):

    name = 'MANAGE_WEBHOOKS'


class PermissionMentionEveryone(Permission):

    name = 'MENTION_EVERYONE'


class PermissionMoveMembers(Permission):

    name = 'MOVE_MEMBERS'


class PermissionMuteMembers(Permission):

    name = 'MUTE_MEMBERS'


class PermissionReadMessageHistory(Permission):

    name = 'READ_MESSAGE_HISTORY'


class PermissionReadMessages(Permission):

    name = 'READ_MESSAGES'


class PermissionSendMessages(Permission):

    name = 'SEND_MESSAGES'


class PermissionSendTtsMessages(Permission):

    name = 'SEND_TTS_MESSAGES'


class PermissionSpeak(Permission):

    name = 'SPEAK'


class PermissionUseVoiceActivation(Permission):

    name = 'USE_VOICE_ACTIVATION'


class PermissionViewAuditLog(Permission):

    name = 'VIEW_AUDIT_LOG'