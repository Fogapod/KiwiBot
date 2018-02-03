async def format_response(response, message, bot):
    format_dict = {}

    if '{warning}' in response:
        format_dict['warning'] = '❗'
    if '{error}' in response:
        format_dict['error'] = '⛔'
    if '{server}' in response:
        format_dict['server'] = message.guild.name
    if '{channel}' in response:
        format_dict['channel'] = message.channel.name
    if '{channel_name}' in response:
        format_dict['channel_name'] = message.channel.name
    if '{channel_id}' in response:
        format_dict['channel_id'] = message.author.id
    if '{id}' in response: 
        format_dict['id'] = message.author.id
    if '{name}' in response:
        format_dict['name'] = message.author.name
    if '{nick}' in response:
        format_dict['nick'] = message.author.display_name
    if '{discrim}' in response:
        format_dict['discrim'] = message.author.discriminator
    if '{mention}' in response:
        format_dict['mention'] = message.author.name + '#' + message.author.discriminator

    return lazy_format(response, **format_dict)


def lazy_format(s, *args, **kwargs):
  while True:
    try:
        return s.format(*args, **kwargs)
    except KeyError as e:
        key = e.args[0]
        kwargs[key] = "{%s}" % key
    except Exception:
        return s