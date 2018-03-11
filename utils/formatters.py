async def format_response(response, message, bot):
    format_dict = {}

    if '{warning}' in response:
        format_dict['warning'] = '❗'
    if '{error}' in response:
        format_dict['error'] = '⛔'
    if '{guild}' in response and message.guild:
        format_dict['guild'] = message.guild.name
    if '{guild_id}' in response and message.guild:
        format_dict['guild_id'] = message.guild.id
    if '{channel}' in response:
        format_dict['channel'] = getattr(message.channel, 'name', 'DMchannel')
    if '{channel_id}' in response:
        format_dict['channel_id'] = message.channel.id
    if '{id}' in response: 
        format_dict['id'] = message.author.id
    if '{name}' in response:
        format_dict['name'] = message.author.name
    if '{nick}' in response:
        format_dict['nick'] = message.author.display_name
    if '{discrim}' in response:
        format_dict['discrim'] = message.author.discriminator
    if '{mention}' in response:
        format_dict['mention'] = message.author.mention

    return lazy_format(response, **format_dict)


def trim_message(text):
    MAX_LEN = 2000
    if len(text) > MAX_LEN:
        return text[:997] + '\n...\n' + text[-998:]

    return text


def lazy_format(s, *args, **kwargs):
  while True:
    try:
        return s.format(*args, **kwargs)
    except KeyError as e:
        key = e.args[0]
        kwargs[key] = "{%s}" % key
    except (ValueError, AttributeError):
        return s